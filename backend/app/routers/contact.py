from fastapi import APIRouter, HTTPException
from schemas import EnquiryRequest
from email_utils import send_enquiry_email

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/send-enquiry")
def send_enquiry(payload: EnquiryRequest):
    try:
        send_enquiry_email(payload.name, payload.email, payload.subject, payload.message)
        return {"message": "Enquiry email sent."}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send enquiry email.")
