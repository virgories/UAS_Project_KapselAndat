from fastapi import FastAPI
from database import init_db, SessionLocal, seed_categories
import models

from routers import categories, data_uas_router, transaction, analytics

# bikin tabel kalau belum ada
init_db()

app = FastAPI(
    title="Warehouse Management API",
    version="1.0.0"
)

# seed kategori (kalau memang butuh)
db_session = SessionLocal()
seed_categories(db_session, models)

# include SEMUA router
app.include_router(categories.router)
app.include_router(data_uas_router.router)
app.include_router(transaction.router)   # CRUD transaksi
app.include_router(analytics.router)    # Analytics
