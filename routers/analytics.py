from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
# Tambahkan date dan fromisoformat untuk konversi string tanggal di Python
from datetime import date
from sqlalchemy import func, cast, Float 
from collections import defaultdict
from typing import Optional, Dict, List 

from ..database import get_db
from .. import models
from .. import schemas

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# ---------------------------------------------------------
# Helper: Clean Category
# ---------------------------------------------------------
def clean_category(column):
    return func.lower(func.trim(column)).label("category")

# ---------------------------------------------------------
# 1. Rata-rata frekuensi transaksi setiap barang per hari - KOREKSI
# ---------------------------------------------------------
@router.get("/avg-frequency", response_model=List[Dict])
def avg_frequency_per_item(db: Session = Depends(get_db)):
    # KOREKSI KRITIS: Menggunakan DATEDIFF (fungsi MySQL)
    # DATEDIFF(MAX(date), MIN(date)) menghitung selisih hari. Tambah 1 untuk inklusivitas.
    total_days_query = db.query(
        func.datediff(func.max(models.DataUAS.date), func.min(models.DataUAS.date)) + 1
    ).scalar()
    
    total_days = total_days_query or 1

    rows = (
        db.query(
            models.DataUAS.item_id,
            models.DataUAS.item_name,
            func.count(models.DataUAS.transaction_id).label("total_transaksi")
        )
        .filter((models.DataUAS.in_ > 0) | (models.DataUAS.out_ > 0)) 
        .group_by(models.DataUAS.item_id, models.DataUAS.item_name)
        .all()
    )

    data = []
    for r in rows:
        avg_freq = r.total_transaksi / total_days if total_days > 0 else 0
        data.append({
            "item_id": r.item_id,
            "item_name": r.item_name,
            "total_transaksi": r.total_transaksi,
            "avg_transaksi_per_hari": avg_freq
        })

    return data


# ---------------------------------------------------------
# 2. Rata-rata waktu restock barang (selisih hari antar transaksi IN) - KOREKSI
# ---------------------------------------------------------
@router.get("/avg-restock-time", response_model=List[Dict])
def avg_restock_time(db: Session = Depends(get_db)):
    rows = (
        db.query(models.DataUAS.item_id, models.DataUAS.item_name, models.DataUAS.date)
        .filter(models.DataUAS.in_ > 0) 
        .order_by(models.DataUAS.item_id, models.DataUAS.date)
        .all()
    )

    per_item = defaultdict(list)
    for r in rows:
        per_item[(r.item_id, r.item_name)].append(r.date)

    data = []
    for (item_id, item_name), dates in per_item.items():
        try:
            # Konversi string tanggal (YYYY-MM-DD) ke objek datetime.date untuk perhitungan di Python
            dates = [date.fromisoformat(d) for d in dates] 
        except ValueError:
            # Jika ada kesalahan format, lewati item ini
            dates = []
            
        if len(dates) < 2:
            avg_days = None
        else:
            diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            avg_days = sum(diffs) / len(diffs)
            
        data.append({
            "item_id": item_id,
            "item_name": item_name,
            "avg_restock_days": avg_days
        })

    return data


# ---------------------------------------------------------
# 3. Tren jumlah barang keluar per bulan
# ---------------------------------------------------------
@router.get("/trend-out", response_model=List[Dict])
def trend_out_per_bulan(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.substr(models.DataUAS.date, 1, 7).label("bulan"), 
            func.sum(models.DataUAS.out_).label("total_out")
        )
        .group_by("bulan")
        .order_by("bulan")
        .all()
    )

    data = [{"bulan": r.bulan, "total_out": r.total_out} for r in rows]
    return data


# ---------------------------------------------------------
# 4. Turnover Ratio (OUT / Rata-rata Stok)
# ---------------------------------------------------------
@router.get("/turnover-ratio", response_model=Dict)
def turnover_ratio(db: Session = Depends(get_db)):
    total_out = float(db.query(func.sum(models.DataUAS.out_)).scalar() or 0) 

    sub = (
        db.query(
            models.DataUAS.item_id,
            models.DataUAS.stock_awal, 
            models.DataUAS.current_stock 
        )
        .group_by(models.DataUAS.item_id)
        .subquery()
    )

    avg_stock_expr = (sub.c.stock_awal + sub.c.current_stock) / 2.0
    total_avg_stock = float(db.query(func.sum(avg_stock_expr)).scalar() or 0)

    turnover = total_out / total_avg_stock if total_avg_stock else None

    return {
        "total_out": total_out,
        "total_avg_stock": total_avg_stock,
        "turnover_ratio": turnover
    }


# ---------------------------------------------------------
# 5. Rasio total barang yang keluar dan masuk
# ---------------------------------------------------------
@router.get("/in-out-ratio", response_model=Dict)
def in_out_ratio(db: Session = Depends(get_db)):
    total_in = float(db.query(func.sum(models.DataUAS.in_)).scalar() or 0)
    total_out = float(db.query(func.sum(models.DataUAS.out_)).scalar() or 0)

    ratio_out_over_in = (total_out / total_in) if total_in else None

    return {
        "total_in": total_in,
        "total_out": total_out,
        "ratio_out_over_in": ratio_out_over_in
    }


# ---------------------------------------------------------
# 6. Prediksi kebutuhan restock berdasarkan data historis (simple)
# ---------------------------------------------------------
@router.get("/restock-forecast", response_model=Dict)
def restock_forecast(
    item_id: str,
    days_ahead: int = 30,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(models.DataUAS.date, models.DataUAS.out_)
        .filter(models.DataUAS.item_id == item_id)
        .order_by(models.DataUAS.date)
        .all()
    )

    if not rows:
        return {"item_id": item_id, "message": "Data tidak ditemukan"}

    try:
        dates = [date.fromisoformat(r.date) for r in rows]
        
        total_out = sum(r.out_ for r in rows)
        
        if not dates:
            total_days = 0
        else:
            total_days = (dates[-1] - dates[0]).days + 1
            
        avg_out_per_day = total_out / total_days if total_days > 0 else 0
        forecast_qty = avg_out_per_day * days_ahead

        return {
            "item_id": item_id,
            "avg_out_per_day": avg_out_per_day,
            "days_ahead": days_ahead,
            "forecast_restock_qty": forecast_qty
        }
    except ValueError:
         raise HTTPException(status_code=500, detail="Kesalahan format tanggal pada data historis.")