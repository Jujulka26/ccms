from fastapi import APIRouter, HTTPException
from backend.schemas import AdminLoginRequest, AdminLoginResponse
import backend.db as db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AdminLoginResponse)
def login(payload: AdminLoginRequest):
    try:
        success = db.verify_admin_credentials(payload.email, payload.password)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
