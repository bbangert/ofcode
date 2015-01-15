from webhelpers.html import tags
from webhelpers.html.tags import form, select, textarea, submit, end_form
from webhelpers.html.tags import stylesheet_link, javascript_link
from webhelpers.html.tools import js_obfuscate
from ofcode.highlight import code_highlight, langdict

sorted_languages = sorted(langdict.items(),  key=lambda x: x[1])
