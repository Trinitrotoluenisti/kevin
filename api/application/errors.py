from . import app, jwt


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
def handle_invalid_token(description):
    error = {"error": "unauthorized", "description": description}
    return error, 401
