from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Transaksi
from ..schemas import TransactionCreate, TransactionUpdate, TransactionOut

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# CREATE
@router.post("/", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    # kalau ID manual:
    db_tx = Transaksi(
        transaction_id=payload.transaction_id,
        date=payload.date,
        item_id=payload.item_id,
        item_name=payload.item_name,
        category_name=payload.category_name,
        stock_current=payload.stock_current,
        stock_awal=payload.stock_awal,
        qty_in=payload.qty_in,
        qty_out=payload.qty_out,
        target_stock=payload.target_stock,
        bulan=payload.bulan,
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx


# READ all
@router.get("/", response_model=list[TransactionOut])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaksi).all()


# READ by id
@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaksi).filter(Transaksi.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


# UPDATE
@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db)
):
    tx = db.query(Transaksi).filter(Transaksi.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.date = payload.date
    tx.item_id = payload.item_id
    tx.item_name = payload.item_name
    tx.category_name = payload.category_name
    tx.stock_current = payload.stock_current
    tx.stock_awal = payload.stock_awal
    tx.qty_in = payload.qty_in
    tx.qty_out = payload.qty_out
    tx.target_stock = payload.target_stock
    tx.bulan = payload.bulan

    db.commit()
    db.refresh(tx)
    return tx


# DELETE
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaksi).filter(Transaksi.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(tx)
    db.commit()
    return {"detail": "Transaction deleted"}