from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..dependencies import require_admin   # sama seperti di transaction/categories

# Tag & prefix biar di Swagger nggak "default"
router = APIRouter(
    prefix="/barang",
    tags=["Barang"]
)

# =========================
# GET: semua barang
# =========================
@router.get("/", response_model=list[schemas.ItemOut])
def get_all_barang(db: Session = Depends(get_db)):
    """
    Ambil semua barang dari tabel items.
    """
    return db.query(models.Item).all()


# =========================
# GET: satu barang by item_code
# =========================
@router.get("/{item_code}", response_model=schemas.ItemOut)
def get_barang(item_code: str, db: Session = Depends(get_db)):
    item = (
        db.query(models.Item)
        .filter(models.Item.item_code == item_code)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barang tidak ditemukan"
        )

    return item


# =========================
# POST: buat barang baru (Admin only)
# =========================
@router.post(
    "/",
    response_model=schemas.ItemOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)]
)
def create_barang(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db)
):
    # cek item_code unik
    existing = (
        db.query(models.Item)
        .filter(models.Item.item_code == item.item_code)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item code sudah terdaftar"
        )

    db_item = models.Item(
        item_code=item.item_code,
        item_name=item.item_name,
        category_name=item.category_name
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# =========================
# PUT: update barang (Admin only)
# =========================
@router.put(
    "/{item_code}",
    response_model=schemas.ItemOut,
    dependencies=[Depends(require_admin)]
)
def update_barang(
    item_code: str,
    item: schemas.ItemUpdate,
    db: Session = Depends(get_db)
):
    db_item = (
        db.query(models.Item)
        .filter(models.Item.item_code == item_code)
        .first()
    )

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barang tidak ditemukan"
        )

    # update field kalau dikirim
    if item.item_name is not None:
        db_item.item_name = item.item_name
    if item.category_name is not None:
        db_item.category_name = item.category_name

    db.commit()
    db.refresh(db_item)
    return db_item


# =========================
# DELETE: hapus barang (Admin only)
# =========================
@router.delete(
    "/{item_code}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)]
)
def delete_barang(item_code: str, db: Session = Depends(get_db)):
    db_item = (
        db.query(models.Item)
        .filter(models.Item.item_code == item_code)
        .first()
    )

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barang tidak ditemukan"
        )

    db.delete(db_item)
    db.commit()
    return {"status": "success", "message": "Barang deleted"}
