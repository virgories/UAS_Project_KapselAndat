import pandas as pd
from pathlib import Path
import random
from datetime import datetime


CSV_FILE = Path("data/barang.csv")


# -------------------- Load & Save --------------------
def load_data():
    if CSV_FILE.exists():
        return pd.read_csv(CSV_FILE)
    else:
        columns = ["Date","Item_ID","Item_Name","Category_Name","Current_Stock",
                   "Stock_Awal","IN","OUT","Target_Stock","Bulan",
                   "Safety_Stock","Restock_Status","Restock_Amount","Transaction_ID"]
        return pd.DataFrame(columns=columns)


def save_data(df):
    df.to_csv(CSV_FILE, index=False)


# -------------------- Get Barang --------------------
def get_all_barang():
    df = load_data()
    return df.to_dict(orient="records")


def get_barang(item_id: str):
    """Ambil transaksi terakhir dari item tertentu"""
    df = load_data()
    df_item = df[df["Item_ID"] == item_id]
    if not df_item.empty:
        return df_item.iloc[-1].to_dict()
    return None


def get_by_transaction(transaction_id: str):
    df = load_data()
    df_tx = df[df["Transaction_ID"] == transaction_id]
    if not df_tx.empty:
        return df_tx.iloc[-1].to_dict()
    return None


# -------------------- Create Barang --------------------
def create_barang_auto(data: dict):
    df = load_data()


    item_id = data["Item_ID"]
    out_val = data["OUT"]
    date_str = data["Date"]


    # Ambil data terakhir dari item ini
    df_item = df[df["Item_ID"] == item_id]
    if not df_item.empty:
        last_item = df_item.iloc[-1]
        stock_awal = int(last_item["Current_Stock"])
        item_name = last_item["Item_Name"]
        category_name = last_item["Category_Name"]
    else:
        stock_awal = 0
        item_name = f"Item {item_id}"
        category_name = "Category"


    # Hitung Current Stock
    current_stock = max(stock_awal - out_val, 0)


    # Target stock
    target_stock = 500


    # Safety stock = OUT / 2
    safety_stock = out_val / 2


    # Restock Status
    restock_status = "YES" if current_stock < safety_stock else "NO"


    # Restock Amount
    restock_amount = target_stock - current_stock if restock_status == "YES" else 0


    # Ambil last restock_amount dari item ini
    last_restock = df_item[df_item["Restock_Status"]=="YES"]
    if not last_restock.empty:
        last_in_val = int(last_restock.iloc[-1]["Restock_Amount"])
    else:
        last_in_val = 0


    # IN = restock_amount jika restock sekarang, else ambil last_in_val
    in_val = restock_amount if restock_status == "YES" else 0


    # Transaction_ID unik
    existing_txr = set(df["Transaction_ID"].tolist())
    def generate_txr(existing_ids):
        while True:
            txr = f"TXR{random.randint(100000, 999999)}"
            if txr not in existing_ids:
                return txr
    transaction_id = generate_txr(existing_txr)


    # Bulan dari tanggal
    try:
        bulan = datetime.strptime(date_str, "%m/%d/%y").strftime("%b-%Y")
    except:
        bulan = "Unknown"


    new_row = {
        "Date": date_str,
        "Item_ID": item_id,
        "Item_Name": item_name,
        "Category_Name": category_name,
        "Current_Stock": current_stock,
        "Stock_Awal": stock_awal,
        "IN": in_val,
        "OUT": out_val,
        "Target_Stock": target_stock,
        "Bulan": bulan,
        "Safety_Stock": safety_stock,
        "Restock_Status": restock_status,
        "Restock_Amount": restock_amount,
        "Transaction_ID": transaction_id
    }


    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    return new_row








# -------------------- Delete Barang --------------------
def delete_transaction(transaction_id: str):
    df = load_data()
    before = len(df)
   
    # Hapus baris dengan Transaction_ID yang sama
    df = df[df["Transaction_ID"] != transaction_id]


    if len(df) == before:
        # Tidak ada baris yang dihapus
        return False


    save_data(df)
    return True


def update_transaction(transaction_id: str, update_data: dict):
    try:
        df = load_data()
        idx = df.index[df["Transaction_ID"] == transaction_id]


        if len(idx) == 0:
            return None


        # Update field
        for key, value in update_data.items():
            df.loc[idx, key] = value


        # Recalculate stock
        row = df.loc[idx[-1]]
        stock_awal = int(row["Stock_Awal"])
        out_val = int(row["OUT"])
        current_stock = max(stock_awal - out_val, 0)
        target_stock = 500
        safety_stock = out_val / 2
        restock_status = "YES" if current_stock < safety_stock else "NO"
        restock_amount = target_stock - current_stock if restock_status == "YES" else 0


        df.loc[idx, "Current_Stock"] = current_stock
        df.loc[idx, "Safety_Stock"] = safety_stock
        df.loc[idx, "Restock_Status"] = restock_status
        df.loc[idx, "Restock_Amount"] = restock_amount
        df.loc[idx, "IN"] = restock_amount if restock_status == "YES" else 0


        save_data(df)
        return df.loc[idx[-1]].to_dict()
    except Exception as e:
        print("ERROR update_transaction:", e)
        raise