try:
    import gevent
    wc = "gevent"
except ImportError:
    wc = "sync"

bind = "127.0.0.1:5040"
workers = 1
worker_class = wc
timeout = 3
proc_name = "ofcode"
pidfile = "ofcode.pid"
limit_request_line = 1024
limit_request_fields = 20
limit_request_field_size = 1024

backlog = 10
