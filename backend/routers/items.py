from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(prefix="/items", tags=["Items"])


# CREATE
@router.post("/", response_model=schemas.Item)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(models.Item).filter(models.Item.item_code == item.item_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item code already exists")

    new_item = models.Item(
        item_code=item.item_code,
        name=item.name,
        category_id=item.category_id,
        target_stock=item.target_stock
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# READ ALL
@router.get("/", response_model=list[schemas.Item])
def get_all_items(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(models.Item).all()


# READ ONE
@router.get("/{item_id}", response_model=schemas.Item)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# UPDATE
@router.put("/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    updated: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = updated.name
    item.category_id = updated.category_id
    item.target_stock = updated.target_stock

    db.commit()
    db.refresh(item)
    return item


# DELETE
@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
