from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Category(Base):
    __tablename__ = "categories"

    id   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column("Transaction ID", String(20), primary_key=True, index=True)
    date          = Column("Date", String(20), index=True)
    item_id       = Column("Item ID", String(20), index=True)
    item_name     = Column("Item Name", String(100))
    category_name = Column("Category Name", String(50))

    stock_awal    = Column("Stock Awal", Integer)
    stock_current = Column("Current Stock", Integer)

    qty_in        = Column("IN", Integer)
    qty_out       = Column("OUT", Integer)

    target_stock  = Column("Target Stock", Integer)
    safety_stock  = Column("Safety Stock (Bener Gasih?)", Float, nullable=True)
    restock_flag  = Column("Restock (YES/NO)", String(10), nullable=True)
    restock       = Column("Restock", Integer, nullable=True)

    bulan         = Column("Bulan", String(20), index=True, nullable=True)


class Item(Base):
    __tablename__ = "items"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_code     = Column("Item ID", String(20), unique=True, index=True)
    item_name     = Column("Item Name", String(100))
    category_name = Column("Category Name", String(50))
