from . import app, server
from flask import render_template, request, make_response, redirect, abort
from requests import get, post



def api(method, path, data={}, headers={}):
    headers["X-Forwarded-For"] = request.remote_addr

    if method == "GET":
        return get(server + path, data=data, headers=headers)
    elif method == "POST":
        return post(server + path, data=data, headers=headers)
    else:
        raise ValueError("Method not known")

def check_token():
    response = make_response()

    # Get token
    access_token = request.cookies.get('access_token')
    request = api("GET", "/user", headers={"Authorization": "Bearer " + access_token})

    # Check if token has expired
    if request.status_code == 401 and request.json()["msg"] == "Token has expired":
        # If it has, create a new access token and return it
        refresh_token = request.cookies.get('refresh_token')
        request = api("POST", "/refresh", headers={"Authorization": "Bearer " + refresh_token})

        # Edit access token and response
        access_token = request.json()['access_token']
        response.set_cookie('access_token', access_token)

    return access_token, request


"""
Others
"""
@app.errorhandler(404)
def error_404(e):
    # Return 404 error page
    return render_template('/404.html'), 404


"""
Home
"""
@app.route('/')
def home():
    # Return home.html
    return render_template('home.html')


"""
Login / Register / Logout
"""
@app.route('/login', methods=["GET", "POST"])
def login():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('login.html', nav=False)

    # If it's POST...
    else:
        # fetch data
        username = request.form["username"]
        password = request.form["password"]

        # make a requets to the apis
        request = api("POST", "/login", data={"username": username, "password": password})

        # if it's ok, return the register
        if request.status_code == 200:
            access = request.json()["access_token"]
            refresh = request.json()["refresh_token"]

            # set cookies
            response = make_response(redirect("/", code=302))
            response.set_cookie('access_token', access)
            response.set_cookie('refresh_token', refresh)

            return response
        else: 
            return render_template("login.html", alert=r.json()["msg"]), request.status_code

@app.route('/register', methods=["GET", "POST"])
def register():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('register.html', nav=False)

    # If it's POST...
    else:
        # fetch data
        username = request.form["username"]
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        password = request.form["password"]

        user = {"username": username, "name": name, "surname": surname,
                "password": password, "email": email}

        # make a requets to the apis
        request = api("POST", "/register", data=user)

        # if it's ok, return the register
        if request.status_code == 200:
            access = request.json()["access_token"]
            refresh = request.json()["refresh_token"]

            # set cookies
            response = make_response(redirect("/", code=302))
            response.set_cookie('access_token', access)
            response.set_cookie('refresh_token', refresh)

            return response
        else: 
            return render_template("register.html", alert=r.json()["msg"]), response.status_code

@app.route('/logout', methods=["GET"])
def logout():
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    # revoke access token
    api("POST", "/logout/access", headers={'Authorization': 'Bearer ' + access_token})

    # revoke refresh token
    api("POST", "/logout/refresh", headers={'Authorization': 'Bearer ' + refresh_token})

    # Delete cookies
    response = make_response(redirect("/", code=302))
    response.set_cookie('access_token', "", expires=0)
    response.set_cookie('refresh_token', "", expires=0)

    # Return to home
    return response


"""
User
"""
@app.route('/view_user')
def view_user():
    # Get user's data
    username = request.args.get('username', '')
    request = api("GET", "/user/" + username)

    # Return view_user.html if it worked
    if request.status_code == 200:
        user_data = request.json()
        return render_template('/view_user.html', user=user_data)

    # If it didn't, return an error in home.html
    else:
        return render_template('/home.html', alert=r.json()["msg"]), request.status_code

@app.route('/user')
def user():
    # Check the token
    access_token, response = check_token()

    request = api("GET", "/user", headers={"Authorization": "Bearer " + access_token})

    # Return view_user.html if it worked
    if request.status_code == 200:
        user_data = request.json()
        response.data = render_template('/user.html', user=user_data)

    # If it didn't, return an error in home.html
    else:
        response.data = render_template('/home.html', alert=request.json()["msg"])
        response.code = request.status_code
    
    return response


"""
Posts
"""
@app.route('/post')
def view_post():
    # Return post.html
    return render_template('post.html')

@app.route('/create_post')
def create_post():
    # Return create_post.html
    return render_template('create_post.html')
