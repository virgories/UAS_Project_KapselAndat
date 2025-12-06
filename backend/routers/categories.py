from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


# CREATE
@router.post("/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_cat = models.Category(name=category.name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


# READ ALL
@router.get("/", response_model=list[schemas.Category])
def get_categories(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(models.Category).all()


# READ ONE
@router.get("/{category_id}", response_model=schemas.Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


# UPDATE
@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    cat.name = data.name
    db.commit()
    db.refresh(cat)
    return cat


# DELETE
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(cat)
    db.commit()
    return {"message": "Category deleted successfully"}
