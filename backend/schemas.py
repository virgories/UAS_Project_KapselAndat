from pydantic import BaseModel
from datetime import date

# =========================
# CATEGORY
# =========================

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# =========================
# ITEM
# =========================

class ItemBase(BaseModel):
    name: str
    category_id: int
    target_stock: int

class ItemCreate(ItemBase):
    item_code: str

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    item_code: str

    class Config:
        from_attributes = True


# =========================
# TRANSACTION
# =========================

class TransactionBase(BaseModel):
    item_id: int
    date: date
    qty_in: int = 0
    qty_out: int = 0

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    stock_before: int | None = None
    stock_after: int | None = None

    class Config:
        from_attributes = True
