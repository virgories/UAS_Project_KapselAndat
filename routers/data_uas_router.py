from fastapi import APIRouter, Depends, HTTPException
import schemas 
import models
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# ... (Pastikan kode ini ada di fungsi yang Anda uji, misalnya get_all_transactions)
@router.get("/", response_model=list[schemas.DataUASOut])
def get_all_transactions(db: Session = Depends(get_db)):
    data = db.query(models.DataUAS).all()
    
    # KODE DIAGNOSIS KRITIS:
    print("\n--- HASIL KUERI DB ---")
    print(f"Jumlah Baris: {len(data)}") 
    print(f"Data 5 Baris Awal: {data[:5]}") 
    print("-------------------------\n")
    
    return data