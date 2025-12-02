class Settings:
    # URL database produksi (MySQL) - Digunakan oleh main.py
    # Kredensial Anda: root:L33ch%40nyoung
    DATABASE_URL = "mysql+pymysql://root:L33ch%40nyoung@localhost:3306/data_transaksi"

    # URL database testing (SQLite in-memory) - Digunakan oleh test_categories.py
    TESTING_DATABASE_URL = "sqlite:///:memory:"

settings = Settings()