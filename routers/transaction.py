from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
from ..dependencies import require_admin   # ini sudah benar

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# ----------------------------
# POST new transaction (CREATE)
# ----------------------------
@router.post(
    "/",
    response_model=schemas.DataUASOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]          # ⬅️ tambahin ini
)
def create_transaction(
    transaction: schemas.DataUASCreate,
    db: Session = Depends(get_db)
):
    db_transaction = models.DataUAS(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/", response_model=list[schemas.DataUASOut])
def get_all_transactions(db: Session = Depends(get_db)):
    return db.query(models.DataUAS).all()


@router.get("/{transaction_id}", response_model=schemas.DataUASOut)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(models.DataUAS).filter(
        models.DataUAS.transaction_id == transaction_id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put(
    "/{transaction_id}",
    response_model=schemas.DataUASOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)]          # ⬅️ di sini juga
)
def update_transaction(
    transaction_id: str,
    transaction: schemas.DataUASCreate,
    db: Session = Depends(get_db)
):
    tx = db.query(models.DataUAS).filter(
        models.DataUAS.transaction_id == transaction_id
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = transaction.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(tx, key, value)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)]          # ⬅️ dan di delete
)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(models.DataUAS).filter(
        models.DataUAS.transaction_id == transaction_id
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(tx)
    db.commit()
    return {"status": "success", "message": "Transaction deleted"}
