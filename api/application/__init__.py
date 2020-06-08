from sys import argv
from flask import Flask
from flask_apscheduler import APScheduler
import logging

from .configs import *


# Initialize Flask
app = Flask(__name__)


# Load configurations from configs.py
if argv[-1] == '-d':
    configs = 'DebugConfigs'
    app.config.from_object(DebugConfigs)
elif argv[-1] == '-t':
    configs = 'TestingConfigs'
    app.config.from_object(TestingConfigs)
else:
    configs = 'ProductionConfigs'
    app.config.from_object(ProductionConfigs)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    filename=app.config['LOGS_FILENAME'],
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='[%d/%m/%y %H:%M:%S]')
logging.getLogger('werkzeug').disabled = True
logging.getLogger('apscheduler.scheduler').disabled = True
logging.getLogger('apscheduler.executors.default').disabled = True

# Log the configs' type
logging.error('Loaded ' + configs)


# Import other file's content
from .database import *
from .routes import *


# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job(id='blacklist_clean', func=RevokedTokens.clean, trigger='interval', **app.config['JWT_BLACKLIST_CLEANING'])
scheduler.start()
