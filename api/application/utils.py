from flask import request

from . import jwt
from . database import RevokedTokens


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return bool(RevokedTokens.query.filter_by(jti=jti).first())

def get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def get_from_body(*args):
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
        fields.append(field)

    return fields
