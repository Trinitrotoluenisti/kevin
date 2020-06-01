from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

from json import load as json_load
from datetime import timedelta
import logging

from secrets import configs, hash_password


# Initialize Flask
app = Flask(__name__)

# Save configs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = configs['DB']['sqlite3']
app.config["JWT_SECRET_KEY"] = configs['JWT']['secret_key']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(**configs['JWT']['token_expiration'])
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = False
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ['access', 'refresh']
logging.basicConfig(level=logging.DEBUG, filename=configs['LOG']['filename'], format='%(asctime)s %(levelname)s - %(message)s', datefmt='[%d/%m/%y %H:%M:%S]')
logging.getLogger('werkzeug').disabled = True
logging.getLogger('apscheduler.scheduler').disabled = True
logging.getLogger('apscheduler.executors.default').disabled = True

# Initialize Flas frameworks
api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
scheduler = APScheduler()

# Import other file's content
from .database import *
from .routes import *

# Add functions to scheduler
scheduler.add_job(func=RevokedTokens.clean, trigger='interval', id='blacklist_clean', **configs['JWT']['blacklist_clean'])
