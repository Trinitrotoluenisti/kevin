from flask import Flask
from requests import get


app = Flask(__name__)
server = "http://localhost:8080"
tokens_age = 45 * 60 # 45 Minutes

# Check if there's a server online
try:
	get(server)
except ConnectionError:
	raise ConnectionError("There isn't an API running in that URL") from None


from .routes import *
