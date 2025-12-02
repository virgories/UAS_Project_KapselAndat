from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from config import settings
from sqlalchemy import func
import os

# Base class untuk model ORM
Base = declarative_base()

# -------------------------
# NORMAL MODE (KEMBALI KE MySQL)
# -------------------------

# >>> GUNAKAN settings.DATABASE_URL (Koneksi MySQL) <<<
DATABASE_URL = settings.DATABASE_URL 

engine = create_engine(
    DATABASE_URL, # Menggunakan string koneksi MySQL dari settings
    echo=False,
    # Kembalikan pool_pre_ping (Penting untuk koneksi MySQL)
    pool_pre_ping=True, 
    # HAPUS connect_args={"check_same_thread": False} (Ini hanya untuk SQLite)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------
# TEST MODE (Override by pytest) - Biarkan apa adanya
# -------------------------
def get_test_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

def get_test_session():
    test_engine = get_test_engine()
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    return test_engine, TestingSessionLocal


# -------------------------
# FastAPI Dependency - Biarkan apa adanya
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

# FUNGSI BARU: Mengisi Kategori Berdasarkan Data Transaksi
def seed_categories(db_session, models):
    """
    Mengambil nama kategori unik dari tabel data_uas, membersihkan spasi/case, 
    dan memasukkannya ke tabel categories.
    """
    # Membersihkan kategori yang ada (agar tidak ada duplikasi setiap restart)
    db_session.query(models.Category).delete()
    
    # 1. Ambil nama kategori unik dari tabel data_uas (setelah pembersihan spasi/case)
    # Ini harus sinkron dengan logika clean_category di analytics.py
    unique_categories_raw = db_session.query(
        func.lower(func.trim(models.DataUAS.category_name))
    ).distinct().all()
    
    # 2. Masukkan ke tabel categories
    new_categories = []
    for (name,) in unique_categories_raw:
        if name:
            new_categories.append(models.Category(name=name))
    
    db_session.add_all(new_categories)
    db_session.commit()
    db_session.close()