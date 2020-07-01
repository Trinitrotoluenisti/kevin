from . import app, tokens_age
from .api import api, check_token, APIError
from flask import render_template, request, make_response, redirect



# Others
app.errorhandler(404)(lambda *args: (render_template('/404.html', username=check_token()[1]), 404))
app.errorhandler(405)(lambda *args: (redirect('/'), 405))


# Home
@app.route('/')
def home():
    return render_template('home.html', username=check_token()[1])


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
@app.route('/users/<string:username>')
def view_user(username=''):
    accessToken, logged_username, response = check_token()

    # Fetch the user from the api
    if accessToken:
        user = api("get", "/users/" + username, auth=accessToken)
    else:
        user = api("get", "/users/" + username)

    # Create and return the response
    response.data = render_template('/user.html', username=logged_username, user=user, owner=(username == logged_username))    
    return response

# Posts
@app.route('/post')
def view_post():
    return render_template('post.html', username=check_token()[1])

@app.route('/create-post')
def create_post():
    if request.method == 'GET':
        # Check if the client is logged in
        accessToken, username, response = check_token()

        # (if tokens are not valid redirect to the index page and delete them)
        if not accessToken:
            return response

        response.data = render_template('create_post.html', username=username)

        # Return create_post.html
        return response
    elif request.method == 'POST':
        pass

# Settings
@app.route('/user/settings')
def settings():
    # Check if the client is logged in
    accessToken, username, response = check_token()

    # (if tokens are not valid redirect to the index page and delete them)
    if not accessToken:
        return response

    response.data = render_template('settings.html', username=username)

    # Return settings.html
    return response

@app.route('/user/settings/change-pw', methods=['POST'])
def change_pw():
    # Check if the client is logged in
    accessToken, username, response = check_token()

    # (if tokens are not valid redirect to the index page and delete them)
    if not accessToken:
        return response

    # Get username
    username = api('get', '/users/' + username, auth=accessToken)['username']
    oldPassword = request.form['opassword']
    newPassword = request.form['password']

    # Check old password
    try:
        api('post', '/login', data={'username': username, 'password': oldPassword})
    except APIError:
        return render_template("settings.html", alert='Wrong old password', username=username), 400

    api('put', f'/users/{username}/password', data={'value': newPassword}, auth=accessToken)

    return render_template("settings.html", username=username)

@app.route('/user/settings/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    # Check if the client is logged in
    accessToken, username, response = check_token()

    # (if tokens are not valid redirect to the index page and delete them)
    if not accessToken:
        return response

    if request.method == 'GET':
        user = api('get', '/users/' + username, auth=accessToken)

        response.data = render_template('edit_profile.html', username=username, user=user)

        # Return edit_profile.html
        return response
    elif request.method == 'POST':
        old = api('get', '/users/' + username, auth=accessToken)
        del old['perms'], old['id']

        new = dict(request.form)
        new['isEmailPublic'] = {'on': True, 'off': False}[new.get('isEmailPublic', 'off').lower()]

        changed = []

        for k, v in old.items():
            if new.get(k) != v:
                changed.append(k)

        for field in changed:
            api('put', f'/users/{username}/{field}', auth=accessToken, data={'value':new[field]})

        return redirect('/user/settings')

# Admin
@app.route('/admin')
def admin():
    # Check if the client is logged in
    accessToken, username, response = check_token()

    # (if tokens are not valid redirect to the index page and delete them)
    if not accessToken:
        return response

    user = api("get", f"/users/{username}", auth=accessToken)

    if user["perms"] >= 2:
        return render_template('admin/admin.html', username=username, user=user)
    else:
        return render_template('/home.html', username=username), 403
