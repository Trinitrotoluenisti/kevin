from json import load
from . import app, jwt



class APIError(Exception):
    """
    An error from the APIs. The full list can be seen on api/errors.json.
    """

    def __init__(self, id, error, description, status):
        """
        Initializes a new APIError.

        - id (int): the unique id for that error
        - error (str): a short title
        - description (str): a not-too-long description for the error
        - status (int): the http status code associated with that error
        """

        self.id = id
        self.error = error
        self.description = description
        self.status = status
        super().__init__(id)

    def json(self):
        """
        Returns the error as a dictionary.
        """

        return {"error": self.error, "description": self.description, "id": self.id, "status": self.status}


# Loads APIErrors from errors.json
with open('errors.json') as f:
    APIErrors = dict(map(lambda e: (e['id'], APIError(**e)), load(f).values()))


# Registers them
handle_apierror = lambda e: (e.json(), e.status)
app.errorhandler(APIError)(handle_apierror)
app.errorhandler(404)(lambda *args: handle_apierror(APIErrors[100]))
app.errorhandler(405)(lambda *args: handle_apierror(APIErrors[110]))
jwt.unauthorized_loader(lambda *args: handle_apierror(APIErrors[120]))
jwt.invalid_token_loader(lambda *args: handle_apierror(APIErrors[130]))
jwt.expired_token_loader(lambda *args: handle_apierror(APIErrors[131]))
jwt.revoked_token_loader(lambda *args: handle_apierror(APIErrors[132]))
app.errorhandler(500)(lambda *args: handle_apierror(APIErrors[190]))
