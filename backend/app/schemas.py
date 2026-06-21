from typing import Any
from pydantic import BaseModel
from datetime import datetime


class CounselorBase(BaseModel):
    name: str
    age: int
    gender: str
    ethnicity: str
    specialization: str
    counselor_language: str
    counselor_modality: str
    experience_years: int
    about_me: str | None = None
    expertise_tags: str | None = None
    helpful_thought_1: str | None = None
    helpful_thought_2: str | None = None
    modality_desc: str | None = None
    image: str | None = None


class CounselorCreate(CounselorBase):
    availability: list[str] = []


class CounselorUpdate(CounselorBase):
    availability: list[str] = []


class CounselorResponse(CounselorBase):
    counselor_id: int
    caseload: int = 0           # computed: open cases (pending + approved)
    availability: str | None = None  # computed: comma-joined time blocks

    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class IntroRequestCreate(BaseModel):
    client_name: str
    client_email: str
    counselor_id: int
    compatibility_score: float
    client_age: int | None = None
    client_gender: str | None = None
    client_ethnicity: str | None = None
    client_issue: str | None = None
    prev_exp: int | None = None
    preferred_language: str | None = None
    preferred_modality: str | None = None
    preferred_c_gender: str | None = None


class RequestResponse(BaseModel):
    request_id: int
    client_name: str
    client_email: str
    counselor_name: str
    compatibility_score: float | None = None
    status: str
    created_at: datetime | None = None
    client_age: int | None = None
    client_gender: str | None = None
    client_ethnicity: str | None = None
    client_issue: str | None = None
    prev_exp: int | None = None
    preferred_language: str | None = None
    preferred_modality: str | None = None
    preferred_c_gender: str | None = None


class UpdateRequestStatus(BaseModel):
    status: str


class EnquiryRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str


class ApprovalEmailRequest(BaseModel):
    client_name: str
    client_email: str
    counselor_name: str


class MatchRequest(BaseModel):
    client_age: int
    client_gender: str
    client_ethnicity: str
    client_issue: str
    prev_exp: int
    preferred_language: str
    preferred_modality: str
    preferred_c_gender: str
    preferred_time: str = "Any time"
    exclude_ids: list[int] = []


class MatchedCounselor(BaseModel):
    counselor_id: int
    name: str
    age: int
    gender: str
    ethnicity: str
    specialization: str
    counselor_language: str
    counselor_modality: str
    experience_years: int
    caseload: int = 0
    availability: str | None = None
    about_me: str | None = None
    expertise_tags: str | None = None
    helpful_thought_1: str | None = None
    helpful_thought_2: str | None = None
    modality_desc: str | None = None
    image: str | None = None
    compatibility_score: float
    issue_match: float
    modality_match: int
    gender_match: int
    ethnicity_match: int
    features: dict[str, float] | None = None


class MatchResponse(BaseModel):
    top_match: MatchedCounselor | None = None
    second_match: MatchedCounselor | None = None
    matches: list[MatchedCounselor] | None = None
    best_features: dict[str, float] | None = None
    error: str | None = None


class ReferenceDataResponse(BaseModel):
    client_gender: list[str]
    client_ethnicity: list[str]
    client_issue: list[str]
    preferred_modality: list[str]
    preferred_language: list[str]
    preferred_counselor_gender: list[str]
    preferred_time: list[str]


class ShapRequest(BaseModel):
    features: dict[str, float]


class ShapResponse(BaseModel):
    shap_values: list[float]
    base_value: float
    feature_names: list[str]
    feature_values: list[float]
    error: str | None = None


class ModelPerformanceResponse(BaseModel):
    models: list[dict[str, Any]]
    best_model: str
    best_roc_auc: float
    model_count: int
    deployed_model: str
    tuning_models: list[dict[str, Any]]
