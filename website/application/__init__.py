from flask import Flask

app = Flask(__name__)
server = "http://localhost:8080"

from .routes import *

