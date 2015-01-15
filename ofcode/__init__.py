from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig


def main(global_config, **settings):
    from ofcode.models import Paste
    from ofcode.models import Root
    from ofcode.models import redis_connect
    from ofcode.security import OfcodeAuthenticationPolicy
    authentication_policy = OfcodeAuthenticationPolicy()
    authorization_policy = ACLAuthorizationPolicy()

    session_factory = UnencryptedCookieSessionFactoryConfig(
        secret="enrN7Khdk7BaZF",
        cookie_name="ofcode",
        cookie_max_age=5 * 365 * 24 * 60 * 60,
    )
    Paste.settings = settings
    Paste.redis = redis_connect()
    config = Configurator(root_factory=Root,
                          settings=settings,
                          session_factory=session_factory,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy
                          )
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
