from . import app, server
from flask import render_template, request, jsonify
from requests import get, post


#pagine standard
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
        username = request.form["user"]
        password = request.form["pass"]

        # make a requets to the apis
        r = post(server + "/login", data={"username": username, "password": password})

        # if it's ok, return the register
        if r.status_code == 200: 
            return render_template('/login.html', token=r.json()["token"])
        else: 
            return render_template('/home.html', alert=r.json()["msg"])


@app.route('/register', methods=["GET", "POST"])
def register():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('register.html')

    # If it's POST...
    else:
        # fetch data
        username = request.form["user"]
        email = request.form["mail"]
        password = request.form["pass"]

        # make a requets to the apis
        r = post(server + "/signup", data={"username": username, "password": password, 'email': email})

        # if it's ok, return the register
        if r.status_code == 200: 
            return render_template('/register.html', token=r.json()["token"])
        else: 
            return render_template('/home.html', alert=r.json()["msg"])


#pagine utenti loggati
@app.route('/settings')
def settings():
    return "Settings"

#pagine admin
@app.route('/admin')
def admin():
    return "da fare solo per gli amministratori"

#errori
@app.errorhandler(404)
def page_not_found(e):
    return "wewaglio se so fregati la pagina", 404

#roba tommy
@app.route('/tom')
def tommy():
    return render_template('geekia.html')
