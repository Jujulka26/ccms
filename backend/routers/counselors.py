from fastapi import APIRouter, HTTPException
from backend.schemas import CounselorCreate, CounselorUpdate, CounselorResponse
import backend.db as db

router = APIRouter(prefix="/counselors", tags=["counselors"])


@router.get("/", response_model=list[CounselorResponse])
def get_counselors():
    try:
        return db.load_counselors()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
def create_counselor(payload: CounselorCreate):
    try:
        db.add_counselor(
            payload.name, payload.age, payload.gender, payload.ethnicity,
            payload.specialization, payload.counselor_language, payload.counselor_modality,
            payload.experience_years, payload.about_me, payload.expertise_tags,
            payload.helpful_thought_1, payload.helpful_thought_2,
            payload.modality_desc, payload.image,
        )
        return {"message": "Counselor added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{counselor_id}")
def update_counselor(counselor_id: int, payload: CounselorUpdate):
    try:
        db.update_counselor(
            counselor_id, payload.name, payload.age, payload.gender, payload.ethnicity,
            payload.specialization, payload.counselor_language, payload.counselor_modality,
            payload.experience_years, payload.about_me, payload.expertise_tags,
            payload.helpful_thought_1, payload.helpful_thought_2,
            payload.modality_desc, payload.image,
        )
        return {"message": f"Counselor {counselor_id} updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{counselor_id}")
def delete_counselor(counselor_id: int):
    try:
        db.delete_counselor(counselor_id)
        return {"message": f"Counselor {counselor_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
