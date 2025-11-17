# source/modules/user/password_utils.py
from passlib.hash import argon2


def hash_password(password: str) -> str:
    """
    Hash password using Argon2 (recommended).
    """
    return argon2.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password using Argon2.
    """
    return argon2.verify(password, hashed)
