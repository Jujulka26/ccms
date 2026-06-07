from fastapi import APIRouter, HTTPException
from schemas import (
    IntroRequestCreate, RequestResponse,
    UpdateRequestStatus, ApprovalEmailRequest,
)
from email_utils import send_approval_email
import db

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("/", response_model=list[RequestResponse])
def get_requests():
    try:
        return db.get_all_requests()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch requests.")


@router.get("/check-pending")
def check_pending(email: str):
    try:
        return {"has_pending": db.has_pending_request(email)}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to check pending status.")


@router.post("/", status_code=201)
def create_request(payload: IntroRequestCreate):
    try:
        db.save_intro_request(
            payload.client_name, payload.client_email,
            payload.counselor_id, payload.compatibility_score,
            payload.client_age, payload.client_gender, payload.client_ethnicity, payload.client_issue,
            payload.prev_exp, payload.preferred_language, payload.preferred_modality, payload.preferred_c_gender,
        )
        return {"message": "Request saved successfully."}
    except db.CounselorAtCapacity as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save request.")


@router.put("/{request_id}/approve")
def approve_request(request_id: int, payload: UpdateRequestStatus):
    try:
        db.update_request_status(request_id, payload.status)
        return {"message": f"Request {request_id} status updated to {payload.status}."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update request status.")


@router.patch("/{request_id}/close")
def close_request(request_id: int):
    try:
        db.close_request(request_id)
        return {"message": f"Request {request_id} closed."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to close request.")


@router.post("/{request_id}/send-approval-email")
def send_email(request_id: int, payload: ApprovalEmailRequest):
    try:
        send_approval_email(payload.client_name, payload.client_email, payload.counselor_name)
        return {"message": "Approval email sent."}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send approval email.")
