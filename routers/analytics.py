from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
from typing import Dict, List
from datetime import datetime, date

from ..database import get_db
from .. import models

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)
def parse_date_str(d: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%y", "%d/%m/%y"):
        try:
            return datetime.strptime(d, fmt).date()
        except ValueError:
            continue
    return None

# ---------------------------------------------------------
# 1. Rata-rata frekuensi transaksi setiap barang per hari
# ---------------------------------------------------------
@router.get("/avg-frequency", response_model=List[Dict])
def avg_frequency_per_item(db: Session = Depends(get_db)):
    total_days = db.query(
        func.count(func.distinct(models.Transaction.date))
    ).scalar() or 1

    rows = (
        db.query(
            models.Transaction.item_id,
            models.Transaction.item_name,
            func.count(models.Transaction.transaction_id).label("total_transaksi"),
        )
        .filter(
            (models.Transaction.qty_in > 0) |
            (models.Transaction.qty_out > 0)
        )
        .group_by(models.Transaction.item_id, models.Transaction.item_name)
        .all()
    )

    data = []
    for r in rows:
        avg_freq = r.total_transaksi / total_days if total_days > 0 else 0
        data.append(
            {
                "item_id": r.item_id,
                "item_name": r.item_name,
                "total_transaksi": r.total_transaksi,
                "avg_transaksi_per_hari": avg_freq,
            }
        )

    return data


# ---------------------------------------------------------
# 2. Rata-rata waktu restock (selisih hari antar transaksi IN)
# ---------------------------------------------------------
@router.get("/avg-restock-time", response_model=List[Dict])
def avg_restock_time(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.Transaction.item_id,
            models.Transaction.item_name,
            models.Transaction.date,
        )
        .filter(models.Transaction.qty_in > 0)
        .order_by(models.Transaction.item_id, models.Transaction.date)
        .all()
    )

    # group hanya per item_id
    per_item_dates: dict[str, list[str]] = defaultdict(list)
    per_item_name: dict[str, str] = {}

    for r in rows:
        if r.item_id not in per_item_name:
            # simpan nama pertama yang ketemu (boleh juga dibikin .title() / .lower())
            per_item_name[r.item_id] = r.item_name
        per_item_dates[r.item_id].append(r.date)

    data: List[Dict] = []

    for item_id, date_strs in per_item_dates.items():
        parsed_dates: List[date] = []
        for d in date_strs:
            parsed = parse_date_str(d)
            if parsed is not None:
                parsed_dates.append(parsed)

        # kalau restock cuma 0–1 kali, SKIP aja (jangan tampil)
        if len(parsed_dates) < 2:
            continue

        parsed_dates.sort()
        diffs = [
            (parsed_dates[i] - parsed_dates[i - 1]).days
            for i in range(1, len(parsed_dates))
        ]
        avg_days = sum(diffs) / len(diffs) if diffs else None

        data.append(
            {
                "item_id": item_id,
                "item_name": per_item_name[item_id],
                "avg_restock_days": avg_days,
            }
        )

    return data

# ---------------------------------------------------------
# 3. Tren jumlah barang keluar per bulan
# ---------------------------------------------------------
@router.get("/trend-out", response_model=List[Dict])
def trend_out_per_bulan(db: Session = Depends(get_db)):
    # kolom "Bulan" sudah tidak ada → hitung bulan dari Date
    rows = (
        db.query(
            models.Transaction.date,
            models.Transaction.qty_out,
        )
        .filter(models.Transaction.qty_out > 0)
        .all()
    )

    per_bulan: dict[str, int] = defaultdict(int)

    for r in rows:
        dt = parse_date_str(r.date)
        if dt is None:
            continue
        label = dt.strftime("%b-%Y")  # contoh: "Jan-2024"
        per_bulan[label] += r.qty_out or 0

    # sort by bulan (pakai parsing ulang label)
    hasil = [
        {"bulan": k, "total_out": v}
        for k, v in sorted(
            per_bulan.items(),
            key=lambda kv: datetime.strptime(kv[0], "%b-%Y")
        )
    ]
    return hasil


# ---------------------------------------------------------
# 4. Turnover Ratio (OUT / Rata-rata Stok)
# ---------------------------------------------------------
@router.get("/turnover-ratio")
def turnover_ratio(db: Session = Depends(get_db)):
    total_out = float(
        db.query(func.sum(models.Transaction.qty_out)).scalar() or 0
    )

    sub = (
        db.query(
            models.Transaction.item_id.label("item_id"),
            func.min(models.Transaction.stock_awal).label("stock_awal"),
            func.max(models.Transaction.stock_current).label("stock_current"),
        )
        .group_by(models.Transaction.item_id)
        .subquery()
    )

    avg_stock_expr = (sub.c.stock_awal + sub.c.stock_current) / 2.0

    total_avg_stock = float(
        db.query(func.sum(avg_stock_expr)).scalar() or 0
    )

    turnover = total_out / total_avg_stock if total_avg_stock > 0 else None

    return {
        "total_out": total_out,
        "total_avg_stock": total_avg_stock,
        "turnover_ratio": turnover,
    }


# ---------------------------------------------------------
# 5. Rasio total barang masuk vs keluar
# ---------------------------------------------------------
@router.get("/in-out-ratio", response_model=Dict)
def in_out_ratio(db: Session = Depends(get_db)):
    total_in = float(
        db.query(func.sum(models.Transaction.qty_in)).scalar() or 0
    )
    total_out = float(
        db.query(func.sum(models.Transaction.qty_out)).scalar() or 0
    )

    ratio_out_over_in = (total_out / total_in) if total_in else None

    return {
        "total_in": total_in,
        "total_out": total_out,
        "ratio_out_over_in": ratio_out_over_in,
    }


# ---------------------------------------------------------
# 6. Simple restock forecast per item
# ---------------------------------------------------------
@router.get("/restock-forecast", response_model=Dict)
def restock_forecast(
    item_id: str,
    days_ahead: int = 30,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            models.Transaction.date,
            models.Transaction.qty_out,
        )
        .filter(models.Transaction.item_id == item_id)
        .order_by(models.Transaction.date)
        .all()
    )

    if not rows:
        return {"item_id": item_id, "message": "Data tidak ditemukan"}

    parsed_dates: List[date] = []
    total_out = 0

    for r in rows:
        d = parse_date_str(r.date)
        if d is None:
            continue
        parsed_dates.append(d)
        total_out += r.qty_out or 0

    if not parsed_dates:
        return {"item_id": item_id, "message": "Tanggal tidak bisa diparse"}

    parsed_dates.sort()
    total_days = (parsed_dates[-1] - parsed_dates[0]).days + 1

    avg_out_per_day = total_out / total_days if total_days > 0 else 0
    forecast_qty = avg_out_per_day * days_ahead

    return {
        "item_id": item_id,
        "avg_out_per_day": avg_out_per_day,
        "days_ahead": days_ahead,
        "forecast_restock_qty": forecast_qty,
    }