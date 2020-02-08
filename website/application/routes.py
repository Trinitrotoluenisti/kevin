from . import app, server
from flask import render_template, request, jsonify
from requests import get, post

#pagine standard
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form["user"]
        password = request.form["pass"]
        r = post(server+"/login", data={"username": username, "password": password})
        if r.status_code==200: 
            return render_template('/login.html', token=r.json()["token"])
        else: 
            return render_template('/home.html', alert=r.json()["message"])

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



@app.route('/tom')
def tommy():
    return render_template('geekia.html')


