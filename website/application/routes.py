from . import app
from flask import render_template


@app.route('/')
def index():
    return render_template('layout.html', messaggio=['ciao', 'ciao2'])

@app.errorhandler(404)
def err404(_):
    return render_template('layout.html'),404