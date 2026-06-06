from fastapi import APIRouter, HTTPException
from schemas import CounselorCreate, CounselorUpdate, CounselorResponse
import db

router = APIRouter(prefix="/counselors", tags=["counselors"])


@router.get("/", response_model=list[CounselorResponse])
def get_counselors():
    try:
        return db.load_counselors()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch counselors.")


@router.post("/", status_code=201)
def create_counselor(payload: CounselorCreate):
    try:
        db.add_counselor(**payload.model_dump())
        return {"message": "Counselor added successfully."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create counselor.")


@router.put("/{counselor_id}")
def update_counselor(counselor_id: int, payload: CounselorUpdate):
    if not db.counselor_exists(counselor_id):
        raise HTTPException(status_code=404, detail=f"Counselor {counselor_id} not found.")
    try:
        db.update_counselor(counselor_id, **payload.model_dump())
        return {"message": f"Counselor {counselor_id} updated successfully."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update counselor.")


@router.delete("/{counselor_id}")
def delete_counselor(counselor_id: int):
    if not db.counselor_exists(counselor_id):
        raise HTTPException(status_code=404, detail=f"Counselor {counselor_id} not found.")
    try:
        db.delete_counselor(counselor_id)
        return {"message": f"Counselor {counselor_id} deleted successfully."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete counselor.")
