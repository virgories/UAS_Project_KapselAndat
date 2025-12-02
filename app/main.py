from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import analytics


app = FastAPI(
    title="Warehouse Management API",
    version="1.0.0"
)

app.include_router(analytics.router)

# nanti kalau CRUD udah siap:
# from .routers import transaksi
# app.include_router(transaksi.router)
