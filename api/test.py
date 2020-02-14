from application import app, db, User
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        # App configs
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"

        # Creating app
        self.app = app.test_client()

        # Recreate database
        db.drop_all()
        db.create_all()

        # add a testing user into the database
        self.testing_user = {'username': 'username', 'email': 'email@email.it', 'password': 'password'}
        r = self.app.post('/register', data=self.testing_user)

        # save tokens
        self.access = r.json['access_token']
        self.refresh = r.json['refresh_token']
    
    def route(self, path, method, expected_sc, response, data=None, auth=None):
        """
        Test a route.

        path:        the route's path
        method:      GET or POST
        expected_sc: the expected status code
        response:    the expected response
        data:        the form data

        NB: if there are unexpected fields in the
        response, no error is raised
        """

        if auth:
            auth = {'Authorization': f'Bearer {auth}'}

        # Make request
        if method.lower() == 'get':
            r = self.app.get(path, headers=auth)
        elif method.lower() == 'post':
            r = self.app.post(path, data=data, headers=auth)
        else:
            raise ValueError("Undefined method")

        # Check status code
        self.assertEqual(r.status_code, expected_sc)

        # Check response
        for key in response:
            self.assertEqual(r.json[key], response[key])

        return r.json

    def auth(self, auth):
        """
        Check if access_token is valid or not
        """

        r = self.app.post("/protected", headers={'Authorization': f'Bearer {auth}'})

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        # without parameters
        response = {"msg": "Missing parameter(s)"}
        self.route('/login', 'POST', 400, response)
        self.route('/login', 'POST', 400, response, data={'username': self.testing_user['username']})
        self.route('/login', 'POST', 400, response, data={'password': self.testing_user['password']})

        # with wrong credentials
        response = {"msg": "Wrong username or password"}
        self.route('/login', 'POST', 400, response, data={'username': self.testing_user['username'], 'password': ''})
        self.route('/login', 'POST', 400, response, data={'username': '', 'password': self.testing_user['password']})

        # with right parameters
        token = self.route('/login', 'POST', 200, {"msg": "Ok"}, data=self.testing_user)['access_token']
        self.auth(token)

    def test_register(self):
        # without parameters
        response = {"msg": "Missing parameter(s)"}
        self.route('/register', 'POST', 400, response)
        self.route('/register', 'POST', 400, response, data={'username': self.testing_user['username']})

        # too long parameters
        response = {"msg": "username and/or password too short"}
        self.route('/register', 'POST', 400, response, data={'username': '', 'email': '', 'password': ''})
        self.route('/register', 'POST', 400, response, data={'username': 'a', 'email': 'zhou@zhou.it', 'password': 'a'})

        # invalid email
        response = {"msg": "Invalid email"}
        self.route('/register', 'POST', 400, response, data={'username': 'qiang', 'email': 'zhou.it', 'password': 'lamiapassword'})

        # already registered
        response = {"msg": "Already registered"}
        self.route('/register', 'POST', 400, response, data=self.testing_user)

        # try with a new user
        user = {'username': 'noobmaster69', 'email': 'lol@gmail.com', 'password': 'password123'}
        token = self.route('/register', 'POST', 200, {"msg": "Ok"}, data=user)['access_token']

        # try token
        self.auth(token)

        # check if user is in the db
        self.route('/login', 'POST', 200, {"msg": "Ok"}, data=user)

    def test_refresh(self):
        # without header
        self.route('/refresh', 'POST', 401, {"msg": "Missing Authorization Header"})

        # with wrong header
        self.route('/refresh', 'POST', 422, {'msg': "Only refresh tokens are allowed"}, auth=self.access)

        # with right refresh
        token = self.route('/refresh', 'POST', 200, {'msg': "Ok"}, auth=self.refresh)['access_token']

        # check token
        self.auth(token)

if __name__ == "__main__":
    unittest.main()
