from flask_jwt_extended import *
from sqlalchemy.exc import IntegrityError

from . import db
from .models import *
from .utils import *
from .errors import APIErrors
from .passwords import hash_password



# UNPROTECTED
@app.route('/login', methods=['POST'])
def login():
    # Fetch request's body
    username, password = get_from_body({'username': 240, 'password': 250})

    # Check credentials
    user = User.query.filter_by(username=username).first()
    if not user or not user.password == hash_password(password):
        raise APIErrors[220]

    # Generate tokens
    access = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)

    return {"accessToken": access, "refreshToken": refresh}, 200

@app.route('/register', methods=['POST'])
def register():
    # Fetch request's body
    username, password, email, name, surname = get_from_body({'username': 240, 'password': 250, 'email': 260, 'name': 270, 'surname': 280})

    # Check if user is valid
    user = User(username=username, email=email, password=password, name=name, surname=surname, public_email=False, perms=0, bio='')
    user.check()

    # Try to add it in the database
    try:
        user.password = hash_password(password)
        user.save()
    except IntegrityError:
        db.session.rollback()
        raise APIErrors[230]

    # Generate the tokens
    access = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)

    return {"accessToken": access, "refreshToken": refresh}, 201

@app.route('/users/<string:username>')
def view_users(username):
    # If a username is specified, check if exists
    user = User.query.filter_by(username=username).first()
    if not user:
        raise APIErrors[200]

    user = user.json()

    # Check if user's email is public
    if not user["isEmailPublic"]:
        del user["email"]

    return user

@app.route('/communities')
@jwt_optional
def list_communities():
    # Get the list of communities
    communities = list(map(lambda c: c.json(), Community.query.all()))

    # If there is an authentication
    user_id = get_jwt_identity()
    if user_id:
        # Check if the user is following that community
        for community in communities:
            follows = Follow.query.filter_by(follower_id=user_id, community_id=community['id']).first()
            community['following'] = bool(follows)


    return {'communities': communities}

@app.route('/communities/<string:name>')
@jwt_optional
def get_communities(name):
    # Try to get the community
    community = Community.query.filter_by(name=name).first()

    # Return an error if it doesn't exists
    if not community:
        raise APIErrors[300]

    community = community.json()

    # If there is an authentication check if the user is following it
    user_id = get_jwt_identity()
    if user_id:
        follow = Follow.query.filter_by(follower_id=user_id, community_id=community['id']).first()
        community['following'] = bool(follow)


    return community


# PROTECTED
@app.route('/token', methods=['PUT'])
@jwt_refresh_token_required
def refresh_token():
    # Fetch data
    user_id = get_jwt_identity()

    # Return an ok message
    return {'accessToken': create_access_token(identity=user_id)}

@app.route('/token/access', methods=['DELETE'])
@jwt_required
def revoke_access_token():
    # Fetch data
    jti = get_raw_jwt()['jti']
    exp = get_raw_jwt()['exp']

    # Revoke token
    RevokedTokens(jti=jti, exp=exp).save()

    # Return an ok message
    return {}, 204

@app.route('/token/refresh', methods=['DELETE'])
@jwt_refresh_token_required
def revoke_refresh_token():
    # Fetch data
    jti = get_raw_jwt()['jti']

    # Revoke token
    RevokedTokens(jti=jti).save()

    # Return an ok message
    return {}, 204

@app.route('/user')
@jwt_required
def view_user():
    # Get the user from the database
    user = User.query.filter_by(id=get_jwt_identity()).first()

    return user.json()

@app.route('/user', methods=['DELETE'])
@jwt_required
def delete_user():
    # Get the user from the database and delete him
    user = User.query.filter_by(id=get_jwt_identity()).first()
    db.session.delete(user)
    db.session.commit()

    return {}, 204

@app.route('/user/<string:field>', methods=['PUT'])
@jwt_required
def edit_user(field):
    # Check if field is valid
    if not field in ('username', 'password', 'email', 'name', 'surname', 'bio', 'isEmailPublic'):
        raise APIErrors[100]

    # Get user and new value
    user = User.query.filter_by(id=get_jwt_identity()).first()
    error_codes = {'username': 240, 'password': 250, 'email': 260, 'isEmailPublic': 262, 'name': 270, 'surname': 280, 'bio': 290}
    value = get_from_body({'value': error_codes[field]})[0]

    # Set new value
    if field == 'username':
        user.username = value
    elif field == 'password':
        user.password = value
    elif field == 'email':
        user.email = value
    elif field == 'name':
        user.name = value
    elif field == 'surname':
        user.surname = value
    elif field == 'bio':
        user.bio = value
    elif field == 'isEmailPublic':
        user.public_email = value

    # Check if changes are valid
    user.check(password=(field == 'password'))

    # Try to save changes
    try:
        if field == 'password':
            user.password = hash_password(value)
        user.save()
    except IntegrityError:
        db.session.rollback()
        raise APIErrors[230]

    return user.json()

@app.route('/communities', methods=['POST'])
@jwt_required
def create_community():
    # Fetch the user from the dat
    user = User.query.filter_by(id=get_jwt_identity()).first()

    # Assert that the user is an admin
    if user.perms < 2:
        raise APIErrors[310]

    # Check if the community is valid
    community = Community(name=get_from_body({'name': 330})[0])
    community.check()

    # Try to save the community
    try:
        community.save()
    except IntegrityError:
        db.session.rollback()
        raise APIErrors[320]

    return community.json(), 201
