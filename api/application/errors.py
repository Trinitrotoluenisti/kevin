from . import app, jwt



# Custom errors
class ContentTypeError(Exception):
    """
    Raised whenever request's body's Content-Type is not set to appication/json
    """

class MissingFieldError(Exception):
    """
    Raised when a field is missing in a request's body
    """


# Custom errors' handlers
@app.errorhandler(MissingFieldError)
def handle_missingfielderror(e):
    field_name = str(e).replace("'", '')
    return {'error': 'invalid request', 'description': f"Missing {field_name}"}, 400

@app.errorhandler(ContentTypeError)
def handle_contenttypeerror(*args):
    return {'error': 'invalid request', 'description': "Content-Type must be application/json"}, 400


# HTTP Errors' handlers
@app.errorhandler(404)
def handle_not_found(*args):
    error = {"error": "not found", "description": "The resource you are looking for hasn't been found"}
    return error, 404

@app.errorhandler(405)
def handle_method_not_allowed(*args):
    error = {"error": "method not allowed", "description": "The resource you are looking for doesn't allow that method"}
    return error, 405

@app.errorhandler(500)
def handle_internal_server_error(*args):
    error = {"error": "internal server error", "description": "The server encountered an error processing the request. We're sorry."}
    return error, 500


# JWT Errors' handlers
@jwt.expired_token_loader
def handle_expired_token(*args):
    error = {"error": "expired token", "description": "The given token has expired"}
    return error, 422

@jwt.invalid_token_loader
def handle_invalid_token(description):
    error = {"error": "invalid token", "description": description}
    return error, 422

@jwt.revoked_token_loader
def handle_revoked_token(*args):
    error = {"error": "revoked token", "description": "The given token has been revoked"}
    return error, 401

@jwt.unauthorized_loader
def handle_unauthorized(description):
    error = {"error": "unauthorized", "description": description}
    return error, 401
