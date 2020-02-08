from . import app, server
from flask import render_template, request, jsonify
from requests import get, post


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('login.html')

    # If it's POST...
    else:
        # fetch data
        username = request.form["username"]
        password = request.form["password"]

        # make a requets to the apis
        r = post(server + "/login", data={"username": username, "password": password})

        # if it's ok, return the register
        if r.status_code == 200: 
            return render_template('/login.html', token=r.json()["token"])
        else: 
            return render_template('/home.html', alert=r.json()["msg"])


@app.route('/signup', methods=["GET", "POST"])
def signup():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('signup.html')

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
            return render_template('/signup.html', token=r.json()["token"])
        else: 
            return render_template('/home.html', alert=r.json()["msg"])

@app.errorhandler(404)
def error_404(e):
    return render_template('/404.html'), 404
