from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from backend.db import Base, engine

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)

    # relasi
    items = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(20), unique=True)
    name = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id"))
    target_stock = Column(Integer)

    stock = Column(Integer, default=0)

    # relasi
    category = relationship("Category", back_populates="items")
    transactions = relationship("Transaction", back_populates="item")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    date = Column(Date)
    qty_in = Column(Integer)
    qty_out = Column(Integer)
    stock_before = Column(Integer)
    stock_after = Column(Integer)
    bulan = Column(String(20))                   # tambahan sesuai CSV
    safety_stock = Column(Float)                 # tambahan sesuai CSV
    restock_flag = Column(String(3))             # YES/NO
    restock_qty = Column(Integer)                # jumlah restock
    transaction_code = Column(String(20))        # Transaction ID


    # relasi
    item = relationship("Item", back_populates="transactions")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
