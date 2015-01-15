"""ofcode decorators"""
import formencode
import simplejson
from decorator import decorator
from webob import Response


def _valid_schema(input_params, schema):
    """Takes a FormEncode schema, returns a tuple of the
    parsed values and errors"""
    params, errors = {}, {}
    try:
        params = schema.to_python(input_params)
    except formencode.Invalid, e:
        errors = e.unpack_errors()
    return params, errors


def validate(name, on_error=None, schema=None):
    """Validate a schema, call the on_error method if
    its invalid, otherwise set some defaults

    """
    @decorator
    def valid_func(func, req):
        req.form_result, req.tmpl_context.form_errors[name] = _valid_schema(req.POST, schema)
        if req.tmpl_context.form_errors.get(name):
            method = on_error
            return method(req)
        else:
            if 'notabot' in req.form_result:
                del req.form_result['notabot']
            return func(req)
    return valid_func


def api(schema):
    """Validates incoming body content of JSON against a FormEncode
    Schema for validation, and returns the body result as JSON"""
    def func_wrapper(func):
        def api_call(self, *args, **kwargs):
            req = self.request
            resp = Response()
            resp.headers['Content-Type'] = 'application/json'
            dct = {}

            if schema:
                try:
                    msg_body = simplejson.loads(req.body)
                except ValueError:
                    dct['status'] = 'failure'
                    dct['reason'] = 'Invalid JSON body'
                else:
                    # We have valid JSON upload, check the schema
                    parsed_json, errors = _valid_schema(msg_body, schema)
                    if errors:
                        first_key = errors.keys()[0]
                        dct['reason'] = '%s: %s' % (first_key, errors[first_key])
                        dct['status'] = 'failure'
                    else:
                        # We change the key values to strings here cause we can't pass
                        # unicode keys as keyword arguments
                        json = {}
                        for k, v in parsed_json.items():
                            json[str(k)] = v
                        self.json = json

            # If our dct is empty, no errors, call the func
            if not dct:
                dct.update(func(self, *args, **kwargs))

            resp.body = simplejson.dumps(dct)
            return resp
        return api_call
    return func_wrapper
