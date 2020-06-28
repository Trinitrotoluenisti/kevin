from json import load
from . import app, jwt



# APIError
class APIError(Exception):
    def __init__(self, id, error, description, status):
        self.id = id
        self.error = error
        self.description = description
        self.status = status
        super().__init__(id)

    def json(self):
        return {"error": self.error, "description": self.description, "id": self.id, "status": self.status}

    def boom(self,*args):
        raise self


# Load errors from errors.json
with open('errors.json') as f:
    APIErrors = dict(map(lambda e: (e['id'], APIError(**e)), load(f).values()))

# Error handlers
handle_apierror = lambda e: (e.json(), e.status)
app.errorhandler(APIError)(handle_apierror)
app.errorhandler(404)(lambda *args: handle_apierror(APIErrors[100]))
app.errorhandler(405)(lambda *args: handle_apierror(APIErrors[110]))
jwt.unauthorized_loader(lambda *args: handle_apierror(APIErrors[120]))
jwt.invalid_token_loader(lambda *args: handle_apierror(APIErrors[130]))
jwt.expired_token_loader(lambda *args: handle_apierror(APIErrors[131]))
jwt.revoked_token_loader(lambda *args: handle_apierror(APIErrors[132]))
app.errorhandler(500)(lambda *args: handle_apierror(APIErrors[190]))
