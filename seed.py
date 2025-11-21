# seed_csv.py
import pandas as pd
from database import SessionLocal, engine, Base
from models import Category, Product, Transaction, TxType
import datetime

CSV_PATH = "/mnt/data/Data UAS Kapsel Andat Fix - Data Transaksi.csv"

COL_DATE = "Date"
COL_ITEM_ID = "Item ID"
COL_ITEM_NAME = "Item Name"
COL_CATEGORY = "Category Name"
COL_CURRENT_STOCK = "Current Stock"
COL_STOCK_AWAL = "Stock Awal"
COL_IN = "IN"
COL_OUT = "OUT"
COL_TARGET_STOCK = "Target Stock"
COL_SAFETY_STOCK = "Safety Stock (Bener Gasih?)"
COL_RESTOCK_FLAG = "Restock (YES/NO)"
COL_RESTOCK_QTY = "Restock"
COL_TX_ID = "Transaction ID"

def safe_int(value):
    try:
        if pd.isna(value): return 0
        return int(float(value))
    except:
        return 0

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    df = pd.read_csv(CSV_PATH, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]

    for _, row in df.iterrows():
        date = pd.to_datetime(row[COL_DATE], dayfirst=True, errors="coerce")
        if pd.isna(date):
            date = datetime.datetime.now()

        item_id = str(row[COL_ITEM_ID]).strip()
        item_name = str(row[COL_ITEM_NAME]).strip()
        category_name = str(row[COL_CATEGORY]).strip()

        qty_in = safe_int(row[COL_IN])
        qty_out = safe_int(row[COL_OUT])

        current_stock = safe_int(row[COL_CURRENT_STOCK])
        stock_awal = safe_int(row[COL_STOCK_AWAL])
        target_stock = safe_int(row[COL_TARGET_STOCK])
        safety_stock = safe_int(row[COL_SAFETY_STOCK])

        restock_flag = str(row[COL_RESTOCK_FLAG]) if not pd.isna(row[COL_RESTOCK_FLAG]) else None
        restock_qty = safe_int(row[COL_RESTOCK_QTY])
        tx_id = str(row[COL_TX_ID]).strip() if not pd.isna(row[COL_TX_ID]) else None

        # --- CATEGORY ---
        category = db.query(Category).filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.add(category)
            db.commit()

        # --- PRODUCT ---
        product = db.query(Product).filter_by(item_id=item_id).first()
        if not product:
            product = Product(
                item_id=item_id,
                name=item_name,
                category_id=category.id,
                current_stock=current_stock,
                stock_awal=stock_awal,
                target_stock=target_stock,
                safety_stock=safety_stock,
            )
            db.add(product)
            db.commit()

        # --- IN TRANSACTION ---
        if qty_in > 0:
            tx = Transaction(
                tx_id=tx_id,
                product_id=product.id,
                timestamp=date,
                quantity=qty_in,
                tx_type=TxType.IN,
                restock_flag=restock_flag,
                restock_qty=restock_qty,
            )
            db.add(tx)
            product.current_stock += qty_in

        # --- OUT TRANSACTION ---
        if qty_out > 0:
            tx = Transaction(
                tx_id=tx_id,
                product_id=product.id,
                timestamp=date,
                quantity=qty_out,
                tx_type=TxType.OUT,
                restock_flag=restock_flag,
                restock_qty=restock_qty,
            )
            db.add(tx)
            product.current_stock -= qty_out
            if product.current_stock < 0:
                product.current_stock = 0

        db.commit()

    db.close()
    print("CSV IMPORT SUCCESS")

if __name__ == "__main__":
    seed()
