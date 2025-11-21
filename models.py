# models.py
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

class UserRole(enum.Enum):
    admin = "admin"
    analyst = "analyst"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(512), nullable=True)

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)

    item_id = Column(String(100), unique=False, nullable=True)    # from "Item ID"
    name = Column(String(255), nullable=False)                    # from "Item Name"
    category_id = Column(Integer, ForeignKey("categories.id"))

    current_stock = Column(Integer, default=0)
    stock_awal = Column(Integer, default=0)
    target_stock = Column(Integer, default=0)
    safety_stock = Column(Integer, default=0)

    category = relationship("Category", back_populates="products")
    transactions = relationship("Transaction", back_populates="product")

class TxType(enum.Enum):
    IN = "IN"
    OUT = "OUT"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)

    tx_id = Column(String(200), nullable=True)               # Transaction ID
    product_id = Column(Integer, ForeignKey("products.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    quantity = Column(Integer, nullable=False)
    tx_type = Column(Enum(TxType), nullable=False)

    restock_flag = Column(String(10), nullable=True)         # "Restock (YES/NO)"
    restock_qty = Column(Integer, default=0)                 # "Restock"

    product = relationship("Product", back_populates="transactions")
