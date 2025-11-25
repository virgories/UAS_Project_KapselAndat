from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import hashlib
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================
# PASSWORD HASHING (Pre-Hash)
# ============================
# Ini solusi resmi untuk bypass limit 72 bytes
# https://passlib.readthedocs.io/manual/faq.html#max-password-size

def hash_password(password: str) -> str:
    print("=== DEBUG HASH ===")
    print("Raw password:", password)
    print("Length chars:", len(password))
    print("Length bytes:", len(password.encode("utf-8")))

    # PRE-HASH pakai SHA256 → hasil 32 bytes aman
    prehashed = hashlib.sha256(password.encode("utf-8")).hexdigest()

    print("Prehashed length:", len(prehashed))
    
    return pwd_context.hash(prehashed)


def verify_password(plain_password: str, hashed: str) -> bool:
    prehashed = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(prehashed, hashed)


# ============================
# TOKEN FUNCTIONS
# ============================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")
