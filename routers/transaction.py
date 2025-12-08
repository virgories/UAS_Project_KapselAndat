from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..dependencies import require_admin

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/",
    response_model=schemas.TransactionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
):
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/", response_model=list[schemas.TransactionOut])
def get_all_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()

@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == transaction_id
    ).first()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put(
    "/{transaction_id}",
    response_model=schemas.TransactionOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
def update_transaction(
    transaction_id: str,
    transaction: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
):
    tx = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == transaction_id
    ).first()

    if tx is None:
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
    dependencies=[Depends(require_admin)],
)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == transaction_id
    ).first()

    if tx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    db.delete(tx)
    db.commit()
    return {"status": "success", "message": "Transaction deleted"}
