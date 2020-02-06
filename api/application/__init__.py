from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from random import randint


# app initializing
app = Flask(__name__)

# app configs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["JWT_SECRET_KEY"] = str(randint(0, 99999))

# api initializing
api = Api(app)
jwt = JWTManager(app)


from .database import *
from .routes import *
