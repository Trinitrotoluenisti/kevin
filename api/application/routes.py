from . import api

from flask_restful import Resource, reqparse


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, location='form', required=True)
        parser.add_argument('password', type=str, location='form', required=True)
        args = parser.parse_args()

        return 'logged-in!'


api.add_resource(Login, '/login')
