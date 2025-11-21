from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from auth_utils import create_access_token, verify_password, hash_password
from models import User, UserRole
from schemas import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(username: str, password: str, role: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, "User exists")

    new_user = User(
        username=username,
        hashed_password=hash_password(password),
        role=UserRole(role)
    )
    db.add(new_user)
    db.commit()

    return {"message": "User created"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(400, "Invalid username or password")

    token = create_access_token({"sub": user.username, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}
