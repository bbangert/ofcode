<hr/>
<div class="syntax">
    <div id="paste-buttons">
        % if paste.is_owner(session):
        <img id="delete-paste" src="/static/images/cancel.png" title="Delete this paste" />
        % endif
        <img id="fork-paste" src="/static/images/edit.png" title="Start a new paste with this content" />
    </div>
${paste.html.decode('utf-8') |n}
</div>
<hr/>
<%inherit file="layout.mak"/>
