from flask import Flask
from flask_apscheduler import APScheduler
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sys import argv

from .configs import *



# Initialize Flask
app = Flask(__name__)


# Load configurations from configs.py
if argv[-1] == '-t':
    configs = 'TestingConfigs'
    app.config.from_object(TestingConfigs)
else:
    configs = 'ProductionConfigs'
    app.config.from_object(ProductionConfigs)

# Initialize flask_sqlalchemy and flask_jwt_extended
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Import other file's content
from .models import *
from .errors import *
from .routes import *


# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job(id='blacklist_cleaner', func=RevokedTokens.clean, trigger='interval', **app.config['JWT_BLACKLIST_CLEANING'])
