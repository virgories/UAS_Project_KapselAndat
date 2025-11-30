# main.py
from fastapi import FastAPI
# Cukup import init_db untuk membuat tabel
from database import init_db, SessionLocal, seed_categories
# Import router Anda
from routers import categories, data_uas_router
# Import router analytics
from routers.analytics import router as analytics_router
import models

# 1. Panggil fungsi inisialisasi database (membuat tabel)
# Ini harus dipanggil sekali sebelum aplikasi berjalan
init_db() 

app = FastAPI()
db_session = SessionLocal()
seed_categories(db_session, models)

# 2. Sertakan semua router
app.include_router(categories.router)
app.include_router(data_uas_router.router)
app.include_router(analytics_router)