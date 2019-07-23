""" 
In this sample, the Flask app object is contained within the hello_app *module*;
that is, hello_app contains an __init__.py along with relative imports. Because
of this structure, a file like webapp.py cannot be run directly as the startup
file through Gunicorn; the result is "Attempted relative import in non-package".

The solution is to provide a simple alternate startup file, like this present
startup.py, that just imports the app object. You can then just specify
startup:app in the Gunicorn command.
"""

from os import environ
from  azure_trans_webapp.webapp import app
from os

f = open('debug_start.log', a)
f.write('started')
f.close()

if __name__ == '__main__':

    HOST = environ.get('SERVER_HOST', 'localhost')

    try:

        PORT = int(environ.get('PORT', '5555'))
        print('Starting on PORT:', PORT)

    except ValueError:

        PORT = 5555
    
    app.run(HOST, PORT)
