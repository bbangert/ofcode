import os

from pyramid.threadlocal import get_current_request
from pyramid.exceptions import ConfigurationError

from ofcode import helpers


def add_renderer_globals(event):
    """ A subscriber to the ``pyramid.events.BeforeRender`` events.  Updates
    the :term:`renderer globals` with values that are familiar to Pylons
    users."""
    request = event.get('request')
    if request is None:
        request = get_current_request()
    globs = {
        'h': helpers,
        }
    if request is not None:
        tmpl_context = request.tmpl_context
        val = request.registry.settings.get('use_minified_assets')
        if val == 'false':
            val = False
        else:
            val = bool(val)
        tmpl_context.use_minified_assets = val
        globs["base_static_url"] = 'https://assets1.ofcode.org'
        if val:
            globs['base_js_url'] = 'https://assets1.ofcode.org/javascripts'
            globs['base_css_url'] = 'https://assets1.ofcode.org/stylesheets'
        else:
            globs['base_js_url'] = '/static/javascripts'
            globs['base_css_url'] = '/static/stylesheets'

        globs['c'] = tmpl_context
        globs['tmpl_context'] = tmpl_context
        try:
            globs['session'] = request.session
        except ConfigurationError:
            pass
        globs['static_path'] = os.path.join(
                os.path.dirname(__file__), 'static')
    event.update(globs)


def setup_tmpl_context(event):
    req = event.request
    req.tmpl_context.font_choice = req.session.get('font', 'dejavu')
    req.tmpl_context.form_errors = {}
    if 'Development' in req.environ.get('SERVER_SOFTWARE', []):
        req.tmpl_context.debug = True
    else:
        req.tmpl_context.debug = False
