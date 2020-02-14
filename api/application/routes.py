from . import api, db
from .database import User

from flask import request
from flask_restful import Resource
from flask_jwt_extended import (create_access_token, create_refresh_token,
                               jwt_refresh_token_required, get_jwt_identity,
                               jwt_required)
from sqlalchemy.exc import IntegrityError

from re import search


class Ping(Resource):
    def get(self):
        return {"msg": "Working"}

# TEMPORARY
class Protected(Resource):
    @jwt_required
    def post(self):
        return {"msg": "Working"}

class Login(Resource):
    def post(self):
        # fetch parameters
        try:
            username = str(request.form['username'])
            password = str(request.form['password'])
        except KeyError:
            return {"msg": "Missing parameter(s)"}, 400

        # check credentials
        try:
            user = User.check(username, password)
        except ValueError:
            return {"msg": "Wrong username or password"}, 400

        # return the token
        access = create_access_token(identity=user.username)
        refresh = create_refresh_token(identity=user.username)
        return {"msg": "Ok", "access_token": access, "refresh_token": refresh}

class Register(Resource):
    def post(self):
        # fetch parameters
        try:
            username = str(request.form['username'])
            email = str(request.form['email'])
            password = str(request.form['password'])
        except KeyError:
            return {"msg": "Missing parameter(s)"}, 400

        # check parameters lenght
        if not len(username) > 4 or not len(password) > 4:
            return {"msg": "username and/or password too short"}, 400

        # check if email is an email
        elif not search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            return {"msg": "Invalid email"}, 400

        # Try add it in the database
        try:
            User(username=username, email=email, password=password).save()

        # If it's already present in the db
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Already registered"}, 400

        # if nothing goes wrong, return the token
        access = create_access_token(identity=username)
        refresh = create_refresh_token(identity=username)
        return {"msg": "Ok", "access_token": access, "refresh_token": refresh}


class Refresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        username = get_jwt_identity()
        return {'msg': 'Ok', 'access_token': create_access_token(identity=username)}


api.add_resource(Ping, '/', '/ping')
# TEMPORARY
api.add_resource(Protected, '/protected')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Refresh, '/refresh')
