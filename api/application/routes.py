from flask import request
from flask_restful import Resource
from flask_jwt_extended import *
from sqlalchemy.exc import IntegrityError
from re import search

from .main import api, db, jwt, logging
from .database import User, RevokedTokens, Post


# Get original IP
get_ip = lambda: request.headers.get('X-Forwarded-For', request.remote_addr)

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
            logging.debug(f"{get_ip()} tried to login without parameters")
            return {"msg": "Missing parameter(s)"}, 400

        # check credentials
        try:
            user = User.check(username, password)
        except ValueError:
            logging.info(f"{get_ip()} tried to login with wrong credentials as '{username}'")
            return {"msg": "Wrong username or password"}, 400

        # generate tokens
        access = create_access_token(identity=user.username)
        refresh = create_refresh_token(identity=user.username)

        # return and log all
        logging.info(f"{get_ip()} logged in as '{username}'")
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
            logging.debug(f"{get_ip()} tried to register without parameters")
            return {"msg": "Missing parameter(s)"}, 400

        # check parameters lenght
        if not len(username) > 4 or not len(password) > 4:
            logging.debug(f"{get_ip()} tried to register with invalid parameters")
            return {"msg": "username and/or password too short"}, 400

        # check if email is an email
        elif not search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            logging.debug(f"{get_ip()} tried to register with invalid infos")
            return {"msg": "Invalid email"}, 400

        # Try add it in the database
        try:
            User(username=username, name=name, surname=surname, email=email, password=password).save()

        # If it's already present in the db
        except IntegrityError:
            db.session.rollback()
            logging.debug(f"{get_ip()} tried to register with already used infos")
            return {"msg": "Already registered"}, 400

        # generate the tokens
        access = create_access_token(identity=username)
        refresh = create_refresh_token(identity=username)

        # log and return all
        logging.info(f"{get_ip()} registered as '{username}'")
        return {"msg": "Ok", "access_token": access, "refresh_token": refresh}

class Refresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        # Fetch data
        username = get_jwt_identity()
        jti = get_raw_jwt()['jti']

        # Log and return all
        logging.debug(f"'{username}' ({get_ip()}) refreshed his access token")
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
        logging.info(f"'{username}' ({get_ip()}) revoked his access token")
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
        logging.info(f"'{username}' ({get_ip()}) revoked his refresh token")
        return {'msg': 'Ok'}

class ViewUser(Resource):
    @jwt_optional
    def get(self, username=None):
        # if username isn't specified, return your infos
        if not username:
            username = get_jwt_identity()

            # check if it's logged in
            if not username:
                logging.debug(f"{get_ip()} requested informations of non-existent user")
                return {"msg": "Missing Authorization Header"}, 401

            # fetch user infos and change something
            user = User.from_username(username).json()
            user['msg'] = "Ok"

            # return them
            logging.debug(f"'{username}' ({get_ip()}) requested his informations")
            return user

        # if a username is specified, check if exists
        user = User.from_username(username)

        if not user:
            logging.debug(f"{get_ip()} requested informations of non-existent user")
            return {"msg": "User does not exist"}, 404

        # If it exists, fetch his public data
        user = user.json()
        del user['name'], user['surname']
        user['msg'] = 'Ok'

        # log all and return it
        logging.info(f"{get_ip()} requested informations of '{username}'")
        return user

class CreatePost(Resource):
    @jwt_required
    def post(self):
        user = User.from_username(get_jwt_identity())
        title = request.form.get('title', None)
        content = request.form.get('content', '')
        tags = request.form.get('tags', '')

        # check content lenght
        if len(content) < 20:
            logging.debug(f"{get_ip()} tried to create an empty post")
            return {"msg": "Post content empty or too short"}, 400

        # save the post
        post = Post(user, title, content, tags)
        post.save()

        # log the post creation
        logging.info(f"{user.username} created a post (id #{post.id})")

        # return an ok msg
        return {'msg': 'Ok'}


# Add resources to APIs
api.add_resource(Ping, '/', '/ping')
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(Refresh, '/refresh')
api.add_resource(LogoutAccess, '/logout/access')
api.add_resource(LogoutRefresh, '/logout/refresh')
api.add_resource(ViewUser, '/user', '/user/<string:username>')
api.add_resource(CreatePost, '/post')
