from . import app
from flask import render_template


@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/articolo')
def articolo():
    return render_template('articolo.html')
