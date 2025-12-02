from fastapi import FastAPI
from backend.db import engine, Base, init_db
from backend.models import *
from backend.routers import categories, items, transactions, auth_router, analytics

app = FastAPI()

# Buat tabel ketika app start
init_db()

# Router
app.include_router(auth_router.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(transactions.router)

@app.get("/")
def home():
    return {"message": "API is running"}
