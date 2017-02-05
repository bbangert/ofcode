import uuid

from pyramid.httpexceptions import HTTPFound

from ofcode.decorators import validate
from ofcode.formschemas import NewPaste
from ofcode.models import Paste


def index(req):
    req.tmpl_context.body_id = 'paste_create'
    req.tmpl_context.new_paste = dict(language='python')
    return {}


def api(req):
    return {}


@validate(name='new_paste', on_error=index, schema=NewPaste())
def create(req):
    if 'id' not in req.session:
        req.session['id'] = str(uuid.uuid4())
    key = Paste.create(session_id=req.session['id'], **req.form_result)
    req.session.changed()
    return HTTPFound(location=('%s' % key))


def show(context, req):
    req.tmpl_context.body_id = 'paste_view'
    return {'paste': context}


def show_json(context, req):
    return {'language': context.language,
            'code': context.code}


def delete(req):
    paste = req.context
    paste.delete()
    return {}


def theme_toggle(req):
    """Toggle the theme chosen, or set it specifically if theme GET
    param is present"""
    theme = req.GET.get('style', 'light')
    if not theme or theme not in ['dark', 'light']:
        theme = req.session.get('style')
        if theme and theme == 'light':
            theme = 'dark'
        else:
            theme = 'light'
    req.session['style'] = theme
    req.session.changed()
    return {}


def font_toggle(req):
    """Toggle the font chosen, or set it specifically if font GET
    param is present"""
    font = req.GET.get('font')
    if not font or font not in ['dejavu', 'anonymous']:
        font = req.session.get('font')
        if font and font == 'anonymous':
            font = 'dejavu'
        else:
            font = 'anonymous'
    req.session['font'] = font
    req.session.changed()
    return {}
