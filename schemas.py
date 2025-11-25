from pydantic import BaseModel, Field, validator
import re

# ============================
# REGISTER
# ============================
class RegisterSchema(BaseModel):
    username: str = Field(..., min_length=6)   # tambahin min_length=6
    password: str
    role: str

    @validator("username")
    def validate_username(cls, value):
        if len(value) < 6:
            raise ValueError("Username minimal 6 karakter")
        return value

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password minimal 6 karakter")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password harus mengandung minimal 1 huruf kapital")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password harus mengandung minimal 1 angka")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password harus mengandung minimal 1 simbol")

        return value


# ============================
# LOGIN
# ============================
class LoginSchema(BaseModel):
    username: str
    password: str


# ============================
# TOKEN
# ============================
class Token(BaseModel):
    access_token: str
    token_type: str


# ============================
# CATEGORY SCHEMAS
# ============================
class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        orm_mode = True
