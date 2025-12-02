from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Transaksi(Base):
    __tablename__ = "transaction"   # sama persis kayak nama tabel di MySQL

    transaction_id = Column("Transaction ID", Integer, primary_key=True, index=True)
    date          = Column("Date", String(20), index=True)           # di DB tipe text
    item_id       = Column("Item ID", String(20), index=True)
    item_name     = Column("Item Name", String(100))
    category_name = Column("Category Name", String(50))

    stock_current = Column("Current Stock", Integer)
    stock_awal    = Column("Stock Awal", Integer)

    qty_in        = Column("IN", Integer)
    qty_out       = Column("OUT", Integer)

    target_stock  = Column("Target Stock", Integer)

    # yang di kanan tabel boleh diabaikan dulu, nanti kalau sempat:
    safety_stock  = Column("Safety Stock (Bener Gasih?)", Float, nullable=True)
    restock_flag  = Column("Restock (YES/NO)", String(10), nullable=True)
    restock       = Column("Restock", Integer, nullable=True)

    bulan         = Column("Bulan", String(20), index=True, nullable=True)
