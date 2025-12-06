from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models import Item, Transaction
from backend.auth import get_current_user
from datetime import datetime
from collections import defaultdict
import statistics

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# -----------------------------------
# FREQUENCY PER ITEM
# -----------------------------------
@router.get("/frequency")
def frequency_per_item(db: Session = Depends(get_db), user=Depends(get_current_user)):
    result = defaultdict(int)
    transactions = db.query(Transaction).all()
    for trx in transactions:
        result[trx.item_id] += 1
    return [{"item_id": k, "transaction_count": v} for k, v in result.items()]

# -----------------------------------
# AVERAGE RESTOCK TIME (days)
# -----------------------------------
@router.get("/avg_restock_time")
def avg_restock_time(db: Session = Depends(get_db), user=Depends(get_current_user)):
    restock_times = {}
    items = db.query(Item).all()
    for item in items:
        trx_in = sorted([trx.date for trx in item.transactions if trx.qty_in > 0])
        if len(trx_in) < 2:
            continue
        intervals = [(trx_in[i] - trx_in[i-1]).days for i in range(1, len(trx_in))]
        restock_times[item.id] = statistics.mean(intervals)
    return [{"item_id": k, "avg_restock_days": v} for k, v in restock_times.items()]

# -----------------------------------
# TREND BARANG KELUAR PER ITEM
# -----------------------------------
@router.get("/out_trend")
def out_trend(db: Session = Depends(get_db), user=Depends(get_current_user)):
    trend = defaultdict(int)
    transactions = db.query(Transaction).all()
    for trx in transactions:
        if trx.qty_out > 0:
            key = (trx.item_id, trx.date.strftime("%Y-%m"))
            trend[key] += trx.qty_out
    return [{"item_id": k[0], "month": k[1], "qty_out": v} for k, v in trend.items()]

# -----------------------------------
# TURNOVER RATIO PER ITEM
# -----------------------------------
@router.get("/turnover_ratio")
def turnover_ratio(db: Session = Depends(get_db), user=Depends(get_current_user)):
    ratio = {}
    items = db.query(Item).all()
    for item in items:
        total_in = sum(trx.qty_in for trx in item.transactions)
        total_out = sum(trx.qty_out for trx in item.transactions)
        ratio[item.id] = total_out / total_in if total_in > 0 else None
    return [{"item_id": k, "turnover_ratio": v} for k, v in ratio.items()]

# -----------------------------------
# SIMPLE RESTOCK PREDICTION
# -----------------------------------
@router.get("/predicted_restock")
def predicted_restock(db: Session = Depends(get_db), user=Depends(get_current_user)):
    prediction = {}
    items = db.query(Item).all()
    for item in items:
        total_out = sum(trx.qty_out for trx in item.transactions)
        total_in = sum(trx.qty_in for trx in item.transactions)
        predicted = max(item.target_stock - (total_in - total_out), 0)
        prediction[item.id] = predicted
    return [{"item_id": k, "predicted_restock": v} for k, v in prediction.items()]
