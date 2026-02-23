from flask import jsonify

def api_response(success, message=None, data=None, status_code=200):
    """
    Standardize API responses for consistency across the application.
    """
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def success_response(message="Operation successful", data=None, status_code=200):
    return api_response(True, message, data, status_code)

def error_response(message="An error occurred", status_code=400, data=None):
    return api_response(False, message, data, status_code)
