from fastapi import APIRouter, HTTPException
from schemas import AdminLoginRequest
from security import create_access_token
import db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: AdminLoginRequest):
    try:
        success = db.verify_admin_credentials(payload.email, payload.password)
    except Exception:
        raise HTTPException(status_code=500, detail="Authentication service unavailable.")
    if not success:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token({"sub": payload.email, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}
