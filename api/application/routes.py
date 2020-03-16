from . import api, db, jwt, logging
from .database import User, RevokedTokens

from flask import request
from flask_restful import Resource
from flask_jwt_extended import *
from sqlalchemy.exc import IntegrityError

from re import search


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Check if tokens are in blacklist
    jti = decrypted_token['jti']

    return bool(RevokedTokens.query.filter_by(jti=jti).first())


class Ping(Resource):
    def get(self):
        return {"msg": "Working"}

class Login(Resource):
    def post(self):
        # fetch parameters
        try:
            username = str(request.form['username'])
            password = str(request.form['password'])
        except KeyError:
            logging.debug(f"{request.remote_addr} tried to login without parameters")
            return {"msg": "Missing parameter(s)"}, 400

        # check credentials
        try:
            user = User.check(username, password)
        except ValueError:
            logging.info(f"{request.remote_addr} tried to login with wrong credentials as '{username}'")
            return {"msg": "Wrong username or password"}, 400

        # generate tokens
        access = create_access_token(identity=user.username)
        refresh = create_refresh_token(identity=user.username)

        # return and log all
        logging.info(f"{request.remote_addr} logged in as '{username}'")
        return {"msg": "Ok", "access_token": access, "refresh_token": refresh}

class Register(Resource):
    def post(self):
        # fetch parameters
        try:
            username = str(request.form['username'])
            name = str(request.form['name'])
            surname = str(request.form['surname'])            
            email = str(request.form['email'])
            password = str(request.form['password'])
        except KeyError:
            logging.debug(f"{request.remote_addr} tried to register without parameters")
            return {"msg": "Missing parameter(s)"}, 400

        # check parameters lenght
        if not len(username) > 4 or not len(password) > 4:
            logging.debug(f"{request.remote_addr} tried to register with invalid parameters")
            return {"msg": "username and/or password too short"}, 400

        # check if email is an email
        elif not search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            logging.debug(f"{request.remote_addr} tried to register with invalid infos")
            return {"msg": "Invalid email"}, 400

        # Try add it in the database
        try:
            User(username=username, name=name, surname=surname, email=email, password=password).save()

        # If it's already present in the db
        except IntegrityError:
            db.session.rollback()
            logging.debug(f"{request.remote_addr} tried to register with already used infos")
            return {"msg": "Already registered"}, 400

        # generate the tokens
        access = create_access_token(identity=username)
        refresh = create_refresh_token(identity=username)

        # log and return all
        logging.info(f"{request.remote_addr} registered as '{username}'")
        return {"msg": "Ok", "access_token": access, "refresh_token": refresh}

class Refresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        # Fetch data
        username = get_jwt_identity()
        jti = get_raw_jwt()['jti']

        # Log and return all
        logging.debug(f"'{username}' ({request.remote_addr}) refreshed his access token")
        return {'msg': 'Ok', 'access_token': create_access_token(identity=username)}

class LogoutAccess(Resource):
    @jwt_required
    def post(self):
        # Fetch data
        jti = get_raw_jwt()['jti']
        exp = get_raw_jwt()['exp']
        username = get_jwt_identity()

        # Revoke token
        RevokedTokens(jti=jti, exp=exp).save()

        # Log and return all
        logging.info(f"'{username}' ({request.remote_addr}) revoked his access token")
        return {'msg': 'Ok'}

class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        # Fetch data
        jti = get_raw_jwt()['jti']
        exp = get_raw_jwt()['exp']
        username = get_jwt_identity()

        # Revoke token
        RevokedTokens(jti=jti, exp=exp).save()

        # Log and return all
        logging.info(f"'{username}' ({request.remote_addr}) revoked his refresh token")
        return {'msg': 'Ok'}

class ViewUser(Resource):
    @jwt_optional
    def get(self, username=None):
        # if username isn't specified, return your infos
        if not username:
            username = get_jwt_identity()

            # check if it's logged in
            if not username:
                logging.debug(f"{request.remote_addr} requested informations of non-existent user")
                return {"msg": "No username specified"}, 401

            # fetch user infos and change something
            user = User.query.filter_by(username=username).first().json
            del user['id'], user['password']
            user['msg'] = "Ok"

            # return them
            logging.debug(f"'{username}' ({request.remote_addr}) requested his informations")
            return user

        # if a username is specified, check if exists
        user = User.query.filter_by(username=username).first()

        if not user:
            logging.debug(f"{request.remote_addr} requested informations of non-existent user")
            return {"msg": "User does not exist"}, 404

        # If it exists, fetch his public data
        user = user.json
        del user['id'], user['name'], user['surname'], user['password']
        user['msg'] = 'Ok'

        # log all and return it
        logging.info(f"{request.remote_addr} requested informations of an user '{username}'")
        return user



# Add resources to APIs
api.add_resource(Ping, '/', '/ping')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Refresh, '/refresh')
api.add_resource(LogoutAccess, '/logout/access')
api.add_resource(LogoutRefresh, '/logout/refresh')
api.add_resource(ViewUser, '/user', '/user/<string:username>')
