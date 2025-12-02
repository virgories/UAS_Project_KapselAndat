from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models

from schemas import (
    RestockFrequencyOut,
    OutTrendOut,
    TurnoverRatioOut,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ---------------------------------------------------------
# 1. Frekuensi Restock (Per Bulan, Per Kategori)
# ---------------------------------------------------------
@router.get("/restock-frequency", response_model=RestockFrequencyOut)
def restock_frequency(db: Session = Depends(get_db)):
    rows = (
        db.query(
            # Menggunakan func.substr untuk mengambil YYYY-MM dari kolom Date (String)
            func.substr(models.DataUAS.date, 1, 7).label("month"), 
            models.DataUAS.category_name,
            # Menghitung jumlah entri Restock 'YES' per group
            func.count(models.DataUAS.restock_yes).label("frequency")
        )
        .filter(models.DataUAS.restock_yes == "YES")
        .group_by("month", models.DataUAS.category_name)
        .order_by("month")
        .all()
    )

    # Memformat hasil ke dalam dictionary {month: {category: frequency}}
    result = {}
    for month, category, frequency in rows:
        result.setdefault(month, {})
        result[month][category] = frequency

    return RestockFrequencyOut(root=result)


# ---------------------------------------------------------
# 2. OUT Trend (Total Barang Keluar Per Bulan, Per Kategori)
# ---------------------------------------------------------
@router.get("/out-trend", response_model=OutTrendOut)
def out_trend(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.substr(models.DataUAS.date, 1, 7).label("month"),
            models.DataUAS.category_name,
            # Menggunakan func.sum untuk menjumlahkan barang keluar di database
            func.sum(models.DataUAS.out_).label("total_out")
        )
        .group_by("month", models.DataUAS.category_name)
        .order_by("month")
        .all()
    )

    # Memformat hasil ke dalam dictionary {category: {month: total_out}}
    trend = {}
    for month, category, total_out in rows:
        trend.setdefault(category, {})
        trend[category][month] = total_out

    return OutTrendOut(root=trend)


# ---------------------------------------------------------
# 3. Turnover Ratio (Total OUT / Total IN Per Kategori)
# ---------------------------------------------------------
@router.get("/turnover-ratio", response_model=TurnoverRatioOut)
def turnover_ratio(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.DataUAS.category_name,
            # Menjumlahkan total IN
            func.sum(models.DataUAS.in_).label("total_in"),
            # Menjumlahkan total OUT
            func.sum(models.DataUAS.out_).label("total_out")
        )
        # Kelompokkan hanya berdasarkan nama kategori
        .group_by(models.DataUAS.category_name)
        .all()
    )

    ratios = {}

    for category, total_in, total_out in rows:
        # Menghitung rasio
        ratio = (total_out / total_in) if total_in and total_in > 0 else None
        
        # MENGATASI MASALAH SPASI/DUPLIKASI (optional: trim spasi jika ada)
        clean_cat = category.strip() if category else None
        
        if clean_cat:
            ratios[clean_cat] = ratio

    return TurnoverRatioOut(root=ratios)