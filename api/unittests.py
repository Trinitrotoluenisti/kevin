import unittest
from os import environ


# Assert that the TESTING variable is set to True
old_testing = bool(environ.get('TESTING'))
if not old_testing:
    environ['TESTING'] = 'true'

from application import *


class Test(unittest.TestCase):
    def setUp(self):
        # Create app
        self.app = app.test_client()

        # Recreate database
        db.drop_all()
        db.create_all()

        # Create things
        User(username="elonmusk", email="elon@tesla.com", password=hash_password("password"), name="Elon", surname="Musk").save()
        User(username="therock", email="therock@hollywood.com", password=hash_password("password"), name="Dwayne", surname="Johnson", perms=2).save()
        Community(name="ScienceThings").save()

    def login(self, username='elonmusk', password='password'):
        user = {'username': username, 'password': password}
        r = self.app.post('/login', json=user)

        self.assertEqual(r.status_code, 200)

        return r.json['accessToken'], r.json['refreshToken']

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

        if token_type == 'access':
            self.assertEqual(self.app.get("/token", headers=headers).status_code == 200, valid)
        elif token_type == 'refresh':
            self.assertEqual(self.app.put("/token", headers=headers).status_code == 200, valid)

    def test_error_handlers(self):
        # E100: Resource not found
        response = APIErrors[100].json()
        self.route('post', '/nil', 404, response)

        # E110: Method not allowed
        response = APIErrors[110].json()
        self.route('get', '/login', 405, response)

        # E120: Missing Authorization Header
        response = APIErrors[120].json()
        self.route("get", "/token", 401, response)

        # E140: Invalid Content-Type
        request = "Hello, it's me"
        response = APIErrors[140].json()
        self.route('post', '/register', 400, response, body=request)

    def test_login(self):
        # E240: Missing username
        request = {"password": "password"}
        response = APIErrors[240].json()
        self.route("post", "/login", 400, response, body=request)

        # E250: Missing password
        request = {"username": "elonmusk"}
        response = APIErrors[250].json()
        self.route("post", "/login", 400, response, body=request)

        # E220: Wrong username or password
        request = {"username": "elonmusk", "password": "password?"}
        response = APIErrors[220].json()
        self.route("post", "/login", 401, response, body=request)

        # OK: Valid credentials
        request = {"username": "elonmusk", "password": "password"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/login", 200, response, body=request, ignored=("accessToken", "refreshToken"))

        # (assert that the access and refresh token are valid)
        self.check_token(json['accessToken'], 'access', True)
        self.check_token(json['refreshToken'], 'refresh', True)

    def test_register(self):
        # Users from the Hitchhiker's Guide to the Galaxy

        # E240: Missing username
        request = {"name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[240].json()
        self.route("post", "/register", 400, response, body=request)

        # E241: username too short
        request = {"username": "a", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[241].json()
        self.route("post", "/register", 400, response, body=request)

        # E242: username too long
        request = {"username": "globglowgabgalabglobw", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[242].json()
        self.route("post", "/register", 400, response, body=request)

        # E243: username contains invalid character(s)
        request = {"username": "dent!", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[243].json()
        self.route("post", "/register", 400, response, body=request)

        # E251: password too short
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "fenny"}
        response = APIErrors[251].json()
        self.route("post", "/register", 400, response, body=request)

        # E252: password too long
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "gfhdnfhcndjsmckvhfngorithgnfithguryt"}
        response = APIErrors[252].json()
        self.route("post", "/register", 400, response, body=request)

        # E253: password contains invalid character(s)
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurchà"}
        response = APIErrors[253].json()
        self.route("post", "/register", 400, response, body=request)

        # E261: email is not an email
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "sandwich!", "password": "ILoveFenchurch"}
        response = APIErrors[261].json()
        self.route("post", "/register", 400, response, body=request)

        # E271: name too short
        request = {"username": "TheSandwichMaker", "name": "A", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[271].json()
        self.route("post", "/register", 400, response, body=request)

        # E272: name too long
        request = {"username": "TheSandwichMaker", "name": "Aaaaaaaaarthurrr", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[272].json()
        self.route("post", "/register", 400, response, body=request)

        # E281: surname too short
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "D", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[281].json()
        self.route("post", "/register", 400, response, body=request)

        # E282: surname too long
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Deeeeeeeeeeeeent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = APIErrors[282].json()
        self.route("post", "/register", 400, response, body=request)

        # E230: User already exist
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "elon@tesla.com", "password": "ILoveFenchurch"}
        response = APIErrors[230].json()
        self.route("post", "/register", 409, response, body=request)

        # OK: Valid user
        request = {"username": "TheSandwichMaker", "name": "Arthur", "surname": "Dent", "email": "arthurdent@gmail.com", "password": "ILoveFenchurch"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/register", 201, response, body=request, ignored=("accessToken", "refreshToken"))

        # (assert that the access and refresh token are valid)
        self.check_token(json['accessToken'], 'access', True)
        self.check_token(json['refreshToken'], 'refresh', True)

    def test_refresh_token(self):
        access_token = self.login()[1]

        # E120: Missing Authorization Header
        response = APIErrors[120].json()
        self.route("put", "/token", 401, response)

        # OK: Created
        response = {"accessToken": ""}
        json = self.route("put", "/token", 200, response, auth=access_token, ignored=("accessToken"))

        # (assert that the access is valid)
        self.check_token(json['accessToken'], 'access', True)

    def test_view_token(self):
        access_token = self.login()[0]

        # E120: Missing Authorization Header
        response = APIErrors[120].json()
        self.route("get", "/token", 401, response)

        # OK: Gotten
        response = {'username': 'elonmusk'}
        self.route("get", "/token", 200, response, auth=access_token)

    def test_revoke_access_token(self):
        access_token = self.login()[0]

        # E120: Missing Authorization Header
        response = APIErrors[120].json()
        self.route("delete", "/token/access", 401, response)

        # OK: Revoked
        self.route("delete", "/token/access", 204, {}, auth=access_token)

        # (assert that the access token isn't valid)
        self.check_token(access_token, 'access', False)

    def test_revoke_refresh_token(self):
        refresh_token = self.login()[1]

        # E120: Missing Authorization Header
        response = APIErrors[120].json()
        self.route("delete", "/token/access", 401, response)

        # OK: Revoked
        self.route("delete", "/token/refresh", 204, {}, auth=refresh_token)

        # (assert that the refresh token isn't valid)
        self.check_token(refresh_token, 'refresh', False)

    def test_view_user(self):
        access_token = self.login()[0]

        # E200: User does not exist
        response = APIErrors[200].json()
        self.route("get", "/users/spongebob", 404, response)

        # OK: Logged in
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/users/elonmusk", 200, response, auth=access_token)

        # OK: Not logged in, email not public
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("get", "/users/elonmusk", 200, response)

        # (set isEmailPublic to true)
        user = User.query.filter_by(username='elonmusk').first()
        user.public_email = True
        user.save()

        # OK: Not logged in, email public
        response = {'username': 'elonmusk', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': True}
        self.route("get", "/users/elonmusk", 200, response)

    def test_delete_user(self):
        access_token = self.login()[0]

        # E210: Can't delete user
        response = APIErrors[210].json()
        self.route("delete", "/users/therock", 403, response, auth=access_token)

        # OK: Deleted by himself
        self.route("delete", "/users/elonmusk", 204, {}, auth=access_token)
        self.assertFalse(User.query.filter_by(username='elonmusk').first())

        # (recreate the user)
        User(username="elonmusk", email="elon@tesla.com", password="password", name="Elon", surname="Musk").save()
        admin_access_token = self.login(username='therock')[0]

        # OK: Deleted by an admin
        self.route("delete", "/users/elonmusk", 204, {}, auth=admin_access_token)
        self.assertFalse(User.query.filter_by(username='elonmusk').first())

    def test_edit_user(self):
        access_token = self.login()[0]

        # E120: Missing Authorization Header
        response = APIErrors[120].json()
        self.route("put", "/users/elonmusk/username", 401, response)

        # E100: Resource not found
        response = APIErrors[100].json()
        self.route("put", "/users/elonmusk/perms", 404, response, auth=access_token)

        # E230: User already exist
        request = {"value": "therock"}
        response = APIErrors[230].json()
        self.route("put", "/users/elonmusk/username", 409, response, body=request, auth=access_token)

        # OK: Changed username
        request = {"value": "hpotter"}
        response = {'username': 'hpotter', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/users/elonmusk/username", 200, response, body=request, auth=access_token)

        # OK: Changed password
        request = {"value": "LordVoldemort"}
        response = {'username': 'hpotter', 'name': 'Elon', 'surname': 'Musk', 'email': 'elon@tesla.com', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/users/hpotter/password", 200, response, body=request, auth=access_token)

        # OK: Changed email
        request = {"value": "harrypotter@hedwig.uk"}
        response = {'username': 'hpotter', 'name': 'Elon', 'surname': 'Musk', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': False}
        self.route("put", "/users/hpotter/email", 200, response, body=request, auth=access_token)

        # E263: isEmailPublic is not a bool
        request = {"value": "TheGuyWhoLived"}
        response = APIErrors[263].json()
        self.route("put", "/users/hpotter/isEmailPublic", 400, response, body=request, auth=access_token)

        # OK: Changed isEmailPublic
        request = {"value": True}
        response = {'username': 'hpotter', 'name': 'Elon', 'surname': 'Musk', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': "", 'isEmailPublic': True}
        self.route("put", "/users/hpotter/isEmailPublic", 200, response, body=request, auth=access_token)

        # OK: Changed name
        request = {"value": "Harry"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Musk', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': True}
        self.route("put", "/users/hpotter/name", 200, response, body=request, auth=access_token)

        # OK: Changed surname
        request = {"value": "Potter"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': '', 'isEmailPublic': True}
        self.route("put", "/users/hpotter/surname", 200, response, body=request, auth=access_token)

        # E291: bio too long
        request = {"value": "a" * 201}
        response = APIErrors[291].json()
        self.route("put", "/users/hpotter/bio", 400, response, body=request, auth=access_token)

        # OK: Changed bio
        request = {"value": "Hey!\nThis is Harry Potter!"}
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': "Hey!\nThis is Harry Potter!", 'isEmailPublic': True}
        self.route("put", "/users/hpotter/bio", 200, response, body=request, auth=access_token)

        # (try to login with new credentials)
        request = {"username": "hpotter", "password": "LordVoldemort"}
        response = {"accessToken": "", "refreshToken": ""}
        json = self.route("post", "/login", 200, {'accessToken': '', 'refreshToken': ''}, body=request, ignored=("accessToken", "refreshToken"))

        # (check new infos)
        response = {'username': 'hpotter', 'name': 'Harry', 'surname': 'Potter', 'email': 'harrypotter@hedwig.uk', 'perms': 0, 'id': 1, 'bio': "Hey!\nThis is Harry Potter!", 'isEmailPublic': True}
        self.route("get", "/users/hpotter", 200, response, auth=json['accessToken'])

    def test_get_communities(self):
        access_token = self.login()[0]

        # OK: Not loged in
        response = {'communities': [{'name': 'ScienceThings', 'id': 1}]}
        self.route('get', '/communities', 200, response)

        # OK: Logged in but not following
        response = {'communities': [{'name': 'ScienceThings', 'id': 1, 'following': False}]}
        self.route('get', '/communities', 200, response, auth=access_token)

        Follow(follower_id=1, community_id=1).save()

        # OK: Logged in and following
        response = {'communities': [{'name': 'ScienceThings', 'id': 1, 'following': True}]}
        self.route('get', '/communities', 200, response, auth=access_token)

    def test_create_community(self):
        access_token = self.login()[0]
        admin_access_token = self.login(username='therock')[0]

        # E310: Can't create community
        response = APIErrors[310].json()
        self.route('post', '/communities', 403, response, auth=access_token)

        # E331: Name too short
        request = {"name": "AMA"}
        response = APIErrors[331].json()
        self.route('post', '/communities', 400, response, body=request, auth=admin_access_token)

        # E332: Name too long
        request = {"name": "AMAMAMAMAMAMAMAMAMAMA"}
        response = APIErrors[332].json()
        self.route('post', '/communities', 400, response, body=request, auth=admin_access_token)

        # E333: Name contains invalid character(s)
        request = {"name": "AMALAPIZZA!"}
        response = APIErrors[333].json()
        self.route('post', '/communities', 400, response, body=request, auth=admin_access_token)

        # E320: Community already exist
        request = {"name": "ScienceThings"}
        response = APIErrors[320].json()
        self.route('post', '/communities', 409, response, body=request, auth=admin_access_token)

        # OK: Created
        request = {"name": "FoodPorn"}
        response = {"name": "FoodPorn", "id": 2}
        self.route('post', '/communities', 201, response, body=request, auth=admin_access_token)

    def test_get_community(self):
        access_token = self.login()[0]

        # E300: Community not found
        response = APIErrors[300].json()
        self.route('get', '/communities/FoodPorn', 404, response)

        # OK: Not logged in
        response = {'name': 'ScienceThings', 'id': 1}
        self.route('get', '/communities/ScienceThings', 200, response)

        # OK: Logged in but not following
        response = {'name': 'ScienceThings', 'id': 1, 'following': False}
        self.route('get', '/communities/ScienceThings', 200, response, auth=access_token)

        Follow(follower_id=1, community_id=1).save()

        # OK: Logged in and following
        response = {'name': 'ScienceThings', 'id': 1, 'following': True}
        self.route('get', '/communities/ScienceThings', 200, response, auth=access_token)

# Run unittests
unittest.main()

# Set the TESTING variable to the previous value
environ['TESTING'] = old_testing
