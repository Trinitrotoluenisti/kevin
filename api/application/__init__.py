from flask import Flask
from flask_apscheduler import APScheduler
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from os import environ

from .configs import ProductionConfigs, TestingConfigs



# Initialize Flask
app = Flask(__name__)

# Load configurations from configs.py
app.config.from_object(TestingConfigs if bool(environ.get('TESTING')) else ProductionConfigs)

# Initialize things
db = SQLAlchemy(app)
jwt = JWTManager(app)
scheduler = APScheduler()

# Import other file's content
from .models import *
from .errors import *
from .routes import *

# Initialize scheduler
scheduler.init_app(app)
scheduler.add_job(id='blacklist_cleaner', func=RevokedTokens.clean, trigger='interval', **app.config['JWT_BLACKLIST_CLEANING'])
