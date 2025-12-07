from pydantic import BaseModel
from typing import Optional


class Barang(BaseModel):
    Date: str
    Item_ID: str
    Item_Name: str
    Category_Name: str
    Current_Stock: int
    Stock_Awal: int
    IN: int
    OUT: int
    Target_Stock: int
    Bulan: str
    Safety_Stock: float
    Restock_Status: str
    Restock_Amount: int
    Transaction_ID: str


class BarangInput(BaseModel):
    Date: str
    Item_ID: str
    OUT: int


class BarangUpdate(BaseModel):
    Date: Optional[str] = None
    OUT: Optional[int] = None
