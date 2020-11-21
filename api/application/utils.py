from flask import request

from . import jwt
from .errors import APIErrors
from .models import RevokedTokens



@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(token):
    """
    Returns true if the token has been revoked

    - token (dict): the decripted token
    """

    return bool(RevokedTokens.query.filter_by(jti=token['jti']).first())

def get_from_body(parameters):
    """
    Tries to return the given arguments by looking for them in the request body.

    - parameters (dict): a dict whose keys are fields' names and the values are
                         the codes of the errors to be raised if that field is not found

    It returns a list.
    """

    # Fetches the request's body
    body = request.get_json()

    # Checks Content-Type
    if not isinstance(body, dict):
        raise APIErrors[140]

    # Tries to get each field
    fields = []
    for field in parameters:
        if not field in body:
            raise APIErrors[parameters[field]]

        fields.append(body[field])

    return fields
