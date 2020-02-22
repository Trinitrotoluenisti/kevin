from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler

from random import randint
from datetime import timedelta
import logging


# Initializating 
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)
scheduler = APScheduler()

# Configs
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["JWT_SECRET_KEY"] = str(randint(0, 999999999999))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=45)
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ['access', 'refresh']

# Logging configs
logging.basicConfig(
	                level=logging.DEBUG,
	                filename='api.log',
	                format='%(name)s %(asctime)s %(levelname)s - %(message)s',
	                datefmt='[%d/%m/%y %H:%M:%S]'
	               )

logging.getLogger('werkzeug').disabled = True
logging.getLogger('apscheduler.scheduler').disabled = True
logging.getLogger('apscheduler.executors.default').disabled = True


from .database import *
from .routes import *


# Add tokens' blacklist cleaning process to the schedule
scheduler.add_job(func=RevokedTokens.clean, trigger='interval', id='blacklist_clean', seconds=5)
