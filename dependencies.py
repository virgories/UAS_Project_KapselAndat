from fastapi import Header, HTTPException, status
from typing import Optional

def require_admin(x_user_role: Optional[str] = Header(None)):
    if x_user_role != "Admin Gudang":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak. Hanya Admin Gudang yang bisa melakukan operasi ini."
        )
    return True

def require_read_access(x_user_role: Optional[str] = Header(None)):
    if x_user_role not in ["Admin Gudang", "Data Analyst"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akses Ditolak. Harus Admin Gudang atau Data Analyst."
        )
    return True
