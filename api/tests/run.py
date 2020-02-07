from sys import path
import unittest


# Import application
path.append(path[0][:-5]) # it's ugly. I know.
from application import app, db, User


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
        self.testing_user = {'username': 'username', 'email': 'email', 'password': 'password'}
        db.session.add(User(**self.testing_user))
        db.session.commit()
    
    def route(self, path, method, expected_sc, response, data=None):
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

        # Make request
        if method.lower() == 'get':
            r = self.app.get(path)
        elif method.lower() == 'post':
            r = self.app.post(path, data=data)
        else:
            raise ValueError("Undefined method")
        
        # Check status code
        self.assertEqual(r.status_code, expected_sc)

        # Check response
        for key in response:
            self.assertEqual(r.json[key], response[key])

    def test_ping(self):
        self.route('/', 'GET', 200, {"msg": "Working"})

    def test_login(self):
        # with right parameters
        self.route('/login', 'POST', 200, {"msg": "Ok"}, data=self.testing_user)

        # without parameters
        response = {"msg": "Missing parameter(s)"}
        self.route('/login', 'POST', 400, response)
        self.route('/login', 'POST', 400, response, data={'username': self.testing_user['username']})
        self.route('/login', 'POST', 400, response, data={'password': self.testing_user['password']})

        # with wrong credentials
        response = {"msg": "Wrong username or password"}
        self.route('/login', 'POST', 400, response, data={'username': self.testing_user['username'], 'password': ''})
        self.route('/login', 'POST', 400, response, data={'username': '', 'password': self.testing_user['password']})


if __name__ == "__main__":
    unittest.main()
