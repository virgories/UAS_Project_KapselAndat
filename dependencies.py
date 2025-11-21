from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserRole
from auth_utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
    except:
        raise HTTPException(401, "Invalid token")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user

def require_admin(user=Depends(get_current_user)):
    if user.role != UserRole.admin:
        raise HTTPException(403, "Only admin allowed")
    return user
