import requests
from flask import request, make_response, render_template, redirect

from . import app, server



class APIError(Exception):
    """
    An error returned by the APIs.
    It is automatically handled, don't worry.    
    """

@app.errorhandler(APIError)
def handle_apierror(e):
    id, error, description, status = e.args
    message = f"{error.capitalize()}: {description} (E{id})"
    return render_template("home.html", alert=message), status


def api(method, path, data={}, auth=''):
    """
    Makes a request at the APIs.
    
    - method (str): "get", "post", "put", "delete"
    - path (str): the endpoint's path. It must start with the '/'.
    - data (dict): the request's data
    - auth (str): the access or the refresh token
    """

    # Sets headers
    headers = {}
    headers["X-Forwarded-For"] = request.remote_addr
    if auth:
        headers["Authorization"] = f"Bearer {auth}"

    # Makes the request
    r = requests.__dict__[method](server + path, json=data, headers=headers)

    # If the response's status code isn't a 2XX raise an APIError
    if not r.status_code in range(199, 300):
        json = r.json()
        raise APIError(json["id"],json["error"], json["description"], json["status"])

    return r.json() if r.text else {}

def get_credentials():
    """
    Returns the access token and the username.
    
    If it finds both the tokens, it returns the access
    token as it is.
    If it finds only the refresh token, it generates
    a new access token and returns it.
    If it finds only the access token, it deletes it.

    Returns:
    - access_token (str or None)
    - username (str or None)
    - response (flask.Response)

    """

    # Creates an empty response
    response = make_response()

    # Fetches access and refresh tokens
    access_token = request.cookies.get('accessToken')
    refresh_token = request.cookies.get('refreshToken')

    # If there are both, returns the token as it is
    if access_token and refresh_token:
        username = api('get', '/token', auth=access_token)['username']
        return access_token, username, response

    # If there is only the refresh token, it generates a new one access
    elif refresh_token:
        access_token = api("put", "/token", auth=refresh_token)['accessToken']
        response.set_cookie('accessToken', access_token, max_age=2700)
        username = api('get', '/token', auth=access_token)['username']
        return access_token, username, response

    # In all the other cases redirect to the home page and reset all cookies
    else:
        response.set_cookie('accessToken', '', expires=0)
        response.set_cookie('refreshToken', '', expires=0)
        return None, None, response
