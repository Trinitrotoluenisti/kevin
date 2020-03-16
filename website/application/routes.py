from . import app, server
from flask import render_template, request, make_response, redirect, abort
from requests import get, post
import requests


@app.route('/')
def home():
    # Check if there is an access token
    access_token = request.cookies.get('access_token')

    # Return home.html
    if access_token:
        return render_template('home.html', logged_in=True)
    else:
        return render_template('home.html')

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
        r = requests.post(server + "/login", data={"username": username, "password": password})

        # if it's ok, return the register
        if r.status_code == 200:
            access = r.json()["access_token"]
            refresh = r.json()["refresh_token"]

            # set cookies
            response = make_response(redirect("/", code=302))
            response.set_cookie('access_token', access, httponly=True)
            response.set_cookie('refresh_token', refresh, httponly=True)

            return response
        else: 
            return redirect("/login", alert=r.json()["msg"]), r.status_code

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
        r = requests.post(server + "/register", data=user)

        # if it's ok, return the register
        if r.status_code == 200:
            access = r.json()["access_token"]
            refresh = r.json()["refresh_token"]

            # set cookies
            response = make_response(redirect("/", code=302))
            response.set_cookie('access_token', access, httponly=True)
            response.set_cookie('refresh_token', refresh, httponly=True)

            return response
        else: 
            return redirect("/register", alert=r.json()["msg"]), r.status_code

@app.route('/logout', methods=["GET"])
def logout():
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    # revoke access token
    requests.post(server + "/logout/access", headers={'Authorization': access_token})

    # revoke refresh token
    requests.post(server + "/logout/refresh", headers={'Authorization': refresh_token})

    # Create response
    response = make_response(redirect("/", code=302))
    response.set_cookie('access_token', "", httponly=True)
    response.set_cookie('refresh_token', "", httponly=True)

    # Return to home
    return response

@app.errorhandler(404)
def error_404(e):
    # Return 404 error page
    return render_template('/404.html'), 404

@app.route('/post')
def post():
    # Return post.html
    return render_template('post.html')

@app.route('/create_post')
def create_post():
    # Return create_post.html
    return render_template('create_post.html')

@app.route('/view_user')
def view_user():
    # Get user's data
    username = request.args.get('username')
    r = get(server + "/user/" + username)

    # Return view_user.html if it worked
    if r.status_code == 200:
        user_data = r.json()
        return render_template('/view_user.html', user=user_data)

    # If it didn't, return an error in home.html
    else:
        return render_template('/home.html', alert=r.json()["msg"]), r.status_code

@app.route('/user')
def user():
    # Get user's data
    access_token = request.cookies.get('access_token')
    r = get(server + "/user", headers={"Authorization": "Bearer " + access_token})

    # Return view_user.html if it worked
    if r.status_code == 200:
        user_data = r.json()
        return render_template('/view_user.html', user=user_data)

    # If it didn't, return an error in home.html
    else:
        return render_template('/home.html', alert=r.json()["msg"])
