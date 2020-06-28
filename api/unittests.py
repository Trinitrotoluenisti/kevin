import unittest
from sys import argv

# Import app
argv.append('-t')
from application import app, db, User, Community, Follow
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
        headers = {'Authorization': f'Bearer {token}'}

        if token_type == 'access' and valid:
            self.assertEqual(self.app.get("/user", headers=headers).status_code, 200)
        elif token_type == 'access':
            self.assertNotEqual(self.app.get("/user", headers=headers).status_code, 200)
        elif token_type == 'refresh' and valid:
            self.assertEqual(self.app.put("/token", headers=headers).status_code, 200)
        elif token_type == 'refresh':
            self.assertNotEqual(self.app.put("/token", headers=headers).status_code, 200)

    def test_error_handlers(self):
        # 400: Invalid content type
        request = "Hello, it's me"
        response = {"error": "Invalid Content-Type", "description": "The Content-Type header must be set to application/json", "id": 140, "status": 400}
        self.route('post', '/register', 400, response, body=request)

        # 404: Not found
        response = {"error": "Resource not found","description": "The resource you were looking for hasn't been found","id": 100,"status": 404}
        self.route('post', '/nil', 404, response)

        # 405: Method not allowed
        response = {"error": "Method not allowed","description": "The resource you were looking for doesn't allow that method","id": 110,"status": 405}
        self.route('get', '/login', 405, response)

    def test_login(self):
        # 400: Missing username
        request = {"password": "password"}
        response = {"error": "Missing username", "description": "Missing username field in request's body", "id": 240, "status": 400}
        self.route("post", "/login", 400, response, body=request)

        # 400: Missing password
        request = {"username": "elonmusk"}
        response = {"error": "Missing password", "description": "Missing password field in request's body", "id": 250, "status": 400}
        self.route("post", "/login", 400, response, body=request)

        # 401: Wrong username or password
        request = {"username": "elonmusk", "password": "password?"}
        response = {"error": "Wrong username or password", "description": "The username and/or password are wrong", "id": 220, "status": 401}
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
        response = {"error": "Missing username", "description": "Missing username field in request's body", "id": 240, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Username contains invalid character(s)
        request = {"username": "dent!", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "username contains invalid character(s)", "description": "username can only contain characters in ranges A-Z, a-z, 0-9, _", "id": 243, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Username too short
        request = {"username": "a", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "username too short", "description": "username must be at least 5 characters long", "id": 241, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Username too long
        request = {"username": "globglowgabgalabglobw", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "username too long", "description": "username can't be longer than 20 characters", "id": 242, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Password too short
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "fenny"}
        response = {"error": "password too short", "description": "password must be at least 8 characters long", "id": 251, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Password too long
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "gfhdnfhcndjsmckvhfngorithgnfithguryt"}
        response = {"error": "password too long", "description": "password can't be longer than 35 characters", "id": 252, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Password contains invalid character(s)
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurchà"}
        response = {"error": "password contains invalid character(s)", "description": "password can only contain characters in the ASCII table", "id": 253, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Email is not an email
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "sandwich!", "password": "ILoveFenchurch"}
        response = {"error": "email is not an email", "description": "email field must contain a valid email", "id": 261, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Name too short
        request = {"username": "TheSandwichMaker", "name": "A", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "name too short", "description": "name must be at least 2 characters long", "id": 271, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Name too long
        request = {"username": "TheSandwichMaker", "name": "Aaaaaaaaarthurrr", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "name too long", "description": "name can't be longer than 15 characters", "id": 272, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Surname too short
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "D", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "surname too short", "description": "surname must be at least 2 characters long", "id": 281, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 400: Surname too long
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Deeeeeeeeeeeeent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"error": "surname too long", "description": "surname can't be longer than 15 characters", "id": 282, "status": 400}
        self.route("post", "/register", 400, response, body=request)

        # 409: Email already used
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "elon@tesla.com", "password": "ILoveFenchurch"}
        response = {"error": "User already exist", "description": "Some user's data has already been used", "id": 230, "status": 409}
        self.route("post", "/register", 409, response, body=request)

        # 200: Valid user
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/register", 201, response, body=request, ignored=("accessToken", "refreshToken"))

        # Assert that the access and refresh token are valid
        self.check_token(json['accessToken'], 'access', True)
        self.check_token(json['refreshToken'], 'refresh', True)

    def test_refresh_token(self):
        # 200: Ok
        response = {"accessToken": ""}
        json = self.route("put", "/token", 200, response, auth=self.refresh, ignored=("accessToken"))

        # Assert that the access is valid
        self.check_token(json['accessToken'], 'access', True)

    def test_revoke_access_token(self):
        # 204: No content
        self.route("delete", "/token/access", 204, {}, auth=self.access)

        # Assert that the access token isn't valid
        self.check_token(self.access, 'access', False)

    def test_revoke_refresh_token(self):
        # 204: No content
        self.route("delete", "/token/refresh", 204, {}, auth=self.refresh)

        # Assert that the refresh token isn't valid
        self.check_token(self.refresh, 'refresh', False)

    def test_view_user(self):
        # 401: Unauthorized
        response = {"error": "Missing Authorization Header", "description": "The resource you were looking for needs a token to work", "id": 120, "status": 401}
        self.route("get", "/user", 401, response)

        # 200: Ok
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/user", 200, response, auth=self.access)

    def test_delete_user(self):
        # 401: Unauthorized
        response = {"error": "Missing Authorization Header", "description": "The resource you were looking for needs a token to work", "id": 120, "status": 401}
        self.route("delete", "/user", 401, response)

        # 204: No content
        self.route("delete", "/user", 204, {}, auth=self.access)

        self.assertFalse(User.query.filter_by(username='elonmusk').first())

    def test_edit_user(self):
        # 401: Unauthorized
        response = {"error": "Missing Authorization Header", "description": "The resource you were looking for needs a token to work", "id": 120, "status": 401}
        self.route("put", "/user/username", 401, response)

        # 404: Not found
        response = {"error": "Resource not found", "description": "The resource you were looking for hasn't been found", "id": 100, "status": 404}
        self.route("put", "/user/perms", 404, response, auth=self.access)

        User(username="TheSandwichMaker", email="arthurdent@gmail.com", password="ILoveFenchurch", name="Arthur", surname="Dent").save()

        # 409: Username already taken
        request = {"value": "TheSandwichMaker"}
        response = {"error": "User already exist", "description": "Some user's data has already been used", "id": 230, "status": 409}
        self.route("put", "/user/username", 409, response, body=request, auth=self.access)
    

        # 400: isEmailPublic is not a bool
        request = {"value": "TheSandwichMaker"}
        response = {"error": "isEmailPublic is not a bool", "description": "isEmailPublic must be a boolean", "id": 263, "status": 400}
        self.route("put", "/user/isEmailPublic", 400, response, body=request, auth=self.access)


        # 400: Bio too long
        request = {"value": "a" * 201}
        response = {"error": "bio too long", "description": "bio can't be longer than 200 characters", "id": 291, "status": 400}
        self.route("put", "/user/bio", 400, response, body=request, auth=self.access)

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
        response = {"error": "User does not exist", "description": "Couldn't find an user with that username", "id": 200, "status": 404}
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

    def test_get_communities(self):
        Community(name='ScienceThings').save()

        # 200: A community
        response = {'communities': [{'name': 'ScienceThings', 'id': 1}]}
        self.route('get', '/communities', 200, response)

        # 200: Logged in but not following
        response = {'communities': [{'name': 'ScienceThings', 'id': 1, 'following': False}]}
        self.route('get', '/communities', 200, response, auth=self.access)

        Follow(follower_id=1, community_id=1).save()

        # 200: Logged in and following
        response = {'communities': [{'name': 'ScienceThings', 'id': 1, 'following': True}]}
        self.route('get', '/communities', 200, response, auth=self.access)

    def test_create_community(self):
        # 403: Forbidden
        response = {"error": "Can't create community", "description": "You have to be logged in as an admin to do that", "id": 310, "status": 403}
        self.route('post', '/communities', 403, response, auth=self.access)

        user = User.query.filter_by(id=1).first()
        user.perms = 2
        user.save()

        # 400: Name too short
        request = {"name": "AMA"}
        response = {"error": "name too short", "description": "name must be at least 5 characters long", "id": 331, "status": 400}
        self.route('post', '/communities', 400, response, body=request, auth=self.access)

        # 400: Name too long
        request = {"name": "AMAMAMAMAMAMAMAMAMAMA"}
        response = {"error": "name too long", "description": "name can't be longer than 20 characters", "id": 332, "status": 400}
        self.route('post', '/communities', 400, response, body=request, auth=self.access)

        # 400: Name contains invalid character(s)
        request = {"name": "AMALAPIZZA!"}
        response = {"error": "name contains invalid character(s)", "description": "username can only contain characters in ranges A-Z, a-z, 0-9, _", "id": 333, "status": 400}
        self.route('post', '/communities', 400, response, body=request, auth=self.access)

        # 201: Created
        request = {"name": "ScienceThings"}
        response = {"name": "ScienceThings", "id": 1}
        self.route('post', '/communities', 201, response, body=request, auth=self.access)

        # 409: Conflict
        request = {"name": "ScienceThings"}
        response = {"error": "Community already exists", "description": "Some community's data has already been used", "id": 320, "status": 409}
        self.route('post', '/communities', 409, response, body=request, auth=self.access)

    def test_get_community(self):
        # 404: Not found
        response = {"error": "Community does not exist", "description": "Couldn't find a community with that name", "id": 300, "status": 404}
        self.route('get', '/communities/ScienceThings', 404, response)

        Community(name='ScienceThings').save()

        # 200: Found
        response = {'name': 'ScienceThings', 'id': 1}
        self.route('get', '/communities/ScienceThings', 200, response)

        # 200: Logged in but not following
        response = {'name': 'ScienceThings', 'id': 1, 'following': False}
        self.route('get', '/communities/ScienceThings', 200, response, auth=self.access)

        Follow(follower_id=1, community_id=1).save()

        # 200: Logged in and following
        response = {'name': 'ScienceThings', 'id': 1, 'following': True}
        self.route('get', '/communities/ScienceThings', 200, response, auth=self.access)

if __name__ == "__main__":
    unittest.main()
