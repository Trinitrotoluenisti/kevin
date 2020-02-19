from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler

from random import randint
from datetime import timedelta


# app initializing
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# app configs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["JWT_SECRET_KEY"] = str(randint(0, 999999999999))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=45)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


# import from routes and database
from .database import *
from .routes import *


# define the function to start the APIs!
def run(**kwargs):
    scheduler = APScheduler()
    scheduler.add_job(func=RevokedTokens.clean, trigger='interval', id='blacklist_clean', minutes=30)
    scheduler.start()
    app.run(**kwargs)
