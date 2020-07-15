from flask import request

from . import jwt
from .errors import APIErrors
from .models import RevokedTokens



@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Return True if the token has been revoked
    jti = decrypted_token['jti']
    return bool(RevokedTokens.query.filter_by(jti=jti).first())

def get_from_body(parameters):
    """
    Try to return the given arguments by looking for them in the request body.

    parameters must be a dict where the keys are the fields' names,
    the values are the codes of the error to be raised if the field is not found
    """

    # Fetch the request's body
    body = request.get_json()

    # Check Content-Type
    if not isinstance(body, dict):
        raise APIErrors[140]

    # Try to get each field
    fields = []
    for field in parameters:
        if not field in body:
            raise APIErrors[parameters[field]]

        fields.append(body[field])

    return fields
