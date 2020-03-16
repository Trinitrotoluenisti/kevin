from . import app, server
from flask import render_template, request, make_response, redirect, abort
from requests import get, post
import requests


@app.route('/')
def home():
    access_token = request.cookies.get('access_token')
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
            return redirect("/", code=302) #render_template('/home.html', alert=r.json()["msg"])


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
            return render_template('/home.html', alert=r.json()["msg"])

@app.route('/admin')
def admin():
    access_token = request.cookies.get('access_token')
    r= get(server + "/user", headers={"Authorization": "Bearer " + access_token})
    if r.status_code == 200:
        perms = r.json()["perms"]
        if perms >= 10:     #TODO: ricorda di cambiare il numero per il max perms (admin)
            return render_template('admin.html')
        else: 
            #return abort(404)
            return render_template('/home.html', alert=r.json()["msg"])
    else: 
        #return abort(404)
        return render_template('/home.html', alert=r.json()["msg"])

@app.errorhandler(404)
def error_404(e):
    return render_template('/404.html'), 404

@app.route('/post')
def post():
    return render_template('post.html')

@app.route('/create_post')
def create_post():
    return render_template('create_post.html')

@app.route('/view_user')
def view_user():
    username = request.args.get('username')
    r = get(server + "/user/" + username).json()
    if r.status_code == 200:
        user_data = r.json()
        return render_template('/view_user.html', user=user_data)
    else:
        return render_template('/home.html', alert=r.json()["msg"])

@app.route('/user')
def user():
    access_token = request.cookies.get('access_token')
    r = get(server + "/user", headers={"Authorization": "Bearer " + access_token})
    if r.status_code == 200:
        user_data = r.json()
        return render_template('/view_user.html', user=user_data)
    else:
        return render_template('/home.html', alert=r.json()["msg"])
