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
    
    def route(self, method, path, code, response, auth=None, body=None, ignored=[]):
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
            r = self.app.put(path, headers=auth)
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

    def check_token(self, token, type, valid):
        code = 200 if valid else 401
        headers = {'Authorization': f'Bearer {token}'}

        if type == 'access':
            self.assertEqual(self.app.get("/user", headers=headers).status_code, code)
        elif type == 'refresh':
            self.assertEqual(self.app.put("/token", headers=headers).status_code, code)

    def test_login(self):
        # 400: Missing username
        request = {"password": "password", "username": ""}
        response = {"error": "invalid login", "description": "Missing user's username"}
        self.route("post", "/login", 400, response, body=request)

        # 400: Missing password
        request = {"username": "elonmusk", "password": ""}
        response = {"error": "invalid login", "description": "Missing user's password"}
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
        response = {"error": "invalid user", "description": "Missing user's username"}
        self.route("post", "/register", 400, response, body=request)

        # 400: Username too short
        request = {"username": "dent", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "invalid user", "description": "User's username is too short"}
        self.route("post", "/register", 400, response, body=request)

        # 400: Password too short
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "fenny"}
        response = {"error": "invalid user", "description": "User's password is too short"}
        self.route("post", "/register", 400, response, body=request)

        # 400: Email is not an email
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "sandwich!", "password": "ILoveFenchurch"}
        response = {"error": "invalid user", "description": "User's email is not an email"}
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

    def test_token_refresh(self):
        # 422: Only refresh tokens are allowed
        response = {"error": "invalid token", 'description': 'Only refresh tokens are allowed'}
        self.route("put", "/token", 422, response, auth=self.access)

        # 200: Ok
        response = {"accessToken": ""}
        json = self.route("put", "/token", 200, response, auth=self.refresh, ignored=("accessToken"))

        # Assert that the access is valid
        self.check_token(json['accessToken'], 'access', True)

    def test_token_revoke_access(self):
        # 422: Only access tokens are allowed
        response = {"error": "invalid token", 'description': 'Only access tokens are allowed'}
        self.route("delete", "/token/access", 422, response, auth=self.refresh)

        # 204: No content
        self.route("delete", "/token/access", 204, {}, auth=self.access)

        # Assert that the access token isn't valid
        self.check_token(self.access, 'access', False)

    def test_token_revoke_refresh(self):
        # 422: Only refresh tokens are allowed
        response = {"error": "invalid token", 'description': 'Only refresh tokens are allowed'}
        self.route("delete", "/token/refresh", 422, response, auth=self.access)

        # 204: No content
        self.route("delete", "/token/refresh", 204, {}, auth=self.refresh)

        # Assert that the refresh token isn't valid
        self.check_token(self.refresh, 'refresh', False)

    def test_user_view(self):
        # 401: Only access tokens are allowed
        response = {"error": "unauthorized", 'description': 'Missing Authorization Header'}
        self.route("get", "/user", 401, response)

        # 422: Only access tokens are allowed
        response = {"error": "invalid token", 'description': 'Only access tokens are allowed'}
        self.route("get", "/user", 422, response, auth=self.refresh)

        # 200: Ok
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/user", 200, response, auth=self.access)

    def test_users_view(self):
        # 404: Not Found
        response = {"error": "User does not exist", "description": "Can't find an user with that username"}
        self.route("get", "/users/spongebob", 404, response)

        # 200: Email NOT public
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/users/elonmusk", 200, response)

        user = User.query.filter_by(username='elonmusk').first()
        user.public_email = True
        db.session.commit()

        # 200: Email public
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': True}
        self.route("get", "/users/elonmusk", 200, response)


if __name__ == "__main__":
    unittest.main()
