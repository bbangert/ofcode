import os
import uuid

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

def main(global_config, **settings):
    from ofcode.models import Paste
    from ofcode.models import Root
    from ofcode.models import redis_connect
    from ofcode.security import OfcodeAuthenticationPolicy
    authentication_policy = OfcodeAuthenticationPolicy()
    authorization_policy = ACLAuthorizationPolicy()

    if "COOKIE_SECRET" in os.environ:
        cookie_secret = os.environ["COOKIE_SECRET"]
    else:
        cookie_secret = str(uuid.uuid4())

    session_factory = SignedCookieSessionFactory(
        secret=cookie_secret,
        max_age=5 * 365 * 24 * 60 * 60,
        timeout=None
    )

    # Pull out env vars if present
    if "REDIS_HOST" in os.environ:
        settings["redis.host"] = os.environ["REDIS_HOST"]
    if "REDIS_PORT" in os.environ:
        settings["redis.port"] = os.environ["REDIS_PORT"]
    if "REDIS_DB" in os.environ:
        settings["redis.db"] = os.environ["REDIS_DB"]

    Paste.settings = settings
    Paste.redis = redis_connect()
    config = Configurator(root_factory=Root,
                          settings=settings,
                          session_factory=session_factory,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy
                          )
    config.include('pyramid_mako')
    config.add_subscriber('ofcode.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('ofcode.subscribers.setup_tmpl_context',
                          'pyramid.events.NewRequest')

    config.add_static_view('static', 'static', cache_max_age=3600)

    # View create form
    config.add_view('.views.index', context='.models.Root',
                    request_method='GET', renderer='/index.mak')

    # Create a paste
    config.add_view('.views.create', context='.models.Root',
                    request_method='POST', renderer='/index.mak',
                    permission='create')

    # View a paste
    config.add_view('.views.show', context='.models.Paste',
                    renderer='/view.mak', permission='view')
    config.add_view('.views.show_json', name='json', context='.models.Paste',
                    renderer='json', permission='view')

    # Delete a paste
    config.add_view('.views.delete', name='delete', context='.models.Paste',
                    renderer='json', permission='delete')

    # Paste API
    # config.add_view('.views.api', name='api', context='.models.Root',
    #                 renderer='/api.mak')

    # Toggles
    config.add_view('.views.theme_toggle', name='theme_toggle',
                    context='.models.Root', renderer='json')
    config.add_view('.views.font_toggle', name='font_toggle',
                    context='.models.Root', renderer='json')
    return config.make_wsgi_app()


zappa = main({}, **{
    "pyramid.debug_authorization": True,
    "mako.directories": "ofcode:templates",
    "ofcode.minified_js": "ofcode-03222012.2-min.js",
    "ofcode.minified_css": "ofcode-012917.1-min.css",
    "use_minified_assets": True
})
