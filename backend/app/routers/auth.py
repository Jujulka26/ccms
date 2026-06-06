from fastapi import APIRouter, HTTPException
from schemas import AdminLoginRequest, AdminLoginResponse
import db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AdminLoginResponse)
def login(payload: AdminLoginRequest):
    try:
        success = db.verify_admin_credentials(payload.email, payload.password)
        return {"success": success}
    except Exception:
        raise HTTPException(status_code=500, detail="Authentication service unavailable.")
