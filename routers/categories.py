from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func # Diperlukan untuk pembersihan nama kategori (lower, trim)
# KOREKSI KRITIS: Mengubah import absolut ke import relatif 
# untuk memastikan Python menemukan model di root directory.
from .. import models 
from .. import schemas # Import schemas secara modular
from ..database import get_db # KOREKSI: Diubah dari 'from database' menjadi 'from ..database'

router = APIRouter(prefix="/categories", tags=["Categories"])


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
    # Kategori sudah diisi (seeded) dengan nama bersih saat startup.
    return db.query(models.Category).all()


# ----------------------------
# CREATE category (Admin only) 
# ----------------------------
@router.post(
    "/", 
    response_model=schemas.CategoryOut,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    # KOREKSI KRITIS: Membersihkan nama kategori sebelum disimpan (sinkronisasi)
    cleaned_name = category.name.strip().lower()

    # Cek apakah kategori sudah ada (untuk mencegah duplikasi)
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
    status_code=status.HTTP_200_OK
)
def update_category(
    category_name: str,
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    # KOREKSI: Bersihkan nama kategori yang dicari
    cleaned_search_name = category_name.strip().lower()
    cleaned_new_name = category.name.strip().lower()

    db_cat = db.query(models.Category).filter(
        models.Category.name == cleaned_search_name
    ).first()

    if not db_cat:
        raise HTTPException(status_code=404, detail=f"Kategori '{category_name}' tidak ditemukan")

    # KOREKSI: Simpan nama baru yang sudah bersih
    db_cat.name = cleaned_new_name
    db.commit()
    db.refresh(db_cat)
    return db_cat


# ----------------------------
# DELETE category by name (Admin only) 
# ----------------------------
@router.delete(
    "/{category_name}",
    status_code=status.HTTP_200_OK
)
def delete_category(
    category_name: str,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    # KOREKSI: Bersihkan nama kategori yang dicari
    cleaned_search_name = category_name.strip().lower()

    db_cat = db.query(models.Category).filter(
        models.Category.name == cleaned_search_name
    ).first()

    if not db_cat:
        raise HTTPException(status_code=404, detail=f"Kategori '{category_name}' tidak ditemukan")

    db.delete(db_cat)
    db.commit()
    return {"status": "success"}