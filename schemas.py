from pydantic import BaseModel, RootModel
from typing import Dict, Optional


# ---------------------------------------------------------
# CATEGORY SCHEMAS
# ---------------------------------------------------------
class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

# ==== ITEM / BARANG SCHEMAS ==== #

class ItemBase(BaseModel):
    item_code: str
    item_name: str
    category_name: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    item_name: Optional[str] = None
    category_name: Optional[str] = None

class ItemOut(ItemBase):
    id: int

    model_config = {"from_attributes": True}

# ---------------------------------------------------------
# TRANSACTION SCHEMAS (untuk CRUD)
# ---------------------------------------------------------
class TransactionBase(BaseModel):
    date: str
    item_id: str
    item_name: str
    category_name: str

    stock_awal: Optional[int] = None
    stock_current: Optional[int] = None

    qty_in: Optional[int] = 0
    qty_out: Optional[int] = 0

    target_stock: Optional[int] = None
    safety_stock: Optional[float] = None
    restock_flag: Optional[str] = None
    restock: Optional[int] = None

    bulan: str | None = None

class TransactionCreate(TransactionBase):
    # contoh: "TXR592898"
    transaction_id: str


class TransactionUpdate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    transaction_id: str

    model_config = {"from_attributes": True}


class DataUASOut(BaseModel):
    date: str
    item_id: str
    item_name: str
    category_name: str
    current_stock: int
    stock_awal: int
    in_: int
    out_: int
    target_stock: int
    safety_stock: float
    restock_yes: str
    restock: int
    transaction_id: Optional[str]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# ANALYTICS SCHEMAS (Wajib Ada)
# ---------------------------------------------------------

class RestockFrequencyOut(RootModel):
    root: Dict[str, Dict[str, int]]


class OutTrendOut(RootModel):
    root: Dict[str, Dict[str, int]]


class TurnoverRatioOut(RootModel):
    root: Dict[str, Optional[float]]
