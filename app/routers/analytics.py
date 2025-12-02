from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
from datetime import timedelta

from ..database import get_db
from ..models import Transaksi

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# 1. Rata-rata frekuensi transaksi setiap barang per satuan waktu (per hari)
@router.get("/avg-frequency")
def avg_frequency_per_item(db: Session = Depends(get_db)):
    total_days = db.query(func.count(func.distinct(Transaksi.tgl))).scalar() or 0

    rows = (
        db.query(
            Transaksi.item_id,
            Transaksi.item_name,
            func.count(Transaksi.id).label("total_transaksi")
        )
        .filter((Transaksi.qty_in > 0) | (Transaksi.qty_out > 0))
        .group_by(Transaksi.item_id, Transaksi.item_name)
        .all()
    )

    data = []
    for r in rows:
        avg_freq = r.total_transaksi / total_days if total_days else 0
        data.append({
            "item_id": r.item_id,
            "item_name": r.item_name,
            "total_transaksi": r.total_transaksi,
            "avg_transaksi_per_hari": avg_freq
        })

    return {
        "total_hari": total_days,
        "data": data
    }


# 2. Rata-rata waktu restock barang (selisih hari antar transaksi IN)
@router.get("/avg-restock-time")
def avg_restock_time(db: Session = Depends(get_db)):
    rows = (
        db.query(Transaksi.item_id, Transaksi.item_name, Transaksi.tgl)
        .filter(Transaksi.qty_in > 0)
        .order_by(Transaksi.item_id, Transaksi.tgl)
        .all()
    )

    per_item = defaultdict(list)
    for r in rows:
        per_item[(r.item_id, r.item_name)].append(r.tgl)

    data = []
    for (item_id, item_name), dates in per_item.items():
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

    return {"data": data}


# 3. Tren jumlah barang keluar per satuan waktu (pakai kolom bulan)
@router.get("/trend-out")
def trend_out_per_bulan(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Transaksi.bulan,
            func.sum(Transaksi.qty_out).label("total_out")
        )
        .group_by(Transaksi.bulan)
        .order_by(Transaksi.bulan)
        .all()
    )

    data = [{"bulan": r.bulan, "total_out": r.total_out} for r in rows]
    return {"data": data}


# 4. Turnover Ratio = total OUT / total rata-rata stok
@router.get("/turnover-ratio")
def turnover_ratio(db: Session = Depends(get_db)):
    total_out = db.query(func.sum(Transaksi.qty_out)).scalar() or 0

    sub = (
        db.query(
            Transaksi.item_id,
            func.min(Transaksi.stock_awal).label("stock_awal"),
            func.max(Transaksi.stock_current).label("stock_current")
        )
        .group_by(Transaksi.item_id)
        .subquery()
    )

    avg_stock_expr = (sub.c.stock_awal + sub.c.stock_current) / 2.0
    total_avg_stock = db.query(func.sum(avg_stock_expr)).scalar() or 0

    turnover = total_out / total_avg_stock if total_avg_stock else None

    return {
        "total_out": total_out,
        "total_avg_stock": total_avg_stock,
        "turnover_ratio": turnover
    }


# 5. Rasio total barang yang keluar dan masuk
@router.get("/in-out-ratio")
def in_out_ratio(db: Session = Depends(get_db)):
    total_in = db.query(func.sum(Transaksi.qty_in)).scalar() or 0
    total_out = db.query(func.sum(Transaksi.qty_out)).scalar() or 0

    ratio_out_over_in = (total_out / total_in) if total_in else None

    return {
        "total_in": total_in,
        "total_out": total_out,
        "ratio_out_over_in": ratio_out_over_in
    }


# 6. Prediksi kebutuhan restock berdasarkan data historis (simple)
@router.get("/restock-forecast")
def restock_forecast(
    item_id: str,
    days_ahead: int = 30,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(Transaksi.tgl, Transaksi.qty_out)
        .filter(Transaksi.item_id == item_id)
        .order_by(Transaksi.tgl)
        .all()
    )

    if not rows:
        return {"item_id": item_id, "message": "Data tidak ditemukan"}

    total_out = sum(r.qty_out for r in rows)
    total_days = (rows[-1].tgl - rows[0].tgl).days + 1

    avg_out_per_day = total_out / total_days if total_days > 0 else 0
    forecast_qty = avg_out_per_day * days_ahead

    return {
        "item_id": item_id,
        "avg_out_per_day": avg_out_per_day,
        "days_ahead": days_ahead,
        "forecast_restock_qty": forecast_qty
    }
