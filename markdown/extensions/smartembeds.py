"""
Smart Embeds Extension for Python-Markdown
==========================================

This extension adds support for automatically embedding external resources.

Supported embeds:

- slideshare:
- speakerdeck:
- youtube:
- pdf:
- vimeo:


Basic Usage:

    >>> import markdown
    >>> text = '''
    ...
    ... @slideshare:[Food Blog Design](http://www.slideshare.net/tammyhart/food-blog-design "{{width=425 height=355 id=11312368}}")
    ...
    ... '''
    >>> md = markdown.Markdown(['smartembeds'])
    >>> print md.convert(text)
    <p><div class="embedded smartembed slideshare" style="width:425px" id="__ss_11312368">
    <iframe class="smartembed slideshare" src="http://www.slideshare.net/slideshow/embed_code/11312368?rel=0" width="425" height="355" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>
    <div class="smartembed-ref-slideshare"><a href="http://www.slideshare.net/tammyhart/food-blog-design" rel="nofollow external" target="_blank">Food Blog Design</a></div>
    </div></p>
    >>> text = '''
    ...
    ... @pdf:[An Introduction to R](http://cran.r-project.org/doc/manuals/R-intro.pdf "{{width=560 height=720}}")
    ...
    ... '''
    >>> md = markdown.Markdown(['smartembeds'])
    >>> print md.convert(text)
    <p><div class='embedded smartembed pdf'>
    <iframe src="http://docs.google.com/gview?embedded=true&url=http://cran.r-project.org/doc/manuals/R-intro.pdf&" width="560" height="720" frameborder="0" marginwidth="0" marginheight="0"></iframe>
    <div class="smartembed-ref-pdf"><a href="http://cran.r-project.org/doc/manuals/R-intro.pdf" rel="nofollow external" target="_blank">Download PDF</a></div>
    </div></p>
    >>>
    >>> text = '''
    ...
    ... @vimeo:[The Invastion end credit sequence](http://vimeo.com/35782590 "{{width=480 height=400}}")
    ...
    ... '''
    >>> md = markdown.Markdown(['smartembeds'])
    >>> print md.convert(text)
    <p><div class='embedded smartembed vimeo'>
    <iframe src="http://player.vimeo.com/video/35782590?title=0&amp;byline=0&amp;portrait=0" width="480" height="400" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>
    <div class="smartembed-ref-vimeo"><a href="http://vimeo.com/35782590" rel="nofollow external" target="_blank">The Invastion end credit sequence</a></div>
    </div></p>
    >>>
    >>> text = '''
    ...
    ... @youtube:[Markel Brown Ejected on Dunk of the Year](http://www.youtube.com/watch?v=0h4u7wGM630&feature=g-logo&context=G21d68b3FOAAAAAAAFAA "{{width=480 height=400}}")
    ...
    ... '''
    >>> md = markdown.Markdown(['smartembeds'])
    >>> print md.convert(text)
    <p><div class='embedded smartembed youtube'>
    <iframe class="youtube-player" type="text/html" width="480" height="400" src="http://www.youtube.com/embed/0h4u7wGM630" frameborder="0"></iframe>
    </div></p>
    >>>
    >>> text = '''
    ...
    ... @speakerdeck:[Eric Brewer: Advancing Distributed Systems](https://speakerdeck.com/eric_brewer/ricon-2012-keynote "{{id=507d8d38f360eb000205d64c}}")
    ...
    ... '''
    >>> md = markdown.Markdown(['smartembeds'])
    >>> print md.convert(text)
    <p><div class="embedded smartembed speakerdeck">
    <script src="http://speakerdeck.com/embed/507d8d38f360eb000205d64c.js"></script>
    <div class="smartembed-ref-speakerdeck"><a href="https://speakerdeck.com/eric_brewer/ricon-2012-keynote" rel="nofollow external" target="_blank">Eric Brewer: Advancing Distributed Systems</a></div>
    </div></p>

Copyright 2012 [Alex Popescu](http://mypopescu.com).

License: BSD (see ../docs/LICENSE for details)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from . import Extension
from ..preprocessors import Preprocessor

import re

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs


_KNOWN_PROTOCOLS = ('slideshare', 'pdf', 'youtube', 'vimeo', 'speakerdeck')


class SmartEmbedsExtension(Extension):
    """ Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add MetaPreprocessor to Markdown instance. """

        md.preprocessors.add("smartembeds", SmartEmbedsPreprocessor(md), "_end")

# regexps for smart embeds
_NOBRACKET = r'[^\[\]]*'
_BRK = r'\[(' + _NOBRACKET + r')\]'
_NOIMG = r'(?<!\!)'
_LINK_RE = _NOIMG + _BRK + r'''\(<?(.*?)>?\s*((['"])(.*?)\5)?\)''' # note the \5: even if the (['"]) is the 4th
_SMARTEMBED_RE = r'\s*@([^:]+):' + _LINK_RE
_reSMARTEMBED = re.compile(_SMARTEMBED_RE)

# regexps for attributes
reATTRIBUTE_TITLE = re.compile("(\{\{(.+)\}\})")
reATTR = re.compile("(#[a-zA-Z0-9_-]+|[a-zA-Z0-9_-]+='[^']+'|[a-zA-Z0-9_-]+=\S+|[a-zA-Z0-9_-]+)")

_PDF_EMBED_TEMPLATE = """<div class='embedded smartembed pdf'>
<iframe src="http://docs.google.com/gview?embedded=true&url=%(url)s&" width="%(width)s" height="%(height)s" frameborder="0" marginwidth="0" marginheight="0"></iframe>
<div class="smartembed-ref-pdf"><a href="%(url)s" rel="nofollow external" target="_blank">Download PDF</a></div>
</div>
"""

_SLIDESHARE_EMBED_TEMPLATE = """<div class="embedded smartembed slideshare" style="width:%(width)spx" id="%(sid)s">
<iframe class="smartembed slideshare" src="http://www.slideshare.net/slideshow/embed_code/%(id)s?rel=0" width="%(width)s" height="%(height)s" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>
<div class="smartembed-ref-slideshare"><a href="%(url)s" rel="nofollow external" target="_blank">%(title)s</a></div>
</div>
"""

_SLIDESHARE_EMBED_NOID_TEMPLATE = """<a href="%(url)s" rel="nofollow external" target="_blank">%(title)s</a>"""

_SPEAKERDECK_EMBED_TEMPLATE = """<div class="embedded smartembed speakerdeck">
<script src="http://speakerdeck.com/embed/%(id)s.js"></script>
<div class="smartembed-ref-speakerdeck"><a href="%(url)s" rel="nofollow external" target="_blank">%(title)s</a></div>
</div>
"""

_SPEAKERDECK_EMBED_NOID_TEMPLATE = """<a href="%(url)s" rel="nofollow external" target="_blank">%(title)s</a>"""

_VIMEO_EMBED_TEMPLATE = """<div class="embedded smartembed vimeo">
<iframe src="http://player.vimeo.com/video/%(id)s?title=0&amp;byline=0&amp;portrait=0" width="%(width)s" height="%(height)s" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>
<div class="smartembed-ref-vimeo"><a href="%(url)s" rel="nofollow external" target="_blank">%(title)s</a></div>
</div>
"""

_YOUTUBE_EMBED_TEMPLATE = """<div class="embedded smartembed youtube">
<iframe class="youtube-player" type="text/html" width="%(width)s" height="%(height)s" src="http://www.youtube.com/embed/%(id)s" frameborder="0"></iframe>
</div>
"""

_TEMPLATES = {
    'pdf': _PDF_EMBED_TEMPLATE,
    'slideshare': _SLIDESHARE_EMBED_TEMPLATE,
    'slideshare_noid': _SLIDESHARE_EMBED_NOID_TEMPLATE,
    'speakerdeck': _SPEAKERDECK_EMBED_TEMPLATE,
    'speakerdeck_noid': _SPEAKERDECK_EMBED_NOID_TEMPLATE,
    'vimeo': _VIMEO_EMBED_TEMPLATE,
    'youtube': _YOUTUBE_EMBED_TEMPLATE,
}

_DEFAULT_PARAMS = {
    'pdf': {'width': '520', 'height': '675'},
    'slideshare': {'id': '', 'sid': '', 'width': '520', 'height': '435'},
    'speakerdeck': {'id': ''},
    'vimeo': {'width': '520', 'height': '390'},
    'youtube': {'width': '520', 'height': '390'}
}


class SmartEmbedsPreprocessor(Preprocessor):
    """ Get Meta-Data. """

    def run(self, lines):
        """ Replace any of the smart embeds with their corresponding inlined HTML"""
        flines = []
        for l in lines:
            if l and l.lstrip()[0] == '@':
                m = _reSMARTEMBED.match(l)
                if m:
                    embed_protocol = m.group(1)
                    if embed_protocol in _KNOWN_PROTOCOLS:
                        flines.append(self._process(l, embed_protocol, m))
                    else:
                        flines.append(l)
                else:
                    flines.append(l)
            else:
                flines.append(l)
        return flines

    def _process(self, line, embed_protocol, m):
        title, url, attrs = self._extract(m)
        params = {'title': title, 'url': url}
        params.update(_DEFAULT_PARAMS.get(embed_protocol, {}))
        params.update(self._attributes(attrs))
        if 'vimeo' == embed_protocol:
            params.update(self._vimeo(url, params))
        elif 'youtube' == embed_protocol:
            params.update(self._youtube(url, params))
        elif 'slideshare' == embed_protocol:
            params.update(self._slideshare(url, params))
            if 'id' not in params or not params['id']:
                embed_protocol = 'slideshare_noid'
        elif 'speakerdeck' == embed_protocol:
            if 'id' not in params or not params['id']:
                embed_protocol = 'speakerdeck_noid'

        return _TEMPLATES.get(embed_protocol, "") % params


    def _slideshare(self, url, params):
        extra_params = {}
        id = params.get('id')
        sid = params.get('sid')
        if id:
            if not sid:
                if id.startswith('__ss_'):
                    extra_params['sid'] = id
                    extra_params['id'] = id[5:]
                else:
                    extra_params['sid'] = "__ss_%s" % id
        elif sid:
            if not id:
                if sid.startswith('__ss_'):
                    extra_params['id'] = sid[5:]
                else:
                    extra_params['id'] = sid
                    extra_params['sid'] = "__ss_%s" % sid
        return extra_params

    def _youtube(self, url, params):
        query_idx = url.find('?')
        if query_idx == -1:
            vid_id = ''
        else:
            url_params = parse_qs(url[query_idx + 1:], keep_blank_values=1)
            vid_id = url_params.get('v', [''])[0]
        return {'id': vid_id}

    def _vimeo(self, url, params):
        url_parts = url.split('/')
        query_idx = url_parts[-1].find('?')
        if query_idx > -1:
            vid_id = url_parts[-1][:query_idx]
        else:
            vid_id = url_parts[-1]
        return {'id': vid_id}

    def _extract(self, m):
        return m.group(2), m.group(3), m.group(6)

    def _attributes(self, attributes):
        if not attributes:
            return {}
        matchobj = reATTRIBUTE_TITLE.search(attributes)
        if not matchobj:
            return {}
            # we have attributes
        attr_str = matchobj.group(2)
        attrs = {}
        matches = reATTR.findall(attr_str)
        for m in matches:
            attr_val = m
            if attr_val.startswith('#'):
                attrs['id'] = attr_val[1:]
                continue
            val_sep_idx = attr_val.find('=')
            if val_sep_idx > -1:
                attr_name = attr_val[:val_sep_idx]
                if attr_val[val_sep_idx + 1] == "'":
                    attrs[attr_name] = attr_val[val_sep_idx + 2:-1]
                else:
                    attrs[attr_name] = attr_val[val_sep_idx + 1:]
            else:
                values = attrs.get('class', [])
                values.append(attr_val)
                attrs['class'] = values
        if attrs.has_key('class'):
            attrs['class'] = ' '.join(attrs['class'])
        return attrs


def makeExtension(configs={}):
    return SmartEmbedsExtension(configs=configs)


if __name__ == "__main__":
    import doctest

    doctest.testmod()