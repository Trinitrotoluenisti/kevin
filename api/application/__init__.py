from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from random import randint
from datetime import timedelta


# app initializing
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# app configs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["JWT_SECRET_KEY"] = "nJibin_iniuui£568vh"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=45)


from .database import *
from .routes import *
