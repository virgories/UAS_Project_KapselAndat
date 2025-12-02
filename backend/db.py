from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# GANTI sesuai database kalian
MYSQL_USER = "root"
MYSQL_PASSWORD = "%40Jessie6162201036"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "wms_db"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# --- ENGINE ---
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# --- SESSION ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- BASE ---
Base = declarative_base()

# --- Dependency untuk FastAPI ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Optional: init_db() ---
def init_db():
    import backend.models  # pastikan models sudah diload
    Base.metadata.create_all(bind=engine)
