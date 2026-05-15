from fastapi import APIRouter, HTTPException
from backend.schemas import IntroRequestCreate, RequestResponse, UpdateRequestStatus, ApprovalEmailRequest
from backend.email_utils import send_approval_email
import backend.db as db

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("/", response_model=list[RequestResponse])
def get_requests():
    try:
        return db.get_all_requests()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-pending")
def check_pending(email: str):
    try:
        return {"has_pending": db.has_pending_request(email)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
def create_request(payload: IntroRequestCreate):
    try:
        db.save_intro_request(
            payload.client_name, payload.client_email,
            payload.counselor_id, payload.compatibility_score,
        )
        return {"message": "Request saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{request_id}/approve")
def approve_request(request_id: int, payload: UpdateRequestStatus):
    try:
        db.update_request_status(request_id, payload.status)
        return {"message": f"Request {request_id} status updated to {payload.status}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/send-approval-email")
def send_email(request_id: int, payload: ApprovalEmailRequest):
    try:
        send_approval_email(payload.client_name, payload.client_email, payload.counselor_name)
        return {"message": "Approval email sent."}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")
