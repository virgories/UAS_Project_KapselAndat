# main.py (di root folder UAS_Project_KapselAndat)
from fastapi import FastAPI

from .database import init_db, SessionLocal, seed_categories
from . import models
from .routers import categories, transaction, analytics

# bikin tabel
init_db()

app = FastAPI(
    title="Warehouse Management API",
    version="1.0.0"
)

db_session = SessionLocal()
seed_categories(db_session, models)

app.include_router(categories.router)
app.include_router(transaction.router)
app.include_router(analytics.router)
