from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import logging

from .configs import *


# Initialize Flask
app = Flask(__name__)

# Load configuations from configs.py
if app.config["DEBUG"]:
    app.config.from_object(DebugConfigs)
elif app.config["TESTING"]:
    app.config.from_object(TestingConfigs)
else:
    app.config.from_object(ProductionConfigs)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    filename=app.config['LOGS_FILENAME'],
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='[%d/%m/%y %H:%M:%S]')
logging.getLogger('werkzeug').disabled = True
logging.getLogger('apscheduler.scheduler').disabled = True
logging.getLogger('apscheduler.executors.default').disabled = True

# Initialize Flask frameworks
api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Import other file's content
from .database import *
from .routes import *

# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job(id='blacklist_clean', func=RevokedTokens.clean, trigger='interval', **app.config['JWT_BLACKLIST_CLEANING'])
scheduler.start()
