from sys import path
import unittest


# Import application
path.append(path[0][:-5]) # it's ugly. i know.
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
    
    def test_ping(self):
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, {"msg": "Working"})

    def test_login(self):
        user = {'username': 'username', 'email': 'email', 'password': 'password'}

        # add the user into the db
        db.session.add(User(**user))
        db.session.commit()

        # with right parameters
        r = self.app.post('/login', data=user)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['msg'], "Ok")

        # without parameters
        r = self.app.post('/login')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json, {"msg": "Missing parameter(s)"})

        # with wrong credentials
        user['username'] = 'new_username'
        r = self.app.post('/login', data=user)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json, {"msg": "Wrong username or password"})

if __name__ == "__main__":
    unittest.main()
