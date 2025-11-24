from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from auth_utils import create_access_token, verify_password, hash_password
from models import User, UserRole
from schemas import Token, RegisterSchema, LoginSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===============================
# REGISTER (PAKAI JSON)
# ===============================
@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        role=UserRole(data.role)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created"}


# ===============================
# LOGIN (PAKAI JSON)
# ===============================
@router.post("/login", response_model=Token)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token = create_access_token({"sub": user.username, "role": user.role.value})

    return {"access_token": token, "token_type": "bearer"}
