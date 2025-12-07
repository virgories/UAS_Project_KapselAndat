from fastapi import FastAPI, HTTPException
from models import Barang, BarangInput, BarangUpdate
import crud


app = FastAPI(title="Warehouse Barang API")


# GET semua barang
@app.get("/barang")
def read_all_barang():
    return crud.get_all_barang()


# GET transaksi spesifik berdasarkan Transaction_ID
@app.get("/barang/{Transaction_ID}")
def read_barang(Transaction_ID: str):
    barang = crud.get_by_transaction(Transaction_ID)
    if barang:
        return barang
    raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")


# POST tambah barang baru
@app.post("/barang")
def add_barang(barang: BarangInput):
    # Input cuma Date, Item_ID, OUT → otomatis hitung field lain
    return crud.create_barang_auto(barang.dict())


# PUT edit transaksi spesifik berdasarkan Transaction_ID
@app.put("/barang/{Transaction_ID}")
def edit_barang(Transaction_ID: str, barang: BarangUpdate):
    updated = crud.update_transaction(Transaction_ID, barang.dict(exclude_unset=True))
    if updated:
        return updated
    raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")


# DELETE transaksi spesifik berdasarkan Transaction_ID
@app.delete("/barang/{Transaction_ID}")
def remove_barang(Transaction_ID: str):
    success = crud.delete_transaction(Transaction_ID)
    if success:
        return {"message": "Transaksi dihapus"}
    raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
