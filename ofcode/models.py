import re
import time
import uuid
import threading

from pyramid.security import Everyone
from pyramid.security import Allow
from redis import Redis
from redis.connection import ConnectionError

from ofcode.baseconvert import base_encode
from ofcode.highlight import code_highlight

HTML_VERSION = '0.2'
VALID_KEY = re.compile(r'^\w+$')


def redis_connect():
    settings = Paste.settings
    with Paste.clock:
        if Paste.redis:
            return
        else:
            Paste.redis = Redis(
                host=settings.get('redis.host', 'localhost'),
                port=int(settings.get('redis.port', 6379)),
                db=int(settings.get('redis.db', 1)),
            )


def redis_reconnect(func):
    def wrapper(*args, **kwargs):
        tries = 0
        if not Paste.redis:
            redis_connect()
        while tries < 3:
            try:
                return func(*args, **kwargs)
            except ConnectionError:
                Paste.redis = None
                redis_connect()
                tries += 1
        return func(*args, **kwargs)
    wrapper.__name__ == func.__name__
    return wrapper


class Paste(object):
    __parent__ = 'Root'
    redis = None
    settings = None
    clock = threading.Lock()

    def __init__(self, key, html=None, session_id=None, version=None,
                 code=None, language=None):
        self.key = key
        self.html = html
        self.session_id = session_id
        self.version = version
        self.language = language
        self.code = code

        if version != HTML_VERSION:
            self.update()

    @redis_reconnect
    def update(self):
        self.language, self.code = self.redis.hmget(
            self.key, ['language', 'code'])
        self.html = code_highlight(self.code, self.language)
        self.version = HTML_VERSION
        self.redis.hmset(self.key,
            {'html': self.html, 'version': self.version})

    @redis_reconnect
    def delete(self):
        self.redis.delete(self.key)
        return True

    @classmethod
    @redis_reconnect
    def create(cls, code=None, language=None, session_id=None):
        html = code_highlight(code, language)
        key = base_encode(uuid.uuid4().int)
        version = HTML_VERSION
        created = time.time()
        cls.redis.hmset(key,
                        dict(code=code, html=html, language=language,
                             session_id=session_id, version=version,
                             created=str(created)))
        cls.redis.expire(key, 60 * 60 * 24 * 7)
        return key

    def is_owner(self, session):
        session_id = session.get('id', None)
        if session_id and session_id == self.session_id:
            return True
        else:
            return False

    @classmethod
    @redis_reconnect
    def fetch_by_key(cls, key):
        """Fetch and return a Paste instance by key for viewing"""
        session_id, html, version, code, language = cls.redis.hmget(
            key, ['session_id', 'html', 'version', 'code', 'language'])
        if not session_id:
            return None
        else:
            return cls(key=key, html=html, session_id=session_id,
                       version=version, code=code, language=language)


class Root(object):
    __acl__ = [
        (Allow, Everyone, 'create')
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        if not VALID_KEY.match(key):
            raise KeyError("Invalid key")

        paste = Paste.fetch_by_key(key)
        if not paste:
            raise KeyError("No paste of that id found.")

        paste.__acl__ = [
            (Allow, Everyone, 'view'),
            (Allow, 'sessionid:%s' % paste.session_id, 'delete'),
        ]
        return paste
