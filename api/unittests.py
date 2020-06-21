import unittest
from sys import argv

# Import app
argv.append('-t')
from application import app, db, User
argv.remove('-t')


class Test(unittest.TestCase):
    def setUp(self):
        # Create app
        self.app = app.test_client()

        # Recreate database
        db.drop_all()
        db.create_all()

        # Add a testing user
        self.user = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'password': 'password'}
        r = self.app.post('/register', json=self.user)

        # save tokens
        self.access = r.json['accessToken']
        self.refresh = r.json['refreshToken']

    def route(self, method, path, code, response, auth=None, body=None, ignored=()):
        # Add auth header if it exists
        if auth:
            auth = {'Authorization': f'Bearer {auth}'}

        # Make request
        if method.lower() == 'get':
            r = self.app.get(path, headers=auth)
        elif method.lower() == 'post':
            r = self.app.post(path, json=body, headers=auth)
        elif method.lower() == 'delete':
            r = self.app.delete(path, headers=auth)
        elif method.lower() == 'put':
            r = self.app.put(path, json=body, headers=auth)
        else:
            raise ValueError("Undefined method")

        # Check status code
        self.assertEqual(r.status_code, code)

        # If the expected response is None, check if the given is None
        if not response:
            self.assertFalse(r.data)
            return

        # Check body's keys
        self.assertEqual(set(r.json.keys()), set(response.keys()))

        # Compare pairs (and skip ignored ones)
        for key in response:
            if key not in ignored:
                self.assertEqual(r.json[key], response[key])

        return r.json

    def check_token(self, token, token_type, valid):
        code = 200 if valid else 401
        headers = {'Authorization': f'Bearer {token}'}

        if token_type == 'access':
            self.assertEqual(self.app.get("/user", headers=headers).status_code, code)
        elif token_type == 'refresh':
            self.assertEqual(self.app.put("/token", headers=headers).status_code, code)

    def test_login(self):
        # 400: Missing username
        request = {"password": "password"}
        response = {"error": "invalid request", "description": "Missing username"}
        self.route("post", "/login", 400, response, body=request)

        # 400: Missing password
        request = {"username": "elonmusk"}
        response = {"error": "invalid request", "description": "Missing password"}
        self.route("post", "/login", 400, response, body=request)

        # 401: Wrong username or password
        request = {"username": "elonmusk", "password": "password?"}
        response = {"error": "invalid login", "description": "Wrong username or password"}
        self.route("post", "/login", 401, response, body=request)

        # 200: Correct
        request = {"username": "elonmusk", "password": "password"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/login", 200, response, body=request, ignored=("accessToken", "refreshToken"))

        # Assert that the access and refresh token are valid
        self.check_token(json['accessToken'], 'access', True)
        self.check_token(json['refreshToken'], 'refresh', True)

    def test_register(self):
        # 400: Missing username
        request = {"name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "invalid request", "description": "Missing username"}
        self.route("post", "/register", 400, response, body=request)

        # 400: Username contains invalid character(s)
        request = {"username": "dent!", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "invalid user", "description": "Username contains invalid character(s)"}
        self.route("post", "/register", 400, response, body=request)

        # 400: Password too short
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "fenny"}
        response = {"error": "invalid user", "description": "Password too short"}
        self.route("post", "/register", 400, response, body=request)

        # 400: Email is not an email
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "sandwich!", "password": "ILoveFenchurch"}
        response = {"error": "invalid user", "description": "Email is not an email"}
        self.route("post", "/register", 400, response, body=request)

        # 409: Email already used
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "elon@tesla.com", "password": "ILoveFenchurch"}
        response = {"error": "user already exists", "description": "Some user's data have already been used"}
        self.route("post", "/register", 409, response, body=request)

        # 200: Correct user
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/register", 201, response, body=request, ignored=("accessToken", "refreshToken"))

        # Assert that the access and refresh token are valid
        self.check_token(json['accessToken'], 'access', True)
        self.check_token(json['refreshToken'], 'refresh', True)

    def test_refresh_token(self):
        # 422: Only refresh tokens are allowed
        response = {"error": "invalid token", 'description': 'Only refresh tokens are allowed'}
        self.route("put", "/token", 422, response, auth=self.access)

        # 200: Ok
        response = {"accessToken": ""}
        json = self.route("put", "/token", 200, response, auth=self.refresh, ignored=("accessToken"))

        # Assert that the access is valid
        self.check_token(json['accessToken'], 'access', True)

    def test_revoke_access_token(self):
        # 422: Only access tokens are allowed
        response = {"error": "invalid token", 'description': 'Only access tokens are allowed'}
        self.route("delete", "/token/access", 422, response, auth=self.refresh)

        # 204: No content
        self.route("delete", "/token/access", 204, {}, auth=self.access)

        # Assert that the access token isn't valid
        self.check_token(self.access, 'access', False)

    def test_revoke_refresh_token(self):
        # 422: Only refresh tokens are allowed
        response = {"error": "invalid token", 'description': 'Only refresh tokens are allowed'}
        self.route("delete", "/token/refresh", 422, response, auth=self.access)

        # 204: No content
        self.route("delete", "/token/refresh", 204, {}, auth=self.refresh)

        # Assert that the refresh token isn't valid
        self.check_token(self.refresh, 'refresh', False)
    
    def test_view_user(self):
        # 401: Unauthorized
        response = {"error": "unauthorized", 'description': 'Missing Authorization Header'}
        self.route("get", "/user", 401, response)

        # 422: Only access tokens are allowed
        response = {"error": "invalid token", 'description': 'Only access tokens are allowed'}
        self.route("get", "/user", 422, response, auth=self.refresh)

        # 200: Ok
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/user", 200, response, auth=self.access)

    def test_delete_user(self):
        # 401: Unauthorized
        response = {"error": "unauthorized", 'description': 'Missing Authorization Header'}
        self.route("delete", "/user", 401, response)

        # 204: No content
        self.route("delete", "/user", 204, {}, auth=self.access)

        self.assertFalse(User.query.filter_by(username='elonmusk').first())

    def test_edit_user(self):
        # 401: Unauthorized
        response = {"error": "unauthorized", 'description': 'Missing Authorization Header'}
        self.route("put", "/user/username", 401, response)

        # 404: Not found
        response = {"error": "not found", 'description': "The field to edit has not been found"}
        self.route("put", "/user/perms", 404, response, auth=self.access)

        User(username="TheSandwichMaker", email="arthurdent@gmail.com", password="ILoveFenchurch", name="Arthur", surname="Dent").save()

        # 409: Username already taken
        request = {"value": "TheSandwichMaker"}
        response = {"error": "user already exists", "description": "username has already been used"}
        self.route("put", "/user/username", 409, response, body=request, auth=self.access)
        
        # 200: Ok (username)
        request = {"value": "hpotter"}
        response = {'username': 'hpotter', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/user/username", 200, response, body=request, auth=self.access)

        # 200: Ok (password)
        request = {"value": "LordVoldemort"}
        response = {'username': 'hpotter', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/user/password", 200, response, body=request, auth=self.access)

        # 200: Ok (name)
        request = {"value": "Harry"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/user/name", 200, response, body=request, auth=self.access)

        # 200: Ok (surname)
        request = {"value": "Potter"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/user/surname", 200, response, body=request, auth=self.access)

        # 200: Ok (email)
        request = {"value": "harrypotter@hedwig.uk"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/user/email", 200, response, body=request, auth=self.access)

        # 200: Ok (bio)
        request = {"value": "Hey!\nThis is Harry Potter!"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': "Hey!\nThis is Harry Potter!", 'isEmailPublic': False}
        self.route("put", "/user/bio", 200, response, body=request, auth=self.access)

        # 200: Ok (isEmailPublic)
        request = {"value": True}
        response = {'username': 'hpotter', 'name':'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': "Hey!\nThis is Harry Potter!", 'isEmailPublic': True}
        self.route("put", "/user/isEmailPublic", 200, response, body=request, auth=self.access)

        # Try to login with new credentials
        request = {"username": "hpotter", "password": "LordVoldemort"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/login", 200, {'accessToken': '', 'refreshToken': ''}, body=request, ignored=("accessToken", "refreshToken"))

        # Check new infos
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': "Hey!\nThis is Harry Potter!", 'isEmailPublic': True}
        self.route("get", "/user", 200, response, auth=json['accessToken'])

    def test_view_users(self):
        # 404: Not Found
        response = {"error": "User does not exist", "description": "Can't find an user with that username"}
        self.route("get", "/users/spongebob", 404, response)

        # 200: Email NOT public
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/users/elonmusk", 200, response)

        user = User.query.filter_by(username='elonmusk').first()
        user.public_email = True
        user.save()

        # 200: Email public
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': True}
        self.route("get", "/users/elonmusk", 200, response)


if __name__ == "__main__":
    unittest.main()
