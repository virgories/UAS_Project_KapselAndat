from pydantic import BaseModel, RootModel
from typing import Dict, Optional, List
from datetime import date
from decimal import Decimal


# ---------------------------------------------------------
# CATEGORY SCHEMAS
# ---------------------------------------------------------
class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# DATA UAS INPUT/OUTPUT SCHEMA
# ---------------------------------------------------------
class DataUASCreate(BaseModel):
    # Field input (sesuai dengan atribut Python di models.py)
    transaction_id: str
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


class DataUASOut(DataUASCreate):
    # Output schema mewarisi semua field dari input
    # Hanya tambahkan field yang mungkin dibuat atau diubah tipenya oleh database.
    
    # model_config ini WAJIB untuk membaca objek ORM SQLAlchemy
    model_config = {"from_attributes": True} 


# ---------------------------------------------------------
# ANALYTICS SCHEMAS
# ---------------------------------------------------------

class RestockFrequencyOut(RootModel):
    # Struktur: {YYYY-MM: {category_name: frequency}}
    root: Dict[str, Dict[str, int]]


class OutTrendOut(RootModel):
    # Struktur: {category_name: {YYYY-MM: total_out}}
    root: Dict[str, Dict[str, int]]


class TurnoverRatioOut(RootModel):
    # Struktur: {category_name: rasio (float atau None)}
    root: Dict[str, Optional[float]]