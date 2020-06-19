from flask import request
from flask_jwt_extended import *
from sqlalchemy.exc import IntegrityError
from re import search

from . import jwt, logging, db
from .database import *
from .utils import *



# UNPROTECTED
@app.route('/')
def ping():
    return {"message": "AUDP APIs working!", "version": "dev"}

@app.route('/login', methods=['POST'])
def login():
    # Fetch request's body
    try:
        username, password = get_from_body('username', 'password')
    except ValueError:
        logging.debug(f"{get_ip()} tried to login with a wrong content-type")
        return {'error': 'invalid request', 'description': "Content-Type must be application/json"}, 400
    except KeyError as e:
        field_name = str(e).replace("'", '')
        logging.debug(f"{get_ip()} tried to login without {field_name}")
        return {'error': 'invalid login', 'description': f"Missing user's {field_name}"}, 400

    # Check credentials
    if not User.check(username, password):
        logging.info(f"{get_ip()} tried to login with wrong credentials as '{username}'")
        return {"error": "invalid login", "description": "Wrong username or password"}, 401

    # Generate tokens
    access = create_access_token(identity=username)
    refresh = create_refresh_token(identity=username)

    logging.info(f"{get_ip()} logged in as '{username}'")
    return {"accessToken": access, "refreshToken": refresh}, 200

@app.route('/register', methods=['POST'])
def register():
    # Fetch request's body
    try:
        username, email, password, name, surname = get_from_body('username', 'email', 'password', 'name', 'surname')
    except ValueError:
        logging.debug(f"{get_ip()} tried to login with a wrong content-type")
        return {'error': 'invalid request', 'description': "Content-Type must be application/json"}, 400
    except KeyError as e:
        field_name = str(e).replace("'", '')
        logging.debug(f"{get_ip()} tried to login without {field_name}")
        return {'error': 'invalid user', 'description': f"Missing user's {field_name}"}, 400

    # Check username's length
    if len(username) < 5:
        logging.debug(f"{get_ip()} tried to register with an username too short")
        return {"error": "invalid user", "description": "User's username is too short"}, 400

    # Check password's length
    if len(password) < 8:
        logging.debug(f"{get_ip()} tried to register with a password too short")
        return {"error": "invalid user", "description": "User's password is too short"}, 400

    # Check if email is an email
    elif not search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
        logging.debug(f"{get_ip()} tried to register with invalid email")
        return {"error": "invalid user", "description": "User's email is not an email"}, 400

    # Try add it in the database
    try:
        User(username=username, email=email, password=password, name=name, surname=surname).save()
    except IntegrityError:
        logging.debug(f"{get_ip()} tried to register with already used fields")
        return {"error": "user already exists", "description": "Some user's data have already been used"}, 409

    # Generate the tokens
    access = create_access_token(identity=username)
    refresh = create_refresh_token(identity=username)

    logging.info(f"{get_ip()} registered as '{username}'")
    return {"accessToken": access, "refreshToken": refresh}, 201

@app.route('/users/<string:username>')
def users_view(username):
    # If a username is specified, check if exists
    user = User.from_username(username)
    if not user:
        logging.debug(f"{get_ip()} requested informations of non-existent user")
        return {"error": "User does not exist", "description": "Can't find an user with that username"}, 404

    user = user.json()

    # Check if user's email is public
    if not user["isEmailPublic"]:
        del user["email"]

    logging.info(f"{get_ip()} requested informations of '{username}'")
    return user


# PROTECTED
@app.route('/token', methods=['PUT'])
@jwt_refresh_token_required
def refresh_access_token():
    # Fetch data
    username = get_jwt_identity()

    # Return an ok message
    logging.debug(f"'{username}' ({get_ip()}) refreshed his access token")
    return {'accessToken': create_access_token(identity=username)}

@app.route('/token/access', methods=['DELETE'])
@jwt_required
def rovoke_access_token():
    # Fetch data
    jti = get_raw_jwt()['jti']
    exp = get_raw_jwt()['exp']
    username = get_jwt_identity()

    # Revoke token
    RevokedTokens(jti=jti, exp=exp).save()

    # Return an ok message
    logging.info(f"'{username}' ({get_ip()}) revoked his access token")
    return {}, 204

@app.route('/token/refresh', methods=['DELETE'])
@jwt_refresh_token_required
def revoke_refresh_token():
    # Fetch data
    jti = get_raw_jwt()['jti']
    username = get_jwt_identity()

    # Revoke token
    RevokedTokens(jti=jti).save()

    # Return an ok message
    logging.info(f"'{username}' ({get_ip()}) revoked his refresh token")
    return {}, 204

@app.route('/user')
@jwt_required
def user_view():
    # Get username from jwt
    username = get_jwt_identity()

    # Get the user from the database
    user = User.from_username(username).json()

    logging.debug(f"'{username}' ({get_ip()}) requested his informations")
    return user


"""
@app.route('/post', methods=['POST'])
@jwt_required
def post_create():
    # Fetch parameters
    try:
        body = request.get_json()
        title = body.get('title', '')
        content = body['content']
        tags = body.get('tags', '')
    except (KeyError, TypeError):
        logging.debug(f"{get_ip()} tried to register without parameters")
        return {"msg": "Missing parameter(s)"}, 400

    # Check content lenght
    if len(content) < 20:
        logging.debug(f"{get_ip()} tried to create an empty post")
        return {"msg": "Post content empty or too short"}, 400

    # Save the post
    user = User.from_username(get_jwt_identity())
    post = Post(user, title, content, tags)
    post.save()

    # Log the post creation
    logging.info(f"{user.username} created a post (id #{post.id})")

    # Return an ok message
    return {'msg': 'Ok'}

"""
