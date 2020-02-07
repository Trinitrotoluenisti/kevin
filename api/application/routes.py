from . import api
from .database import User

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token


class Ping(Resource):
    def get(self):
        return {"msg": "Working"}

class Login(Resource):
    def post(self):
        # fetch parameters
        try:
            username = request.form['username']
            password = request.form['password']
        except KeyError:
            return {"msg": "Missing parameter(s)"}, 400

        # check credentials
        try:
            user = User.check(username, password)
        except ValueError:
            return {"msg": "Wrong username or password"}, 400

        # return the token
        return {"msg": "Ok", "token": create_access_token(identity=user.username)}


api.add_resource(Ping, '/', '/ping')
api.add_resource(Login, '/login')
