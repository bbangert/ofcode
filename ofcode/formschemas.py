from formencode import schema
from formencode.validators import (
    OneOf,
    UnicodeString,
)

from pygments.lexers import get_all_lexers

languagelist = [lang[1][0] for lang in get_all_lexers()]


class myschema(schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True


class NewPaste(myschema):
    notabot = OneOf([u'most_likely'], hideList=True, not_empty=True)
    language = OneOf(languagelist, hideList=True, not_empty=True)
    code = UnicodeString(not_empty=True)


class NewPasteAPI(myschema):
    language = OneOf(languagelist + ['guess'], hideList=True)
    code = UnicodeString(not_empty=True)
