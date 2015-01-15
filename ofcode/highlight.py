from pygments import highlight
from pygments.formatter import Formatter
from pygments.formatters.html import _get_ttype_class
from pygments.formatters.html import escape_html
from pygments.lexers import get_lexer_by_name, get_all_lexers

import StringIO

__all__ = ['code_highlight']

langdict = {}
formatter = None
for lang in get_all_lexers():
    langdict[lang[1][0]] = lang[0]


def code_highlight(source, language, truncate_lines=None):
    create_formatter()
    if truncate_lines:
        split_source = source.split('\n')
        if len(split_source) > truncate_lines:
            source = split_source[:truncate_lines - 1]
            source.append('...')
            source = ''.join(source)
    lexer = get_lexer_by_name(language, stripall=True)
    return highlight(source, lexer, formatter).decode('utf-8')


def create_formatter():
    global formatter
    if formatter:
        return

    class CodeViewFormat(Formatter):
        def __init__(self, **options):
            Formatter.__init__(self, **options)
            self.lineseparator = options.get('lineseparator', '\n')
            self.classprefix = options.get('classprefix', '')
            self._class_cache = {}

        def _get_css_class(self, ttype):
            return self.classprefix + _get_ttype_class(ttype)

        def _wrap_sidebar(self, lines):
            dummyoutfile = StringIO.StringIO()
            lncount = 0
            for t, line in lines:
                if t:
                    lncount += 1
                dummyoutfile.write(line)

            yield 1, '<div id="lcb">'
            for i in range(lncount):
                yield 1, ('<div class="l%s"><pre> </pre></div>' % (i % 2))
            yield 1, '</div>'

            yield 0, dummyoutfile.getvalue()

        def _format_lines(self, tokensource):
            yield 0, '<div id="rcb"><pre>\n'

            lsep = self.lineseparator

            lspan = ''
            line = ''
            for ttype, value in tokensource:
                cls = self._get_css_class(ttype)
                cspan = cls and '<span class="%s">' % cls or ''

                parts = escape_html(value).split('\n')

                # for all but the last line
                for part in parts[:-1]:
                    if line:
                        if lspan != cspan:
                            line += (lspan and '</span>') + cspan + part + \
                                    (cspan and '</span>') + lsep
                        else:  # both are the same
                            line += part + (lspan and '</span>') + lsep
                        yield 1, line
                        line = ''
                    elif part:
                        yield 1, cspan + part + (cspan and '</span>') + lsep
                    else:
                        yield 1, lsep
                # for the last line
                if line and parts[-1]:
                    if lspan != cspan:
                        line += (lspan and '</span>') + cspan + parts[-1]
                        lspan = cspan
                    else:
                        line += parts[-1]
                elif parts[-1]:
                    line = cspan + parts[-1]
                    lspan = cspan

            yield 0, '</pre></div>'

        def format_unencoded(self, tokensource, outfile):

            outfile.write('<div id="codeview"><div>')

            source = self._format_lines(tokensource)
            source = self._wrap_sidebar(source)

            for ttype, value in source:
                outfile.write(value)

            outfile.write('</div></div>')

    # Use this formatter within the app
    formatter = CodeViewFormat(linenos=True, cssclass="syntax", encoding='utf-8')
