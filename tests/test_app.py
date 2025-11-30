import pytest
from fastapi.testclient import TestClient
from datetime import date
from sqlalchemy import Float

# Import semua komponen yang relevan
# Ini mengimpor TestingSessionLocal dari database.py saat runtime
from database import Base, get_test_session, get_db 
import models
from main import app


# ----------------------------
# Setup SQLite Test Database
# ----------------------------
# UNPACKING WAJIB: Mengambil TEST_ENGINE dan TestingSessionLocal dari database.py
TEST_ENGINE, TestingSessionLocal = get_test_session() 

def override_get_db():
    # Menggunakan TestingSessionLocal()
    db = TestingSessionLocal() 
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ----------------------------
# Fixture: Setup data awal
# ----------------------------
@pytest.fixture
def setup_data():
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)

    db = TestingSessionLocal() 

    # Kategori (Huruf kecil agar sinkron dengan func.lower() di router)
    cat1 = models.Category(name="masker")
    cat2 = models.Category(name="serum")
    db.add_all([cat1, cat2])

    # Transaksi (Diperbaiki agar rasio bisa dihitung dan kategori konsisten)
    trans1 = models.DataUAS(
        date="2025-11-25",
        item_id="I001",
        item_name="masker A",
        category_name="masker", 
        current_stock=100,
        stock_awal=500,
        in_=100, # IN > 0
        out_=400,
        target_stock=500,
        safety_stock=150.0, 
        restock_yes="YES",
        restock=400,
        transaction_id="T001"
    )

    trans2 = models.DataUAS(
        date="2025-11-25",
        item_id="I002",
        item_name="Serum W",
        category_name="serum", 
        current_stock=300,
        stock_awal=500,
        in_=50, # IN > 0
        out_=200,
        target_stock=500,
        safety_stock=50.0, 
        restock_yes="NO",
        restock=0,
        transaction_id="T002"
    )

    db.add_all([trans1, trans2])
    db.commit()

    yield
    db.close()


# ----------------------------
# Test Kategori
# ----------------------------
def test_get_all_categories(setup_data):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_create_category(setup_data):
    response = client.post(
        "/categories/",
        json={"name": "Sabun"},
        headers={"X-User-Role": "Admin Gudang"}
    )
    assert response.status_code == 201


# ----------------------------
# Test Transaksi
# ----------------------------
def test_get_all_transactions(setup_data):
    response = client.get("/transactions/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ----------------------------
# Test Analytics
# ----------------------------
def test_restock_frequency(setup_data):
    res = client.get("/analytics/restock-frequency")
    assert res.status_code == 200
    
    # EKSPEKTASI: Kunci Kategori Huruf Kecil
    expected_data = {'2025-11': {'masker': 1}}
    assert res.json() == expected_data


def test_out_trend(setup_data):
    res = client.get("/analytics/out-trend")
    assert res.status_code == 200

    # EKSPEKTASI: Kunci Kategori Huruf Kecil
    expected_data = {
        "masker": {"2025-11": 400}, 
        "serum": {"2025-11": 200}
    }
    assert res.json() == expected_data


def test_turnover_ratio(setup_data):
    res = client.get("/analytics/turnover-ratio")
    assert res.status_code == 200

    result = res.json()
    
    # Hasil Rasio Masker: 4.0, Serum: 4.0
    assert result["masker"] == pytest.approx(4.0)
    assert result["serum"] == pytest.approx(4.0)