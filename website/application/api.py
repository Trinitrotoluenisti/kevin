from . import server, tokens_age

from flask import request, make_response
import requests


def api(method, path, data={}, auth=''):
    # Build headers
    headers = {}
    headers["X-Forwarded-For"] = request.remote_addr
    if auth:
        headers["Authorization"] = f"Bearer {auth}"

    # Make the request (raise KeyError if the method is unknown)
    try:
        r = requests.__dict__[method](server + path, json=data, headers=headers)
    except KeyError:
        raise KeyError("Unknown method")

    # If the code isn't 200 (ok), raise an APIError
    if not r.status_code == 200:
        raise APIError(r.json()['msg'], r.status_code)

    # Otherwise return the body of the response formatted as json
    return r.json()

def check_token():
    # Create a blank response
    response = make_response()

    # Fetch access and refresh tokens
    access_token = request.cookies.get('accesToken')
    refresh_token = request.cookies.get('refreshToken')

    # If there are both, return access token and a blank response
    if access_token and refresh_token:
        return access_token, response

    # If there is only the refresh token, generate a new access
    # token and return it with a blank response that sets the cookie
    elif refresh_token:
        access_token = api("put", "/token", auth=refresh_token)['accessToken']
        response.set_cookie('accessToken', access_token, expires=tokens_age)
        return access_token, response

    # In all the other cases redirect to the home page and reset all cookies
    else:
        response.data = redirect("/", code=302)
        response.set_cookie('accessToken', "", expires=0)
        response.set_cookie('refreshToken', "", expires=0)
        return None, response

class APIError(Exception):
    """
    An error returned by the API
    """
