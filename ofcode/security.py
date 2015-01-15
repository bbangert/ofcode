import logging

from pyramid.security import Everyone


class OfcodeAuthenticationPolicy(object):
    def authenticated_userid(self, request):
        return None

    def effective_principals(self, request):
        effective_principals = [Everyone]
        if 'id' in request.session:
            effective_principals.append('sessionid:%s' % request.session['id'])
        logging.info("Effective principals: %s", effective_principals)
        return effective_principals
