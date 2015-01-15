<%text filter="rst_render">
===
API
===

Of Code provides an API to update, retrieve, and create content on the Of Code sites.

Pastes
======

Retrieve List of Available Languages
------------------------------------

Before posting a paste, it is useful to have a list of the available languages
that may be used.

.. code-block:: text
    
    GET http://paste.ofcode.org/api/1.0/languages

Will return a JSON structure of the languages including the language key that
should be used during a POST, and the human readable version:
    
.. code-block:: javascript
    
    {
        "ragel-java": "Ragel in Java Host", 
        "coffee-script": "CoffeeScript", 
        "antlr-as": "ANTLR With ActionScript Target", 
        "antlr": "ANTLR", 
        "text": "Text only", 
        "aspx-vb": "aspx-vb", 
        "newspeak": "Newspeak",
        ...
    }


Post a Paste
------------

Pastes posted through the API have a default expire time of 24 hours from the time it
was posted.

.. note::
    
    Future API updates will allow customizeable expirations when the user is logged in.

To post a paste:

.. code-block:: text
    
    POST http://paste.ofcode.org/api/1.0/

The content of the POST should be a JSON structure:

.. code-block:: javascript

    {
        code: "The code to be posted as\na large block of text.",
        language: "text"
    }

Note that the language must be a valid language as described in the available languages
results. Or if you'd like to have the languaged guessed based on the content, set it to
``guess``.

After a successful post, the API will return the status of the paste, and the URL it
can be reached at if it was successful:

.. code-block:: javascript
    
    // A successful paste POST
    {
        status: 'success',
        url: 'http://paste.ofcode.org/QmTQFsAK2Tyu5AiiXa6PtU'
    }
    
    // Or if the POST failed
    {
        status: 'failure',
        reason: 'Invalid language'
    }


Tracebacks
==========

.. note::
    
    The Traceback API is previewed here, but is not currently available.

Post a Traceback
----------------

To post a traceback:

.. code-block:: text

    POST http://trace.ofcode.org/api/1.0/

The content of the POST should be a JSON structure:

.. code-block:: js
    
    {
        traceback: {
            // Optional, if this traceback was caused by another
            cause: 'other_exception',
            
            type: 'GenerationException',
            value: "url_for could not generate URL. Called with args: ()",
            
            // Currently only values of python, ruby, or java are accepted
            language: 'python',
            
            version: '2.5.2',
            full_version: '2.5.2 darwin',
            platform: 'osx'
        }
        frames: [
            {
                // For Java tracebacks, this should be the declaringClass
                module: 'weberror.evalexception',
                
                line: 431,
                function: 'respond',
                operation: 'app_iter = self.application(environ, detect_start_response)',
                
                // Optional
                filename: '/path/to/file',
                variables: 'str repr of vars in scope'
            },
            {
                // Repeating for each frame, in order
                // of the top caller to the bottom
            }
        ]
        
        // If this exception was caused by another one (Java, Python 3+), then
        // add another traceback / frames section for it
        // traceback only needs these values, while frames should be the
        // same as for the frames above:
        traceback_1: {
            // Optional, if this traceback was caused by another
            cause: 'other_exception',
            
            type: 'GenerationException',
            value: "url_for could not generate URL. Called with args: ()"
        },
        frames_1: {
            ...
        },
        meta: {
            description: 'This happened when I upgraded from Routes 1.10 to 1.12',
            
            // Optional, supplying an email address will let the user be notified
            // when comments are added. An email will also be sent with a special
            // URL that allows the person clicking it to mark a comment as the
            // solution and/or delete the traceback post.
            
            // Notifications can be true or false if comments on the traceback
            // should send an email to the user
            email: 'fred@nowhere.com',
            notifications: true
        }
        libraries: {
            // A maximum of 50 libraries may be specified
            beaker: '1.4.3',
            formencode: '1.2.2'
        }
        
        // Optional, environment may store arbitrary keys with single string values
        // or a key/value structure. The key/value structure may NOT contain more nested
        // structures.
        environment: {
            // Valid examples
            http_environment: 'True',
            wsgi: {
                HTTP_HOST: 'http://...'
            }
        }
    }


</%text>
<%inherit file="/layout.mak"/>
<%!
from pasteofcode.helpers import rst_render
%>
