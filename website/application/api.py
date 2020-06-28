from . import app, server, tokens_age

from flask import request, make_response, render_template, redirect
import requests



class APIError(Exception):
    """
    An error returned by the API
    """


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
    if not r.status_code in range(199, 300):
        json = r.json()
        raise APIError(json["error"], json["description"], json["code"], json["status"])

    if r.status_code != 204:
        return r.json()

def check_token():
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
        response.set_cookie('accessToken', access_token, max_age=tokens_age)
        return access_token, response

    # In all the other cases redirect to the home page and reset all cookies
    else:
        response = make_response(redirect("/", code=302))
        response.set_cookie('accessToken', "", expires=0)
        response.set_cookie('refreshToken', "", expires=0)
        return None, response

@app.errorhandler(APIError)
def handle_apierror(e):
    error, description, status, code = e.args
    message = f"{error.capitalize()}: description (E{code})"
    return render_template("home.html", alert=message), status
