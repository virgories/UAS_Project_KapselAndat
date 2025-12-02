from sqlalchemy import text
from app.database import SessionLocal

def main():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        print("Koneksi OK:", list(result))
    except Exception as e:
        print("Koneksi ERROR:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
