from . import api

from flask_restful import Resource, reqparse


""" RESOURCES """
class Login(Resource):
    def post(self):
    	# Parse args
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, location='form', required=True)
        parser.add_argument('password', type=str, location='form', required=True)
        args = parser.parse_args()

        # return loged-in, no matter what
        return 'logged-in!'


""" ADDING RESOURCES TO API """
api.add_resource(Login, '/login')
