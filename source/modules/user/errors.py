class ErrorCode:
    E_USER_NOT_FOUND = {"code": "E_USER_NOT_FOUND", "message": "User not found"}
    E_DUPLICATE_USER_EMAIL = {
        "code": "E_DUPLICATE_USER_EMAIL",
        "message": "User email already exists",
    }
    E_DUPLICATE_USER_PHONENUMBER = {
        "code": "E_DUPLICATE_USER_PHONENUMBER",
        "message": "User phone number already exists",
    }
    E_DUPLICATE_INTERNAL_ID = {
        "code": "E_DUPLICATE_INTERNAL_ID",
        "message": "User with Internal Id already exists",
    }
    E_INVALID_PASSWORD = {
        "code": "E_INVALID_PASSWORD",
        "message": "Password does not match",
    }
    E_INVALID_ROLE_FOR_CLIENT = {
        "code": "E_INVALID_ROLE_FOR_CLIENT",
        "message": "Invalid role for this client",
    }
    E_PROCESSING_ERROR = {
        "code": "E_PROCESSING_ERROR",
        "message": "An error occurred while processing the request",
    }
