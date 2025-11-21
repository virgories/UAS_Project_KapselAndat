from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user, require_admin
from models import Category
from schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryOut)
def create_category(payload: CategoryCreate,
                    db: Session = Depends(get_db),
                    _ = Depends(require_admin)):

    if db.query(Category).filter(Category.name == payload.name).first():
        raise HTTPException(400, "Category already exists")

    cat = Category(name=payload.name, description=payload.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/", response_model=list[CategoryOut])
def get_all_categories(db: Session = Depends(get_db),
                       user=Depends(get_current_user)):
    return db.query(Category).all()

@router.get("/{cat_id}", response_model=CategoryOut)
def get_category(cat_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    return cat

@router.put("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int,
                    payload: CategoryCreate,
                    db: Session = Depends(get_db),
                    _ = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")

    cat.name = payload.name
    cat.description = payload.description

    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), _ = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")

    db.delete(cat)
    db.commit()

    return {"message": "Category deleted"}
