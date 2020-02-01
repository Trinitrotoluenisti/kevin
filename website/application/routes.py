from . import app
from flask import render_template


@app.route('/')
def index():
    with open('application/templates/content1.html') as f:
        content = f.read()

    return render_template('layout.html', content=content)
