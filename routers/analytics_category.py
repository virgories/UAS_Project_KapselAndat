from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict

from ..database import get_db
from .. import models

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics Category"],
)

# ---------------------------------------------------------
# OUT TREND PER KATEGORI PER BULAN
# ---------------------------------------------------------
@router.get("/out-trend", response_model=List[Dict])
def out_trend(db: Session = Depends(get_db)):
    """
    Tren total OUT per kategori per bulan.
    Bulan diambil dari kolom Date ('2024-01-01' -> '2024-01').
    """
    rows = (
        db.query(
            models.Transaction.category_name.label("category"),
            # ambil 'YYYY-MM' dari 'YYYY-MM-DD'
            func.substr(models.Transaction.date, 1, 7).label("month"),
            func.sum(models.Transaction.qty_out).label("total_out"),
        )
        .filter(models.Transaction.qty_out > 0)
        .group_by("category", "month")
        .order_by("category", "month")
        .all()
    )

    return [
        {
            "category": r.category,
            "month": r.month,
            "total_out": r.total_out,
        }
        for r in rows
    ]


# ---------------------------------------------------------
# RESTOCK FREQUENCY PER KATEGORI
# ---------------------------------------------------------
@router.get("/restock-frequency", response_model=List[Dict])
def restock_frequency(db: Session = Depends(get_db)):
    """
    Frekuensi restock per kategori.
    Hitung berapa banyak transaksi yang punya restock_flag = 'YES'.
    """
    rows = (
        db.query(
            models.Transaction.category_name.label("category"),
            func.count(models.Transaction.transaction_id).label("restock_count"),
        )
        .filter(models.Transaction.restock_flag == "YES")
        .group_by(models.Transaction.category_name)
        .order_by(models.Transaction.category_name)
        .all()
    )

    return [
        {
            "category": r.category,
            "restock_count": r.restock_count,
        }
        for r in rows
    ]
