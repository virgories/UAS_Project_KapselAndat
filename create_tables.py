from database import Base, engine  # import Base dan engine dari project-mu

# Buat semua tabel di database MySQL (atau SQLite)
Base.metadata.create_all(bind=engine)

print("Tabel berhasil dibuat!")
