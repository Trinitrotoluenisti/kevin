from secrets import token_hex
from datetime import timedelta, datetime



class ProductionConfigs(object):
    # Things
    SECRET_KEY = token_hex(16)
    HOST = "0.0.0.0"
    PORT = 8080

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/database.db'
    DATABASE_PATH = 'application/database/'

    # Tokens
    JWT_SECRET_KEY = token_hex(16)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_BLACKLIST_CLEANING = {'minutes': 30}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=45)
    JWT_REFRESH_TOKEN_EXPIRES = False

class TestingConfigs(ProductionConfigs):
    TESTING = True

    # Temporary database
    dt = int(datetime.now().timestamp())
    SQLALCHEMY_DATABASE_URI = f'sqlite:////tmp/kevin-{dt}/test.db'
    DATABASE_PATH = f'/tmp/kevin-{dt}/'

    # Expirations fastened
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3)
