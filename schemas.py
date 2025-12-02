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


# ---------------------------------------------------------
# DATA UAS OUTPUT SCHEMA
# ---------------------------------------------------------
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
