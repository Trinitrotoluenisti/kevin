from . import app
from flask import render_template

#pagine standard
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return "webserver"

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


