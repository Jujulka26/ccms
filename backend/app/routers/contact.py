from fastapi import APIRouter, HTTPException
from schemas import EnquiryRequest, UpdateRequestStatus
from email_utils import send_enquiry_email
import db

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/send-enquiry")
def send_enquiry(payload: EnquiryRequest):
    # Persist first so the enquiry is never lost even if email delivery fails.
    try:
        db.save_enquiry(payload.name, payload.email, payload.subject, payload.message)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save enquiry.")

    try:
        send_enquiry_email(payload.name, payload.email, payload.subject, payload.message)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send enquiry email.")
    return {"message": "Enquiry received."}


@router.get("/enquiries")
def list_enquiries():
    try:
        return db.get_enquiries()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch enquiries.")


@router.patch("/enquiries/{enquiry_id}")
def set_enquiry_status(enquiry_id: int, payload: UpdateRequestStatus):
    try:
        db.update_enquiry_status(enquiry_id, payload.status)
        return {"message": f"Enquiry {enquiry_id} updated to {payload.status}."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update enquiry.")
