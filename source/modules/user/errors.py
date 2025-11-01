# errors.py - Simplified version
class ErrorCode:
    E_USER_NOT_FOUND = {"code": "E_USER_NOT_FOUND", "message": "User not found"}
    E_DUPLICATE_USER_EMAIL = {"code": "E_DUPLICATE_USER_EMAIL", "message": "User email already exists"}
    E_INVALID_PASSWORD = {"code": "E_INVALID_PASSWORD", "message": "Password does not match"}
    E_PASSWORD_NOT_SET = {"code": "E_PASSWORD_NOT_SET", "message": "Password not set yet"}
