from secrets import token_hex
from datetime import timedelta


class ProductionConfigs(object):
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/database.db'
    DATABASE_PATH = 'application/database'

    # Tokens
    JWT_SECRET_KEY = token_hex(16)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_BLACKLIST_CLEANING = {'minutes': 30}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=45)
    JWT_REFRESH_TOKEN_EXPIRES = False

    # Logs
    LOGS_FILENAME = 'api.log'


class DebugConfigs(ProductionConfigs):
    JWT_SECRET_KEY = 'constant-key'
    LOGS_FILENAME = '/dev/null'


class TestingConfigs(ProductionConfigs):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/kevin/test.db'
    DATABASE_PATH = '/tmp/kevin/'
    JWT_BLACKLIST_CLEANING = {'seconds': 3}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3)
    LOGS_FILENAME = '/dev/null'
