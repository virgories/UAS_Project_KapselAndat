from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Transaksi(Base):
    __tablename__ = "transaksi"

    id = Column(Integer, primary_key=True, index=True)
    tgl = Column(Date, index=True)
    item_id = Column(String(20), index=True)
    item_name = Column(String(100))
    category_name = Column(String(50))
    stock_current = Column(Integer)
    stock_awal = Column(Integer)
    qty_in = Column(Integer)
    qty_out = Column(Integer)
    target_stock = Column(Integer)
    bulan = Column(String(20), index=True)
