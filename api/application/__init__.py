from flask import Flask
from flask_restful import Api


# app initializing
app = Flask(__name__)

# app configs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# api initializing
api = Api(app)


from .database import *
from .routes import *
