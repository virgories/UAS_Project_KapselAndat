from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
# Menggunakan impor relatif yang konsisten dari root directory
from .. import models
from .. import schemas
from ..database import get_db 

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# ----------------------------
# POST new transaction (DataUAS) - CREATE
# ----------------------------
@router.post(
    "/",
    response_model=schemas.DataUASOut,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction: schemas.DataUASCreate, # Menggunakan skema input yang benar
    db: Session = Depends(get_db)
):
    # Buat objek model ORM dari skema Pydantic
    # Menggunakan **transaction.model_dump() untuk memetakan semua field
    db_transaction = models.DataUAS(**transaction.model_dump())
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


# ----------------------------
# GET all transactions (DataUAS) - READ all
# ----------------------------
@router.get("/", response_model=list[schemas.DataUASOut])
def get_all_transactions(db: Session = Depends(get_db)):
    return db.query(models.DataUAS).all()


# ----------------------------
# GET transaction by ID - READ by id
# ----------------------------
@router.get("/{transaction_id}", response_model=schemas.DataUASOut)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)): # ID harus str
    tx = db.query(models.DataUAS).filter(
        models.DataUAS.transaction_id == transaction_id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


# ----------------------------
# PUT update transaction (Full Update)
# ----------------------------
@router.put(
    "/{transaction_id}",
    response_model=schemas.DataUASOut,
    status_code=status.HTTP_200_OK
)
def update_transaction(
    transaction_id: str, # ID harus str
    transaction: schemas.DataUASCreate, # Menggunakan skema input yang benar
    db: Session = Depends(get_db)
):
    tx = db.query(models.DataUAS).filter(
        models.DataUAS.transaction_id == transaction_id
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Ambil data baru dari skema Pydantic
    update_data = transaction.model_dump(exclude_unset=True)

    # Perbarui semua atribut model ORM
    for key, value in update_data.items():
        setattr(tx, key, value)

    db.commit()
    db.refresh(tx)
    return tx


# ----------------------------
# DELETE transaction by ID
# ----------------------------
@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)): # ID harus str
    tx = db.query(models.DataUAS).filter(
        models.DataUAS.transaction_id == transaction_id
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(tx)
    db.commit()
    return {"status": "success", "message": "Transaction deleted"}