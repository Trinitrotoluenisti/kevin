from flask import request

from . import jwt
from .models import RevokedTokens



@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Return True if the token has been revoked
    jti = decrypted_token['jti']
    return bool(RevokedTokens.query.filter_by(jti=jti).first())

def get_ip():
    # Return the ip of the client that made the request
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def get_from_body(*args):
    """
    Try to return the given arguments by looking for them
    in the request body.
    Can raise a ValueError (body isn't encoded in application/json)
    or a KeyError (field not found).
    """

    # Fetch the request's body
    body = request.get_json()

    # Raise a ValueError if it isn't encoded in application/json
    if not body:
        raise ValueError("Request's body is not in application/json")

    # Prepare the fields' list
    fields = []

    # Try to get every field
    for key in args:
        field = body[key]

        if not field:
            raise KeyError(key)

        fields.append(field)

    return fields
