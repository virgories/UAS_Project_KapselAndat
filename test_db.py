from sqlalchemy import text
from backend.db import engine

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))  # pastikan pakai text()
        print("✅ Koneksi database berhasil!", result.fetchone())
except Exception as e:
    print("❌ Koneksi database gagal:", e)
