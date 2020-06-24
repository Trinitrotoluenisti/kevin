from . import app, tokens_age
from .api import api, check_token, APIError
from flask import render_template, request, make_response, redirect



# Others
@app.errorhandler(404)
def error_404(e):
    # Return 404 error page
    return render_template('/404.html'), 404


# Home
@app.route('/')
def home():
    # Return home.html
    return render_template('home.html')


# Login / Register / Logout
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
        persistent = bool(request.form.get("keep_logged", ""))

        # make a requets to the apis
        r = api("post", "/login", data={"username": username, "password": password})

        # set access token's cookie
        response = make_response(redirect("/", code=302))
        response.set_cookie('accessToken', r["accessToken"], max_age=tokens_age)

        # If "keep me logged in" was enabled, set the refresh token's expiration
        # for one month, otherwise it will expire once the session is closed
        if persistent:
            response.set_cookie('refreshToken', r["refreshToken"], max_age=2628000)
        else:
            response.set_cookie('refreshToken', r["refreshToken"])

        return response

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
        persistent = bool(request.form.get("keep_logged", ""))

        # build the user's dict
        user = {"username": username, "name": name, "surname": surname,
                "password": password, "email": email}

        # make a requets to the apis
        r = api("post", "/register", data=user)

        # set access token's cookie
        response = make_response(redirect("/", code=302))
        response.set_cookie('accessToken', r["accessToken"], max_age=tokens_age)

        # If "keep me logged in" was enabled, set the refresh token's expiration
        # for one month, otherwise it will expire once the session is closed
        if persistent:
            response.set_cookie('refreshToken', r["refreshToken"], max_age=2628000)
        else:
            response.set_cookie('refreshToken', r["refreshToken"])

        return response


@app.route('/logout', methods=["GET"])
def logout():
    # revoke access token
    access = request.cookies.get('accessToken')
    if access:
        try:
            api("delete", "/token/access", auth=access)
        except APIError:
            pass

    # revoke refresh token
    refresh = request.cookies.get('refreshToken')
    if refresh:
        try:
            api("delete", "/token/refresh", auth=refresh)
        except APIError:
            pass

    # Delete cookies
    response = make_response(redirect("/", code=302))
    response.set_cookie('accessToken', "", expires=0)
    response.set_cookie('refreshToken', "", expires=0)

    return response


# User
@app.route('/user')
@app.route('/user/<string:username>')
def user(username=''):
    # If a username is specified
    if username:
        # Try to return his profile
        user = api("get", "/users/" + username)
        return render_template('/user.html', user=user)

    # If there isn't an username
    else:
        # Check if the client is logged in
        accessToken, response = check_token()

        # (if tokens are not valid redirect to the index page and delete them)
        if not accessToken:
            return response

        # Return the user
        user = api("get", "/user", auth=accessToken)
        response.data = render_template('/user.html', user=user, owner=True)
        return response

# Posts
@app.route('/post')
def view_post():
    # Return post.html
    return render_template('post.html')

@app.route('/create-post')
def create_post():
    # Check if the client is logged in
    accessToken, response = check_token()

    # (if tokens are not valid redirect to the index page and delete them)
    if not accessToken:
        return response

    response.data = render_template('create_post.html')

    # Return create_post.html
    return response

# Settings
@app.route('/settings')
def settings():
    # Check if the client is logged in
    accessToken, response = check_token()

    # (if tokens are not valid redirect to the index page and delete them)
    if not accessToken:
        return response

    response.data = render_template('settings.html')

    # Return settings.html
    return response

@app.route('/settings/edit-user')
def edit_user():
    pass

# Admin
@app.route('/admin')
def admin():
    accessToken = request.cookies.get('accessToken')
    user = api("get", "/user", auth=accessToken)
    perms = user ["perms"]
    if perms >= 10:     #TODO: ricorda di cambiare il numero per il max perms (admin)
        return render_template('admin/admin.html', user=user)
    else:
        #return abort(404)
        return render_template('/home.html', alert="non hai permessi")
