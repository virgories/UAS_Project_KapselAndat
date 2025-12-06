import mysql.connector
import csv
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Jessie6162201036",
    database="wms_db"
)

cursor = db.cursor()

def convert_date(value):
    """
    Convert format '1/13/24' → '2024-01-13'
    """
    # Kalau kosong, balikin NULL
    if value.strip() == "":
        return None
    
    # Ubah ke format MySQL
    return datetime.strptime(value, "%m/%d/%y").strftime("%Y-%m-%d")

with open("data.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:

        safety_stock = row["Safety Stock (Bener Gasih?)"].replace(",", ".")

        sql = """
            INSERT INTO transactions (
                transaction_code, date, item_id, item_name, category_name,
                current_stock, stock_awal, qty_in, qty_out, target_stock,
                bulan, safety_stock, restock_flag, restock_qty
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (
            row["Transaction ID"],
            convert_date(row["Date"]),     # ← PENTING!!
            row["Item ID"],
            row["Item Name"],
            row["Category Name"],
            int(row["Current Stock"]),
            int(row["Stock Awal"]),
            int(row["IN"]),
            int(row["OUT"]),
            int(row["Target Stock"]),
            row["Bulan"],
            float(safety_stock),
            row["Restock (YES/NO)"],
            int(row["Restock"]),
        )

        cursor.execute(sql, data)

db.commit()
print("Data berhasil di-import!")
