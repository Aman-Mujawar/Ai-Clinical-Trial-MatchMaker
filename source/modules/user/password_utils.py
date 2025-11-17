# source/modules/user/password_utils.py
from passlib.context import CryptContext

# ✅ Only bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt safely (truncate to 72 bytes for bcrypt)
    """
    return pwd_context.hash(password.encode("utf-8")[:72])

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password using bcrypt
    """
    return pwd_context.verify(password.encode("utf-8")[:72], hashed)
