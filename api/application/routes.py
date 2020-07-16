from flask_jwt_extended import *
from sqlalchemy.exc import IntegrityError

from . import app, db
from .errors import APIErrors
from .utils import get_from_body
from .models import User, Community, Follow, RevokedTokens
from .passwords import hash_password



# Not Protected
@app.route('/login', methods=['POST'])
def login():
    """
    Generates a new pair of tokens for the user.
    """

    # Fetches request's body
    username, password = get_from_body({'username': 240, 'password': 250})

    # Checks credentials
    user = User.query.filter_by(username=username).first()
    if not user or not user.password == hash_password(password):
        raise APIErrors[220]

    # Generates new tokens
    access = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)

    return {"accessToken": access, "refreshToken": refresh}, 200

@app.route('/register', methods=['POST'])
def register():
    """
    Creates a new user and saves it in the database.
    """

    # Fetches request's body
    username, password, email, name, surname = get_from_body({'username': 240, 'password': 250, 'email': 260, 'name': 270, 'surname': 280})

    # Checks if user is valid
    user = User(username=username, email=email, password=password, name=name, surname=surname, public_email=False, perms=0, bio='')
    user.check()

    # Tries to save it in the database
    try:
        user.password = hash_password(password)
        user.save()
    except IntegrityError:
        db.session.rollback()
        raise APIErrors[230]

    # Generates new tokens
    access = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)

    return {"accessToken": access, "refreshToken": refresh}, 201

@app.route('/users/<string:username>')
@jwt_optional
def view_user(username):
    """
    Gets informations about an user.

    - username (str): user's username
    """

    # Checks if user exists
    target_user = User.query.filter_by(username=username).first()
    logged_user = User.query.filter_by(id=get_jwt_identity()).first()

    if not target_user:
        raise APIErrors[200]

    target_user = target_user.json()

    # Removes the email from the user if it isn't logged in and isEmailPublic is set to false
    if (not logged_user or not target_user == logged_user.json()) and not target_user["isEmailPublic"]:
        del target_user["email"]

    return target_user

@app.route('/communities')
@jwt_optional
def list_communities():
    """
    Gets the list of communities.
    """

    # Fetches the list of communities
    communities = list(map(lambda c: c.json(), Community.query.all()))

    # If there is an authentication, it checks also if the user is following that community
    user_id = get_jwt_identity()
    if user_id:
        for community in communities:
            follows = Follow.query.filter_by(follower_id=user_id, community_id=community['id']).first()
            community['following'] = bool(follows)

    return {'communities': communities}

@app.route('/communities/<string:name>')
@jwt_optional
def get_communities(name):
    """
    Returns a specific community.

    - name (str): community's name
    """

    # Tries to get the community
    community = Community.query.filter_by(name=name).first()

    # Returns an error if it doesn't exist
    if not community:
        raise APIErrors[300]

    community = community.json()

    # If there is an authentication, it checks if the user is following it
    user_id = get_jwt_identity()
    if user_id:
        follow = Follow.query.filter_by(follower_id=user_id, community_id=community['id']).first()
        community['following'] = bool(follow)

    return community


# Protected
@app.route('/token', methods=['PUT'])
@jwt_refresh_token_required
def refresh_token():
    """
    Generates a new access token from a refresh token.
    """

    return {'accessToken': create_access_token(identity=get_jwt_identity())}

@app.route('/token')
@jwt_required
def get_token():
    """
    Returns the username of the logged-in user.
    """

    logged_user = User.query.filter_by(id=get_jwt_identity()).first()
    return {'username': logged_user.username}

@app.route('/token/access', methods=['DELETE'])
@jwt_required
def revoke_access_token():
    """
    Revokes the access token
    """

    token = get_raw_jwt()
    RevokedTokens(jti=token['jti'], exp=token['exp']).save()

    return {}, 204

@app.route('/token/refresh', methods=['DELETE'])
@jwt_refresh_token_required
def revoke_refresh_token():
    """
    Revokes the refresh token
    """

    RevokedTokens(jti=get_raw_jwt()['jti']).save()

    return {}, 204

@app.route('/users/<string:username>', methods=['DELETE'])
@jwt_required
def delete_user(username):
    """
    Removes the user from the database

    - username (str): user's username
    """

    # Checks if the user exists
    target_user = User.query.filter_by(username=username).first()
    logged_user = User.query.filter_by(id=get_jwt_identity()).first()

    if not target_user:
        raise APIErrors[200]

    # Raises an error if the user isn't logged in or there aren't enough perms
    if not target_user == logged_user and logged_user.perms < 2:
        raise APIErrors[210]

    # Deletes the user
    db.session.delete(target_user)
    db.session.commit()

    return {}, 204

@app.route('/users/<string:username>/<string:field>', methods=['PUT'])
@jwt_required
def edit_user(username, field):
    """
    Edit the user's infos.

    - username (str): user's username
    - field (str): the field to edit
    """

    # Checks if the user exists
    target_user = User.query.filter_by(username=username).first()
    logged_user = User.query.filter_by(id=get_jwt_identity()).first()

    if not target_user:
        raise APIErrors[200]

    # Checks if field is valid
    elif not field in ('username', 'password', 'email', 'name', 'surname', 'bio', 'isEmailPublic'):
        raise APIErrors[100]

    # Raises an error if the user isn't logged in
    elif not target_user == logged_user:
        raise APIErrors[211]

    # Gets new value and fetches user from the database
    error_codes = {'username': 240, 'password': 250, 'email': 260, 'isEmailPublic': 262, 'name': 270, 'surname': 280, 'bio': 290}
    value = get_from_body({'value': error_codes[field]})[0]

    # Sets new value
    if field == 'username':
        target_user.username = value
    elif field == 'password':
        target_user.password = value
    elif field == 'email':
        target_user.email = value
    elif field == 'name':
        target_user.name = value
    elif field == 'surname':
        target_user.surname = value
    elif field == 'bio':
        target_user.bio = value
    elif field == 'isEmailPublic':
        target_user.public_email = value

    # Checks if changes are valid
    target_user.check(password=(field=='password'))

    # Hashes password
    if field == 'password':
        target_user.password = hash_password(value)

    # Tries to save changes
    try:
        target_user.save()
    except IntegrityError:
        db.session.rollback()
        raise APIErrors[230]

    return target_user.json()

@app.route('/communities', methods=['POST'])
@jwt_required
def create_community():
    """
    Create a new community and saves it in the database.
    """

    # Fetches the user from the database
    user = User.query.filter_by(id=get_jwt_identity()).first()

    # Asserts that the user is an admin
    if user.perms < 2:
        raise APIErrors[310]

    # Checks if the community is valid
    community = Community(name=get_from_body({'name': 330})[0])
    community.check()

    # Tries to save the community
    try:
        community.save()
    except IntegrityError:
        db.session.rollback()
        raise APIErrors[320]

    return community.json(), 201
