from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import pandas as pd
import os

# --- Load environment variables ---
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# --- Build database URL ---
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("DATABASE_URL:", DATABASE_URL)

try:
    # --- Test Connection ---
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("✔ Koneksi ke database berhasil!\n")

    # --- List all tables ---
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("📌 Tabel dalam database:")
    for t in tables:
        print(" -", t)

    # --- Optional: show first rows of each table ---
    print("\n📌 Contoh isi tabel (LIMIT 5 per tabel):")
    for t in tables:
        print(f"\n=== {t} ===")
        try:
            df = pd.read_sql(f"SELECT * FROM {t} LIMIT 5", conn)
            print(df)
        except Exception as e:
            print("Tidak bisa baca tabel:", e)

    conn.close()
    print("\n✔ Selesai")

except Exception as e:
    print("❌ Koneksi gagal!")
    print("Error:", e)
