from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# -----------------------------------
# CREATE TRANSACTION
# -----------------------------------
@router.post("/", response_model=schemas.Transaction)
def create_transaction(
    data: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    # cek item
    item = db.query(models.Item).filter(models.Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # stok sebelum
    stock_before = item.stock

    # update stok otomatis
    if data.qty_in > 0:
        item.stock += data.qty_in

    if data.qty_out > 0:
        if item.stock < data.qty_out:
            raise HTTPException(status_code=400, detail="Stock not enough")
        item.stock -= data.qty_out

    stock_after = item.stock

    trx = models.Transaction(
        item_id=data.item_id,
        date=data.date,
        qty_in=data.qty_in,
        qty_out=data.qty_out,
        stock_before=stock_before,
        stock_after=stock_after
    )

    db.add(trx)
    db.commit()
    db.refresh(trx)
    return trx


# -----------------------------------
# GET ALL
# -----------------------------------
@router.get("/", response_model=list[schemas.Transaction])
def get_all_transactions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(models.Transaction).all()


# -----------------------------------
# GET ONE
# -----------------------------------
@router.get("/{trx_id}", response_model=schemas.Transaction)
def get_transaction(
    trx_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    trx = db.query(models.Transaction).filter(models.Transaction.id == trx_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return trx


# -----------------------------------
# DELETE
# -----------------------------------
@router.delete("/{trx_id}")
def delete_transaction(
    trx_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    trx = db.query(models.Transaction).filter(models.Transaction.id == trx_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(trx)
    db.commit()
    return {"message": "Transaction deleted"}
