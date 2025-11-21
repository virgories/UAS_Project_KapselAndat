from fastapi import FastAPI
from database import Base, engine
from routers import auth, categories

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
