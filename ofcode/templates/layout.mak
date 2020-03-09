<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Paste ofCode</title>
    <!--[if IE]>
        <script src="${base_js_url}/html5.js"></script>
    <![endif]-->
    <link rel="icon" type="image/png" href="${base_static_url}/images/paste_favicon.png">
    <link href="${base_css_url}/print.4.css" media="print" rel="stylesheet" type="text/css" />
    ${self.styles()}
    <!--[if lt IE 8]>
        <link href="${base_css_url}/ie.4.css" media="screen, projection" rel="stylesheet" type="text/css" />
    <![endif]-->
</head>
<body id="${getattr(c, 'body_id','none')}" class="paste ${self.body_class()}">
    <div id="container">
        ${self.header()}
        ${next.body()}
        <div id="toggles">
            Toggle:
            <a id="toggle_theme" href="#">theme</a>,
            <a id="toggle_font" href="#">font</a>
        </div>
        <footer>
            <nav>
                <ul>
                ##     <li><a href="${url('ofcode_tmpl', request, action='about')}">About</a></li>
                ##    <li><a href="/api">API</a></li>
                ##     <li><a href="${url('ofcode_tmpl', request, action='contact')}">Contact</a></li>
                </ul>
            </nav>
            <div>&copy; 2020 ofCode.org</div>
        </footer>
    </div>
    ${self.javascript()}
</body>
</html>
<%def name="body_class()">${session.get('style', 'dark')} font_${c.font_choice}</%def>
<%def name="header()">
    <header>
       <hgroup>
           <a href="${request.application_url}"><h1>Paste<br /><span>Of Code</span></h1></a>
       </hgroup>
    </header>
</%def>
##
<%def name="styles()">
    <%
        #Only read from file in dev
        if not c.use_minified_assets:
            with open(static_path + '/stylesheets/CSSLIST','r') as f:
                stylesheets = f.read()
            f.close()
            stylesheet_files = ['/static/stylesheets/%s.css' % f for f in stylesheets.split()]
    %>
    % if c.use_minified_assets:
        ${h.stylesheet_link('https://assets1.ofcode.org/stylesheets/%s' % request.registry.settings['ofcode.minified_css'])}
    % else:
        ${ h.stylesheet_link(*stylesheet_files) }
    %endif

    % if c.font_choice == 'anonymous':
        <link href="${base_css_url}/anon_font.css" media="screen, projection, print" rel="stylesheet" type="text/css" />
    % else:
        <link href="${base_css_url}/bitstream_mono.css" media="screen, projection, print" rel="stylesheet" type="text/css" />
    % endif
</%def>
##
<%def name="javascript()">
    <script>
        var OFCODE = OFCODE || {};
        OFCODE.base_js = '${base_js_url}';
    </script>
    <%
        #Only read from file in dev
        if not c.use_minified_assets:
            with open(static_path + '/javascripts/JSLIST','r') as f:
                javascripts = f.read()
            javascripts = [x.strip() for x in javascripts.split('\n') if x.strip()]
            javascript_files = ['/static/javascripts/%s.js' % f for f in javascripts]
    %>
    % if c.use_minified_assets:
        ${ h.javascript_link('https://assets1.ofcode.org/javascripts/%s' % request.registry.settings['ofcode.minified_js'])}
    % else:
        ${ h.javascript_link(*javascript_files) }
    % endif
</%def>
##
<%!
from time import time
now = time()
%>
