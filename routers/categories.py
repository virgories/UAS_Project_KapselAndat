from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models
from .. import schemas
from ..database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# ----------------------------
# Helper: Role validation
# ----------------------------
def require_admin(role: str = Header(None, alias="X-User-Role")):
    if role != "Admin Gudang":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return role


# ----------------------------
# GET all categories
# ----------------------------
@router.get("/", response_model=list[schemas.CategoryOut])
def get_all_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


# ----------------------------
# CREATE category (Admin only)
# ----------------------------
@router.post(
    "/",
    response_model=schemas.CategoryOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
):
    cleaned_name = category.name.strip().lower()

    if db.query(models.Category).filter(models.Category.name == cleaned_name).first():
        raise HTTPException(status_code=400, detail=f"Kategori '{cleaned_name}' sudah ada.")

    db_cat = models.Category(name=cleaned_name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


# ----------------------------
# UPDATE category by name (Admin only)
# ----------------------------
@router.put(
    "/{category_name}",
    response_model=schemas.CategoryOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)]
)
def update_category(
    category_name: str,
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
):
    cleaned_search_name = category_name.strip().lower()
    cleaned_new_name = category.name.strip().lower()

    db_cat = db.query(models.Category).filter(
        models.Category.name == cleaned_search_name
    ).first()

    if not db_cat:
        raise HTTPException(status_code=404, detail=f"Kategori '{category_name}' tidak ditemukan")

    db_cat.name = cleaned_new_name
    db.commit()
    db.refresh(db_cat)
    return db_cat


# ----------------------------
# DELETE category by name (Admin only)
# ----------------------------
@router.delete(
    "/{category_name}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)]
)
def delete_category(
    category_name: str,
    db: Session = Depends(get_db),
):
    cleaned_search_name = category_name.strip().lower()

    db_cat = db.query(models.Category).filter(
        models.Category.name == cleaned_search_name
    ).first()

    if not db_cat:
        raise HTTPException(status_code=404, detail=f"Kategori '{category_name}' tidak ditemukan")

    db.delete(db_cat)
    db.commit()
    return {"status": "success"}


# ----------------------------
# AUTO-FILL categories from transaction table (Admin only)
# ----------------------------
@router.post(
    "/auto-fill",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def auto_fill_categories(db: Session = Depends(get_db)):
    """
    Isi tabel categories berdasarkan kolom 'Category Name' di tabel transaction.
    Hanya menambah kategori yang belum ada.
    """
    rows = (
        db.query(models.Transaction.category_name)
        .distinct()
        .filter(models.Transaction.category_name.isnot(None))
        .all()
    )

    created: list[models.Category] = []

    for (name,) in rows:
        if not name:
            continue

        cleaned_name = name.strip().lower()

        existing = (
            db.query(models.Category)
            .filter(models.Category.name == cleaned_name)
            .first()
        )
        if existing:
            continue

        new_cat = models.Category(name=cleaned_name)
        db.add(new_cat)
        created.append(new_cat)

    db.commit()

    for cat in created:
        db.refresh(cat)

    return [{"id": c.id, "name": c.name} for c in created]
