from flask import Flask


app = Flask(__name__)
server = "http://localhost:8080"
tokens_age = 45 * 60 # 45 Minutes


from .routes import *
