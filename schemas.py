from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    class Config:
        orm_mode = True

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str
