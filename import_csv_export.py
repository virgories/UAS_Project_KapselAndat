import pandas as pd
from backend.db import SessionLocal
from backend.models import Category, Item, Transaction

db = SessionLocal()

query = db.query(
    Transaction.date,
    Item.item_code.label("Item ID"),
    Item.name.label("Item Name"),
    Category.name.label("Category Name"),
    Transaction.stock_after.label("Current Stock"),
    Transaction.stock_before.label("Stock Awal"),
    Transaction.qty_in.label("IN"),
    Transaction.qty_out.label("OUT"),
    Item.target_stock.label("Target Stock"),
    Transaction.id  # ID transaksi
).join(Item, Transaction.item_id == Item.id)\
 .join(Category, Item.category_id == Category.id)

df = pd.DataFrame(query.all(), columns=[
    "Date","Item ID","Item Name","Category Name","Current Stock","Stock Awal",
    "IN","OUT","Target Stock","ID"
])

df.to_csv("export_data.csv", index=False)
print("✅ Data berhasil diexport ke export_data.csv")
db.close()
