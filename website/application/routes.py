from . import app, server
from flask import render_template, request, make_response, redirect
from requests import get, post


@app.route('/')
def home():
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
        r = post(server + "/login", data={"username": username, "password": password})

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
            return render_template('/home.html', alert=r.json()["msg"])


@app.route('/register', methods=["GET", "POST"])
def register():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('register.html', nav=False)

    # If it's POST...
    else:
        # fetch data
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # make a requets to the apis
        r = post(server + "/signup", data={"username": username, "password": password, 'email': email})

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
            return render_template('/home.html', alert=r.json()["msg"])

@app.errorhandler(404)
def error_404(e):
    return render_template('/404.html'), 404
