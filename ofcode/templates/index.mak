<div id="editor"></div>

<%form:form name="new_paste" url="/">
    <%form:textarea name="code"/>
    <div class="language">
        <label for="language">Language:</label>
        <%form:select id="language" name="language", options="${h.sorted_languages}"/>
    </div>
    
    <%form:js_obfuscate name="notabot" value='<input type="hidden" name="notabot" value="most_likely" />'/>

    <div class="submit">
        <%form:submit value="Paste it! &nbsp;&nbsp;&nbsp; &#8997;Enter"/>
    </div>
</%form:form>
<p class="note">Your code is <b>always private, and always expires in one week</b>. Only those that you
    provide with the URL will be able to access your pasted code within this period. A cookie will be
    left so that you can <b>delete this pasted code at anytime</b> earlier if desired.</p>
<%namespace name="form" file="/lib/forms.mak"/>
<%inherit file="/layout.mak"/>