"""
Critic Markup
=============

This extension adds support for `Critic Markup<http://criticmarkup.com>`_.

Syntax for Critic Markup:

*  {++addition++}
*  {--deletion--}
*  {~~replace~>with~~}
*  {>>comment<<}
*  {==highlight==}{>>comment<<}

Copyright 2014 [Alex Popescu](http://mypopescu.com).

License: BSD (see ../docs/LICENSE for details).

Implementation inspired by `critic.py<https://github.com/CriticMarkup/CriticMarkup-toolkit/blob/master/Marked%20Processor/critic.py>`_.

"""

from __future__ import absolute_import
from . import Extension
from ..preprocessors import Preprocessor

import os
import re



ADDITION_RE = re.compile(r'''{\+\+(?P<value>.*?)\+\+}''', re.DOTALL)
DELETION_RE = re.compile(r'''{--(?P<value>.*?)--}''', re.DOTALL)
SUBSTITUTION_RE = re.compile(r'''{~~(?P<original>(?:[^~>]|(?:~(?!>)))+)~>(?P<new>(?:[^~~]|(?:~(?!~})))+)~~}''', re.DOTALL)
COMMENT_RE = re.compile(r'''{>>(?P<value>.*?)<<}''', re.DOTALL)
HIGHLIGHT_RE = re.compile(r'''{==(?P<value>.*?)==\}''', re.DOTALL)



def makeExtension(configs=[]):
    """ Return an instance of the ExtraInlineExtension """
    return CriticMarkupExtension(configs=configs)


class CriticMarkupExtension(Extension):
    """The :class:`extensions.CriticMarkupExtension` provides conversion
    of additional inline formatting for `Critic Markup<http://criticmarkup.com>`_.
    """
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('criticmarkup_add', Addition(), '_end')
        md.preprocessors.add('criticmarkup_del', Deletion(), '_end')
        md.preprocessors.add('criticmarkup_sub', Substitution(), '_end')
        md.preprocessors.add('criticmarkup_highlight', Highlighter(), '_end')
        md.preprocessors.add('criticmarkup_comment', Comment(), '_end')

class Addition(Preprocessor):
    """ Convert CriticMarkup {++adition++} to <INS>"""

    def run(self, lines):
        text = os.linesep.join(lines)
        return ADDITION_RE.sub(self._sub, text).splitlines(False)

    def _sub(self, matchobj):
        value = matchobj.group('value')
        if value.startswith('\n\n') and value != "\n\n":
            replaceString = "\n\n<ins class='critic' break>&nbsp;</ins>\n\n"
            replaceString += '<ins>' + value.replace("\n", " ")
            replaceString += '</ins>'
        # Is the addition just a single new paragraph
        elif value == "\n\n":
            replaceString = "\n\n<ins class='critic break'>&nbsp;" + '</ins>\n\n'
        # Is it added text followed by a new paragraph?
        elif value.endswith('\n\n') and value != "\n\n":
            replaceString = '<ins>' + value.replace("\n", " ") + '</ins>'
            replaceString += "\n\n<ins class='critic break'>&nbsp;</ins>\n\n"
        else:
            replaceString = '<ins>' + value.replace("\n", " ") + '</ins>'

        return replaceString

class Deletion(Preprocessor):
    def run(self, lines):
        return DELETION_RE.sub(self._sub, os.linesep.join(lines)).splitlines(False)

    def _sub(self, matchobj):
        val = matchobj.group('value')
        if val == '\n\n':
            return '<del>&nbsp;</del>'
        return '<del>' + val.replace('\n\n', '&nbsp') + '</del>'

class Highlighter(Preprocessor):
    def run(self, lines):
        return HIGHLIGHT_RE.sub(self._sub, os.linesep.join(lines)).splitlines(False)

    def _sub(self, matchobject):
        return u'<mark>' + matchobject.group('value') + u'</mark>'

class Comment(Preprocessor):
    def run(self, lines):
        return COMMENT_RE.sub(self._sub, os.linesep.join(lines)).splitlines(False)

    def _sub(self, matchobj):
        return u'<span class="critic comment">' + matchobj.group('value') + u'</span>'

class Substitution(Preprocessor):
    def run(self, lines):
        return SUBSTITUTION_RE.sub(self._sub, os.linesep.join(lines)).splitlines(False)

    def _sub(self, matchobj):
        return u'<del>' + matchobj.group('original') + u'</del><ins>' + matchobj.group('new') + u'</ins>'