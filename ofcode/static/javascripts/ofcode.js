var OFCODE = OFCODE || {};

/**
 * Shader is a component for the Codeview which'll enable shading of lines of
 * code.
 *
 * @param outterdiv - the div which'll represent the codeview
 */
OFCODE.Shader = (function() {
    /* private member stuff */
    
    /**
     * create a div to use as the overlay for shadowing in lines
     */
    function add_overlay(outterdiv) {
        var armed = false;
        var armed_shade_on = false;
        
        outterdiv.append('<div id="codeview_overlay"></div>');
        var overlay = $('#codeview_overlay');
        
        overlay.css({
            'z-index':'5',
            'position':'absolute',
            'top':'0px',
            'left':'0px',
            'width':outterdiv.css('width'),
            'height':outterdiv.css('height'),
            'display': 'none'
        });
        
        var couples = [];
        
        $('#lcb > div').each(function(idx) {
            var i = idx + 1;
            overlay.append('<div id="shade'+i+'"></div>');
            var elf = $('#shade'+i);
            var elb = $(this);
            elf.css({'width':elb.css('width'), 'height':elb.css('height')});
            elf.click(function() {
                if(!armed) {
                    $(this).toggleClass('shade');
                }
                else {
                    armed = false;
                }
            });
            elf.dblclick(function() {
                armed_shade_on = $(this).hasClass('shade');
               $(this).toggleClass('shade');
               armed = true;
            });
            elf.mouseover(function() {
                if(armed) {
                    var has_shade = $(this).hasClass('shade');
                    if((armed_shade_on && has_shade) || (!armed_shade_on && !has_shade))
                        $(this).toggleClass('shade');
                }
            });
            couples.push([elf, elb]);
        });

        $(window).resize(function() {
            overlay.css({
                'width':outterdiv.css('width'),
                'height':outterdiv.css('height')
            });
            $.each(couples, function(idx) {
                this[0].css({'width':this[1].css('width'), 'height':this[1].css('height')});
            });
        });
        
        $(document).bind('keydown', 'Alt+t', function () {
            $.each(couples, function() {
                this[0].toggleClass('shade');
            });
            return false;
        });
        
        $(document).bind('keydown', 'Alt+o', function () {
            $.each(couples, function() {
                this[0].removeClass('shade');
            });
            return false;
        });
        
        return overlay;
    }// add_overlay
    
    function enable_overlay(overlay) {
        overlay.css('display', 'block');
    }
    
    function disable_overlay(overlay) {
        overlay.css('display', 'none');
    }
    
    /* the object */
    function Shader(outterdiv) {
        var visible = false;
        
        var overlay = add_overlay(outterdiv);
        
        this.isVisible = function() {
            return visible;
        };
        
        this.disable_overlay = function() {
            disable_overlay(overlay);
            visible = false;
        };
        
        this.enable_overlay = function() {
            enable_overlay(overlay);
            visible = true;
        };
    }
    
    Shader.prototype.toggleVisible = function() {
        if(this.isVisible()) {
            this.disable_overlay();
        }
        else {
            this.enable_overlay();
        }
    };
    
    return Shader;
})();

OFCODE.Codeview = (function() {
    
    function Codeview(root_id, options) {
        if(options === undefined) {
            options = { linenos: true };
        }
        
        var codeview = $('#codeview');
        var lcb = $('#lcb');
        var rcb = $('#rcb');
        var rcb_pre = $('#rcb > pre');
        var outterdiv = $('#codeview > div');
        var rcb_min_width = rcb.width();
        
        var shader = new OFCODE.Shader(outterdiv);

        function _on_resize() {
            var rcbw_diff = rcb.outerWidth() - rcb.width();
            var ow = outterdiv.width();
            var ow_diff = ow - rcbw_diff;
            
            if(ow_diff < rcb_min_width) {
                rcb.width(rcb_min_width);
            }
            else {
                rcb.width(ow - rcbw_diff);
            }
            lcb.width(rcb.outerWidth());
        }
        
        function add_linenos() {
            outterdiv.after('<div id="codeview_linenos"></div>');
            var overlay = $('#codeview_linenos');
            
            overlay.css({
                'z-index':'7',
                'position':'absolute',
                'top':'0px',
                'left':'0px',
                'width':rcb.outerWidth() - rcb.width(),
                'height':outterdiv.css('height')
            });
            
            $('#lcb > div').each(function(idx) {
                var i = idx + 1;
                overlay.append('<div><pre>'+i+'</div>');
            });
        }// add_linenos
        
        // events
        $(document).bind('keydown', 'Alt+s', function (event) {
            shader.toggleVisible();
            return false;
        });
        
        $(window).resize(function() {
            _on_resize();
        });
        
        if(options.linenos) {
            add_linenos();
        }
        
        _on_resize();// init the layout
        outterdiv.css('overflow-x', 'auto');
    }// Codeview constructor
    
    Codeview.prototype.select_text = function() {
        Utils.Selection.clear();
        Utils.Selection.add(Utils.Ranges.selectNode($('#rcb pre')[0]));
    };
    
    return Codeview;
})();

OFCODE.SysInfo = (function() {

});

OFCODE.BottomFeeder = (function() {
    function BottomFeeder(id) {
        var e_body = $('body');
        var e_window = $(window);

        var e_bf = $(id);
        e_bf.css('position', 'absolute');
        e_body.append(e_bf);

        var yw = e_bf.outerWidth();
        var yh = e_bf.outerHeight();
        var wh = e_window.height();

        function _on_resize() {
            e_bf.offset({left: 0, top: 0});
            wh = e_window.height();
            yw = e_bf.outerWidth();
            e_bf.width(e_body.outerWidth());
            _on_scroll();
        }

        function _on_scroll() {
           e_bf.offset({left: e_window.scrollLeft(), top: e_window.scrollTop()+(wh-yh)});
        }

        e_window.resize(function() { _on_resize(); });
        e_window.scroll(function(e) { _on_scroll(); });


        _on_resize();
        _on_scroll();
    }
    return BottomFeeder;
})();

/**
 * A pane that contains the workspace for a logged in user.
 */
OFCODE.Workspace = (function() {
    var workspace = null;

    function singletonWrap(id) {
        if (workspace === null) {
            workspace = new Workspace(id);
        }
        return workspace;
    }

    function Workspace(id) {
        new OFCODE.BottomFeeder(id);
    }

    return singletonWrap;
})();

/**
 * Singleton displays messages on the screen.
 */
OFCODE.Messanger = (function() {

    var messanger = null;

    /*
     * Any new Messanger calls will all reference the one Messanger instance
     */
    function singletonWrap(endpoint) {
        if (messanger === null) {
            messanger = new Messanger();
        }
        return messanger;
    }

    /*
     * Constructor for Messanger
     */
    function Messanger() {

        var mez = this;

        var hidden = true; // starts hidden

        var messageQueue = [];
 
        var messanger = $(
            '<div id="messanger">' +
                '<div id="msgblk"><span></span><button id="sysmsgnext"></button></div>' +
            '</div>');

        var e_window = $(window);

        var body = $('body'); // wraps whole page, used to get correct width
    
        var e_msgblk= messanger.children('div');

        var e_message = e_msgblk.children('span');

        var e_message_next = e_msgblk.children('button');

        /**
         * Called to close/change sys message
         */
        function closeSysMessage() {
            nextMessage(function() {
                hidden = true;
                e_msgblk.slideUp(function() {
                    e_message.hide();
                });
            });
        }

        /**
         * Display the next sys message in queue
         *
         * @param emptycb callback, called when queue is empty
         */
        function nextMessage(emptycb) {
            // if callback registered to handle empty queue
            if (messageQueue.length <= 0) {
                if (!!emptycb) emptycb();
                return;
            }

            var message  = messageQueue.pop();

            function onchg(m) {
                e_message.html(message);
                if (messageQueue.length === 0) {
                    e_message_next.html('<img src="/images/delete.png" />');
                    e_message_next.children('img').css('margin', '0px 0px -5px 0px');
                }
            }

            if (hidden) {
                onchg(message);
                e_message.show(function() {
                    e_msgblk.slideDown();
                });
                hidden = false;
            }
            else {
                e_msgblk.fadeOut(function() {
                    onchg(message);
                    e_msgblk.fadeIn();
                });
            }
            
        }

        /*
         * Add a message to the messages
         */
        this.addMessage = function(_message) {
            if (!_message) return;
            messageQueue.push(_message);
            if (hidden) {
                nextMessage();
            }
            else if (messageQueue.length == 1) {
                e_message_next.fadeOut(function() {
                    e_message_next.html('<img src="/images/go-next.png" />');
                    e_message_next.children('img').css('margin', '0px 0px -3px 0px');
                    e_message_next.fadeIn();
                });
            }
        };

        // stuff to do when creating messanger

        e_message_next.click(closeSysMessage);
        e_msgblk.hide();
        body.prepend(messanger);
    }

    return singletonWrap;
})();// Messanger


/**
 * Once created will poll given endpoint for new messages.
 */
OFCODE.MessagePoller = (function() {

    function MessagePoller(endpoint) {
        if (!endpoint) throw Error("Must provide an endoint for Messanger");

        /**
         * Responsible for calling message service endpoint and grabbing
         * messages for the user.
         */
        function _getNewMessages() {
            $.ajax({
                url: endpoint,
                success: function(data) {
                    mez.addMessage(data.messages[0]);
                },
                error: function(r, s, e) {
                    console.log("got an error: "+s);
                    poller.stop();
                }
            });
        }

        // gets any new messages
        var poller = new OFCODE.Poller(_getNewMessages, pollTime);

        /**
         * Must be called on page load to start polling for messages
         * for current user.
         */
        this.start = function(rightAway) {
            poller.start(rightAway);
        };
        
        /**
         * Wanna stop message polling, call this guy.
         */
        this.stop = function() {
            poller.stop();
        };
    }

    return MessagePoller;
})();

OFCODE.utils = (function() {
    var _utils =  {
        isString: function(s) {
            return (typeof s == "string");
        }
    };
    return _utils;
})();


/**
 * An object for setting a function to occur ever so often.
 */
OFCODE.Poller = (function() {
    function Poller(func, pollTime) {
        if (!func) throw Error("polling function not defined");
        pollTime = pollTime || 15000;
        var timer = null;

        function _doit() {
            func();
            timer = setTimeout(_doit, pollTime);
        }

        this.isStarted = function() {
            return timer !== null;
        };

        this.start = function(rightAway) {
            if (!!rightAway) func();
            if (timer === null) timer = setTimeout(_doit, pollTime);
            return this;
        };

        this.stop = function() {
            if (timer !== null) {
                clearTimeout(timer);
                timer = null;
            }
            return this;
        };

        this.pollTime = function(_pollTime) {
            if (!!pollTime) {
                if (pollTime > 0) {
                    pollTime = _pollTime;
                }
                else {
                    pollTime = 15000;
                }
            }
            return pollTime;
        };
    }

    return Poller;
})();

OFCODE.supported_modes = [
    'c_cpp', 'css', 'csharp', 'clojure', 'coffee', 'html', 'java',
    'javascript', 'json', 'lua', 'ocaml', 'perl', 'php', 'python',
    'powershell', 'ruby', 'scala', 'scss', 'sql', 'svg', 'text', 'xml'
];
OFCODE.editor_modes = {};
OFCODE.mode_translates = {
    js: 'javascript',
    c: 'c_cpp',
    cpp: 'c_cpp',
    'coffee-script': 'coffee'
};
OFCODE.update_editor_mode = function(mode) {
    if (mode in OFCODE.mode_translates) {
        mode = OFCODE.mode_translates[mode];
    }
    if ($.inArray(mode, OFCODE.supported_modes) == -1) {
        OFCODE.update_editor_mode('text');
        return true;
    }
    if (mode in OFCODE.editor_modes) {
        window.editor.getSession().setMode(new OFCODE.editor_modes[mode]());
    } else {
        // Load the Javascript needed and set the editor
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.async = true;
        s.src = OFCODE.base_js + '/mode-' + mode + '.js';
        $(s).load(function () {
            var loaded_mode = require("ace/mode/" + mode).Mode;
            OFCODE.editor_modes[mode] = loaded_mode;
            window.editor.getSession().setMode(new loaded_mode());
        });
        var x = document.getElementsByTagName('script')[0];
        x.parentNode.insertBefore(s, x);
    }
};

/**
 * Much of the logic for our application resides through this one callback. On
 * ready this'll be called and we'll look for
 */
$(document).ready(function () {
    //new OFCODE.Messanger('/messages').start(true);

    /**
     * Very important function, sets up context for application on page load.
     * User account info, theme preferences and anything really can be
     * attached to this context.
     */
    function setup() {
        // TODO: lookup context or create new
        return {};
    }
    
    /**
     * Called when the page contains the Paste create form. Amoung other things
     * it will setup a lot of key bindings for fast paste good time.
     */
    paste_create = function (context) {
        $('textarea').focus();
        var keybinds = {
            b: 'bash',
            c: 'c',
            h: 'html',
            j: 'java',
            l: 'clojure',
            m: 'html+mako',
            p: 'python',
            r: 'rb',
            t: 'text',
            x: 'xml',
            y: 'yaml'
        };
        var shift_keybinds = {
            c: 'css',
            e: 'erlang',
            h: 'haskell',
            j: 'js',
            p: 'perl'
        };
        $.each(keybinds, function (i, val) {
            $('#language option[value="'+val+'"]').append(' &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#8997;' + i.toUpperCase());
            $(document).bind('keydown', 'Alt+' + i, function () {
                $('#language').val(val);
                OFCODE.update_editor_mode(val);
                return false;
            });
        });
        $.each(shift_keybinds, function (i, val) {
            $('#language option[value="'+val+'"]').append(' &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#8679;&#8997;' + i.toUpperCase());
            $(document).bind('keydown', 'Alt+Shift+' + i, function () {
                $('#language').val(val);
                OFCODE.update_editor_mode(val);
                return false;
            });
        });
        $(document).bind('keydown', 'Alt+return', function () {
            $('input[type=submit]').click();
            return false;
        });
        $(document).bind('keydown', 'Alt+enter', function () {
            $('input[type=submit]').click();
            return false;
        });

        // Determine if we need to load existing code and load it
        var edits = document.location.search.match(/edit=(.*)/);
        if (edits) {
            $.ajax({
                url: '/' + edits[1] + '/json',
                type: 'GET',
                dataTypeString: 'json',
                error: function(event) {
                    alert("Unable to load the paste to edit.");
                },
                success: function(data, textStatus) {
                    OFCODE.update_editor_mode(data.language);
                    window.editor.getSession().setValue(data.code);
                    $('#language').val(data.language);
                }
            });
        } else {
            OFCODE.update_editor_mode('python');
        }
    }; // paste_create
    
    /**
     * Will setup the paste view page, which displays the paste in our
     * Codeview.
     */
    paste_view = function (context) {
        var codeview = new OFCODE.Codeview('junk', {linenos: true});

        // events
        
        $(document).bind('keydown', 'Meta+a', function () {
            window.setTimeout(codeview.select_text, 0);
        });
        
        $(document).bind('keydown', 'Ctrl+a', codeview.select_text);
        
        $('#delete-paste').click(function (event) {
            if (confirm('Are you sure you want to delete this paste?')) {
                $.ajax({
                    url: location.pathname + '/delete',
                    type: 'POST',
                    error: function(event) {
                        alert("Sorry, for some reason it didn't work out, try again.");
                    },
                    success: function(data, textStatus) {
                        alert('Your paste has been deleted.');
                        window.location = '/';
                        return false;
                    }
                });
            }
            event.stopPropagation();
            return false;
        });

        $('#fork-paste').click(function (event) {
            window.location = "/?edit=" + window.location.pathname.split('/')[1];
            return false;
        });

    }; // paste_view
    
    // init code
    
    var context = setup();
    
    var bodyid = $('body').attr('id');

    if (bodyid == 'paste_view') {
        paste_view(context);
    }
    else if( bodyid == 'paste_create'){
        var editor = window.editor = ace.edit("editor");
        if ($('body').hasClass('dark')) {
            editor.setTheme("ace/theme/vibrant_ink");
        } else {
            editor.setTheme("ace/theme/dreamweaver");
        }
        editor.setShowPrintMargin(false);
        editor.getSession().setTabSize(4);
        editor.getSession().setUseSoftTabs(true);
        paste_create(context);
    }
    else if (bodyid == 'none') {
    }
    else {
        alert('Found unknown body id: '+bodyid);
        return;
    }
    

    // Bind submit button when present
    $('input[type=submit]').click(function (event) {
        $('textarea').val(editor.getSession().getValue());
        return true;
    });

    // Bind select box change to update syntax highlight
    $('#language').change(function (event) {
        OFCODE.update_editor_mode($(this).val());
    });

    // GLOBAL site theme and font toggles
    
    $('#toggle_theme').click(function (event) {
        if ($('body').hasClass('dark')) {
            $('body').removeClass('dark').addClass('light');
            editor.setTheme("ace/theme/dreamweaver");
            $.get('/theme_toggle', { style: 'light' });
        } else {
            $('body').removeClass('light').addClass('dark');
            editor.setTheme("ace/theme/vibrant_ink");
            $.get('/theme_toggle', { style: 'dark' });
        }
        event.stopPropagation();
        return false;
    });
    
    $('#toggle_font').click(function (event) {
      if ($('body').hasClass('font_dejavu')) {
          $.get('/font_toggle', { font: 'anonymous' }, function () {
              document.location = location.pathname;
          });
      } else {
          $.get('/font_toggle', { font: 'dejavu' }, function () {
              document.location = location.pathname;
          });
      }
      event.stopPropagation();
      return false;
    });
});


var Utils = {
  NOT_SUPPORTED : {},
  DOM : {
    getElementWithId : function() {
      var func = function() { return Utils.NOT_SUPPORTED; };
      if(document.getElementById) {
        func = function(id) {
          return document.getElementById(id);
        };
      } else if(document.all) {
        func = function(id) {
          return document.all[id];
        };
      }
      return ( this.getElementWithId = func )();
    }
  },
  Ranges : {
    create : function() {
      var func = function() { return Utils.NOT_SUPPORTED; };
      if(document.body && document.body.createTextRange) {
        func = function() { return document.body.createTextRange(); };
      } else if(document.createRange) {
        func = function() { return document.createRange(); };
      }
      return (this.create = func)();
    },
    selectNode : function(node, originalRng) {
      var func = function() { return Utils.NOT_SUPPORTED; };
      var rng = this.create(), method = '';
      if(rng.moveToElementText) { method = 'moveToElementText'; }
      else if(rng.selectNode) { method = 'selectNode'; }
      if(method)
        func = function(node, rng) {
          rng = rng || Utils.Ranges.create();
          rng[method](node);
          return rng;
        };
      return rng = null, (this.selectNode = func)(node, originalRng);
    }
  },
  Selection : {
    clear:function() {
      var func = function() { return Utils.NOT_SUPPORTED; };
      if( typeof document.selection !== 'undefined' ) {
        func = function() {
          if(document.selection && document.selection.empty) {
            return (Utils.Selection.clear = function() {
              if(document.selection) { document.selection.empty(); }
            })();
          }
        };
      } else if(window.getSelection) {
        var sel = window.getSelection();
        if(sel.removeAllRanges) {
          func = function() {
            window.getSelection().removeAllRanges();
          };
        }
        sel = null;
      }
      return (this.clear = func)();
    },
    add : function(originalRng) {
      var func = function() { return Utils.NOT_SUPPORTED; };
      var rng = Utils.Ranges.create();
      if(rng.select) {
        func = function(rng) { rng.select(); };
      } else if(window.getSelection) {
        var sel = window.getSelection();
        if(sel.addRange) {
          func = function(rng) { window.getSelection().addRange(rng); };
        }
        sel = null;
      }
      return (this.add = func) ( originalRng );
    }
  }
};

