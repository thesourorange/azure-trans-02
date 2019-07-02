from flask import Flask, render_template
from flask_bower import Bower
from azure_trans_webapp.processors.views import views

print('Creating', __name__)

app = Flask(__name__)    # Create an instance of the class for our use
        
Bower(app) 

app.register_blueprint(views)

wsgi_app = app.wsgi_app
