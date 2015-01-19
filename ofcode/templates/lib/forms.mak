<%def name="errors(name)">\
% if name in c._form_errors:
<div class="error-message">${c._form_errors[name]|n}</div>\
% endif
</%def>

<%def name="form(name, url, multipart=False, **attrs)">
<%
    form = getattr(c, name)
    if not isinstance(form, dict):
        raise Exception("No form dictionary found at c.%s" % name)
    form_errors = c.form_errors.get(name, {})
    c._form, c._form_errors = form, form_errors
    
%>
${h.form(url, name=name, multipart=coerce_bool(multipart), **attrs)|n}\
${caller.body()}\
${h.end_form()|n}\
<%
    del c._form
    del c._form_errors
%></%def>

<%def name="text(name, **attrs)">\
${h.text(name, value=form_value(c, name), **attrs)|n}\
${errors(name)|n}\
</%def>

<%def name="upload(name, **attrs)">\
${h.file(name, **attrs)|n}\
${errors(name)|n}\
</%def>

<%def name="hidden(name, **attrs)">\
${h.hidden(name, value=form_value(c, name), **attrs)|n}\
</%def>

<%def name="password(name, **attrs)">\
${h.password(name, value=form_value(c, name), **attrs)|n}\
${errors(name)|n}\
</%def>

<%def name="textarea(name, **attrs)">\
<%
    error = name in c._form_errors
    if error and 'class' in attrs:
        attrs['class'] += ' error'
    elif error:
        attrs['class'] = 'error'
%>\
${errors(name)|n}\
${h.textarea(name, content=form_value(c, name), **attrs)|n}\
</%def>

<%def name="js_obfuscate(name, value)">
${h.js_obfuscate(value)|n}
${errors(name)|n}
</%def>

<%def name="select(name, options, **attrs)">\
<% 
    selected = request.POST.getall(name) or c._form.get(name, []) 
%>\
<select name=${name} ${display_attrs(attrs)|n}>
${''.join('<option value="%s"%s>%s</option>' % (t[0], ' selected="selected"' if t[0] in selected else '', t[1]) for t in options)|n}
</select>
${errors(name)|n}\
</%def>

<%def name="checkbox(name, value='true')">\
${h.checkbox(name, value, checked=form_value(c, name) == value)|n}\
${errors(name)|n}
</%def>

<%def name="radio(name, value)">\
${h.radio(name, value, checked=form_value(c, name) == value)}\
${errors(name)}
</%def>

<%def name="submit(**attrs)">\
<input type="submit" ${value if value else ''} ${display_attrs(attrs)|n}/>
</%def>

<%!
from webhelpers.html import literal
def coerce_bool(arg):
    if isinstance(arg, basestring):
        return eval(arg)
    elif isinstance(arg, bool):
        return arg
    else:
        raise ArgumentError("%r could not be coerced to boolean" % arg)

def form_value(c, name):
    try:
        return c._form.get(name)
    except AttributeError:
        raise Exception("Form tag used without a form context present; ensure that c.{form name} is populated with a dict, and that this tag is enclosed within the %form() tag from this library.")

def display_attrs(attrs):
    return ' '.join('%s="%s"' % (x,y) for x, y in attrs.iteritems())
%>
