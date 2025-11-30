from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float # Tambahkan Float

class DataUAS(Base):
    __tablename__ = "data_uas"



    # Kolom yang Memiliki Spasi/Kapital
    # Perhatikan: Nama di database (string) HARUS SAMA PERSIS dengan di CSV
    date = Column("Date", String(50)) 
    item_id = Column("Item ID", String(50))
    item_name = Column("Item Name", String(255))
    category_name = Column("Category Name", String(255))
    
    current_stock = Column("Current Stock", Integer)
    stock_awal = Column("Stock Awal", Integer)

    # Kolom IN dan OUT (Sesuai dengan kasus terakhir yang error)
    in_ = Column("IN", Integer)
    out_ = Column("OUT", Integer)

    target_stock = Column("Target Stock", Integer)

    # Safety Stock memiliki tipe data Float (desimal) di CSV Anda
    safety_stock = Column("Safety Stock", Float) 
    
    # Restock YES memiliki spasi
    restock_yes = Column("Restock YES", String(10)) 
    restock = Column(Integer)
    
    # Kolom ini bernama 'Transaction ID' di CSV Anda, BUKAN 'Restock_Transaction_ID'
    transaction_id = Column("Transaction ID", String(50), primary_key=True) 


class Category(Base):
    __tablename__ = "categories"
    
    # ... (Model Category tidak ada masalah)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True)