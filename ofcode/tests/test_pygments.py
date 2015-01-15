from nose.tools import eq_

from ofcode.highlight import code_highlight


class TestPygments(object):
    def test_hightlight_function(self):
        formatted = code_highlight('print "hiyas"\nprint "joe"', 'python', 1)
        eq_(formatted,  u'<div id="codeview"><div><div id="lcb"><div class="l0"><pre> </pre></div></div><div id="rcb"><pre>\n<span class="o">...</span>\n</pre></div></div></div>')
