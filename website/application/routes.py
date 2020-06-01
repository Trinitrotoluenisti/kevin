from . import app, tokens_age
from .api import api, check_token, APIError

from flask import render_template, request, make_response, redirect



"""
Others
"""
@app.errorhandler(404)
def error_404(e):
    # Return 404 error page
    return render_template('/404.html'), 404


"""
Home
"""
@app.route('/')
def home():
    # Return home.html
    return render_template('home.html')


"""
Login / Register / Logout
"""
@app.route('/login', methods=["GET", "POST"])
def login():
    # Return the template if it's a GET request
    if request.method == "GET":
        return render_template('login.html', nav=False)

    # If it's a POST request
    else:
        # fetch data
        username = request.form["username"]
        password = request.form["password"]

        try:
            # make a requets to the apis
            r = api("post", "/login", data={"username": username, "password": password})

            # set cookies
            response = make_response(redirect("/", code=302))
            response.set_cookie('access_token', r["access_token"], max_age=tokens_age)
            response.set_cookie('refresh_token', r["refresh_token"])

            return response

        # If errors occourred, write them in an alert box
        except APIError as e:
            return render_template("login.html", alert=e.args[0], nav=False), e.args[1]

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

        # build the user's dict
        user = {"username": username, "name": name, "surname": surname,
                "password": password, "email": email}

        try:
            # make a requets to the apis
            r = api("post", "/register", data=user)

            # set cookies
            response = make_response(redirect("/", code=302))
            response.set_cookie('access_token', r["access_token"], max_age=tokens_age)
            response.set_cookie('refresh_token', r["refresh_token"])

            return response

        # If errors occourred, write them in an alert box
        except APIError as e:
            return render_template("register.html", alert=e.args[0], nav=False), e.args[1]

@app.route('/logout', methods=["GET"])
def logout():
    # revoke access token
    access = request.cookies.get('access_token')
    if access:
        api("post", "/logout/access", auth=access)

    # revoke refresh token
    refresh_token = request.cookies.get('refresh_token')
    if refresh:
        api("post", "/logout/refresh", auth=refresh)

    # Delete cookies
    response = make_response(redirect("/", code=302))
    response.set_cookie('access_token', "", expires=0)
    response.set_cookie('refresh_token', "", expires=0)

    return response


"""
User
"""
@app.route('/user')
def user():
    username = request.args.get('username', '')

    # If a username is specified
    if username:
        # Try to return his profile
        try:
            user = api("get", "/user/" + username)
            print(user)
            return render_template('/user.html', user=user)

        # (if errors are encountered it returns them in an alert box)
        except APIError as e:
            return render_template('/home.html', alert=e.args[0]), e.args[1]

    # If there isn't an username
    else:
        try:
            # Check if the client is logged in
            access_token, response = check_token()

            # (if tokens are not valid redirect to the index page and delete them)
            if not access_token:
                return response

            # Return the user
            user = api("get", "/user", auth=access_token)
            response.data = render_template('/user.html', user=user, owner=True)
            return response

        # (if errors are encountered it returns them in an alert box)
        except APIError as e:
            return render_template('/home.html', alert=e.args[0]), e.args[1]

"""
Posts
"""
@app.route('/post')
def view_post():
    # Return post.html
    return render_template('post.html')

@app.route('/create_post')
def create_post():
    # Return create_post.html
    return render_template('create_post.html')
