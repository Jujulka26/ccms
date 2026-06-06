from fastapi import APIRouter, HTTPException
from schemas import MatchRequest, MatchResponse, ReferenceDataResponse, ShapRequest, ShapResponse
import ml
import db

router = APIRouter(prefix="/matching", tags=["matching"])


@router.get("/reference-data", response_model=ReferenceDataResponse)
def reference_data():
    try:
        return ml.get_reference_data()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch reference data.")


@router.post("/", response_model=MatchResponse)
def match(payload: MatchRequest):
    try:
        counselors = db.load_counselors()
        result = ml.run_match(payload, counselors)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Matching failed.")


@router.post("/shap", response_model=ShapResponse)
def shap_explain(payload: ShapRequest):
    try:
        result = ml.compute_shap(payload.features)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="SHAP explanation failed.")
