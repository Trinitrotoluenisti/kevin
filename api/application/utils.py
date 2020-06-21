from flask import request

from . import jwt
from .errors import ContentTypeError, MissingFieldError
from .models import RevokedTokens



@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Return True if the token has been revoked
    jti = decrypted_token['jti']
    return bool(RevokedTokens.query.filter_by(jti=jti).first())

def get_from_body(*args):
    """
    Try to return the given arguments by looking for them
    in the request body.
    The possible errors will be automatically handled.
    """

    # Fetch the request's body
    body = request.get_json()

    # Raise a ValueError if it isn't encoded in application/json
    if not body:
        raise ContentTypeError()

    # Try to get each field
    fields = []
    for key in args:
        if not key in body:
            raise MissingFieldError(key)

        fields.append(body[key])

    return fields
