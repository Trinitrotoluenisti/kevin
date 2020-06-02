from application.main import app, db, User

import unittest
from datetime import timedelta


class Test(unittest.TestCase):
    def setUp(self):
        # App configs
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=5)

        # Creating app
        self.app = app.test_client()

        # Recreate database
        db.drop_all()
        db.create_all()

        # create some tersting users
        self.testing_user = {
                             'username': 'baobab',
                             'name': 'Paolo',
                             'surname': 'Barbieri',
                             'email': 'paolobarbieri@libero.it',
                             'password': 'paoloba69'
                            }
        r = self.app.post('/register', json=self.testing_user)

        # save tokens
        self.access = r.json['access_token']
        self.refresh = r.json['refresh_token']
    
    def route(self, path, method, expected_sc, response, json=None, auth=None, equal=True):
        """
        Test a route.

        path:        the route's path
        method:      GET or POST
        expected_sc: the expected status code
        response:    the expected response
        json:        the form json
        auth:        the access/refresh token
        equal:       if true, the expected response must be
                     perfectly equal to the gotten
        """

        if auth:
            auth = {'Authorization': f'Bearer {auth}'}

        # Make request
        if method.lower() == 'get':
            r = self.app.get(path, headers=auth)
        elif method.lower() == 'post':
            r = self.app.post(path, json=json, headers=auth)
        else:
            raise ValueError("Undefined method")

        # Check status code
        self.assertEqual(r.status_code, expected_sc)

        # Check response
        if equal:
            self.assertEqual(r.json, response)
        else:
            for key in response:
                self.assertEqual(r.json[key], response[key])

        return r.json

    def auth(self, auth, real=True):
        """
        Check if access_token is valid or not
        """

        r = self.app.get("/user", headers={'Authorization': f'Bearer {auth}'})

        # Check status code
        if real:
            self.assertEqual(r.status_code, 200)
        else:
            self.assertEqual(r.status_code, 401)

    def test_login(self):
        # without parameters
        response = {"msg": "Missing parameter(s)"}
        self.route('/login', 'POST', 400, response)
        self.route('/login', 'POST', 400, response, json={'username': self.testing_user['username']})
        self.route('/login', 'POST', 400, response, json={'password': self.testing_user['password']})

        # with wrong credentials
        response = {"msg": "Wrong username or password"}
        self.route('/login', 'POST', 400, response, json={'username': self.testing_user['username'], 'password': ''})
        self.route('/login', 'POST', 400, response, json={'username': '', 'password': self.testing_user['password']})

        # with right parameters
        token = self.route('/login', 'POST', 200, {"msg": "Ok"}, json=self.testing_user, equal=False)['access_token']
        self.auth(token)

    def test_register(self):
        # without parameters
        response = {"msg": "Missing parameter(s)"}
        self.route('/register', 'POST', 400, response)

        # already registered
        user = self.testing_user
        response = {"msg": "Already registered"}
        self.route('/register', 'POST', 400, response, json=user)

        # too long parameters
        user = dict(zip(user.keys(), [''] * len(user)))
        response = {"msg": "Username and/or password too short"}
        self.route('/register', 'POST', 400, response, json=user)

        # invalid email
        user = dict(zip(user.keys(), user.keys()))
        response = {"msg": "Invalid email"}
        self.route('/register', 'POST', 400, response, json=user)

        # try with a new user
        user['email'] = 'email@email.it'
        token = self.route('/register', 'POST', 200, {"msg": "Ok"}, json=user, equal=False)['access_token']

        # try token
        self.auth(token)

        # check if user is in the db
        self.route('/login', 'POST', 200, {"msg": "Ok"}, json=user, equal=False)

    def test_refresh(self):
        # without header
        self.route('/refresh', 'POST', 401, {"msg": "Missing Authorization Header"})

        # with wrong header
        self.route('/refresh', 'POST', 422, {'msg': "Only refresh tokens are allowed"}, auth=self.access)

        # with right refresh
        token = self.route('/refresh', 'POST', 200, {'msg': "Ok"}, auth=self.refresh, equal=False)['access_token']

        # check token
        self.auth(token)

    def test_logouts(self):
        self.auth(self.access)

        # revoke access token
        self.app.post('/logout/access', headers={'Authorization': f'Bearer {self.access}'})

        # make sure it's revoked
        self.auth(self.access, real=False)

        # try generating a new access
        access = self.route('/refresh', 'POST', 200, {'msg': "Ok"}, auth=self.refresh, equal=False)['access_token']
        self.auth(access)

        # revoke refresh
        self.app.post('/logout/refresh', headers={'Authorization': f'Bearer {self.refresh}'})

        # make sure it's revoked
        self.route('/refresh', 'POST', 401, {'msg': "Token has been revoked"}, auth=self.refresh)

        # try without headers
        self.route('/logout/access', 'POST', 401, {'msg': "Missing Authorization Header"})
        self.route('/logout/refresh', 'POST', 401, {'msg': "Missing Authorization Header"})

        # try with wrong tokens
        self.route('/logout/access', 'POST', 422, {'msg': "Only access tokens are allowed"}, auth=self.refresh)
        self.route('/logout/refresh', 'POST', 422, {'msg': "Only refresh tokens are allowed"}, auth=self.access)

        # try with revoked tokens
        self.route('/logout/access', 'POST', 401, {'msg': "Token has been revoked"}, auth=self.access)
        self.route('/logout/refresh', 'POST', 401, {'msg': "Token has been revoked"}, auth=self.refresh)

    def test_user_view(self):
        # no username is specified but there is the access token
        response = self.testing_user.copy()
        response.update({'perms': 0, 'id': 1, 'public_email': False, 'bio': ''})
        del response['password']
        self.route('/user', 'GET', 200, response, auth=self.access)

        # no username is specified and there isn't any token
        self.route('/user', 'GET', 401, {'msg': "Missing Authorization Header"})

        # try to fetch data of an unexistent user
        self.route('/user/friend', 'GET', 404, {'msg': "User does not exist"})

        # add an user
        user = dict(zip(self.testing_user.keys(), self.testing_user.keys()))
        user['email'] = 'email@email.com'
        self.app.post('/register', json=user)

        # try to fetch his data
        del user['password'], user['email']
        user.update({'perms': 0, 'id': 2, 'public_email': False, 'bio': ''})        
        self.route('/user/username', 'GET', 200, user)

        # set public_email=True
        User.query.filter_by(username='username').first().public_email = True
        db.session.commit()

        # retry to fetch his data
        user['public_email'] = True
        user['email'] = 'email@email.com'         
        self.route('/user/username', 'GET', 200, user)

    def test_post_creation(self):
        # without authorization
        self.route('/post', 'POST', 401, {'msg': "Missing Authorization Header"})

        # with empty content
        data = {}
        response = {'msg': "Missing parameter(s)"}
        self.route('/post', 'POST', 400, response, json=data, auth=self.access)

        # too short content
        data['content'] = "a"
        response = {'msg': 'Post content empty or too short'}
        self.route('/post', 'POST', 400, response, json=data, auth=self.access)

        # good post
        data['content'] = "a" * 21
        self.route('/post', 'POST', 200, {'msg': 'Ok'}, json=data, auth=self.access)

if __name__ == "__main__":
    unittest.main()
