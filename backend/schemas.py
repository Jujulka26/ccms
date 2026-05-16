from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
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
    about_me: Optional[str] = None
    expertise_tags: Optional[str] = None
    helpful_thought_1: Optional[str] = None
    helpful_thought_2: Optional[str] = None
    modality_desc: Optional[str] = None
    image: Optional[str] = None


class CounselorCreate(CounselorBase):
    pass


class CounselorUpdate(CounselorBase):
    pass


class CounselorResponse(CounselorBase):
    counselor_id: int

    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    success: bool


class IntroRequestCreate(BaseModel):
    client_name: str
    client_email: str
    counselor_id: int
    compatibility_score: float
    outcome_consent: bool = False
    client_age: Optional[int] = None
    client_gender: Optional[str] = None
    client_ethnicity: Optional[str] = None
    client_issue: Optional[str] = None
    prev_exp: Optional[int] = None
    preferred_language: Optional[str] = None
    preferred_modality: Optional[str] = None
    preferred_c_gender: Optional[str] = None


class RequestResponse(BaseModel):
    request_id: int
    client_name: str
    client_email: str
    counselor_name: str
    compatibility_score: Optional[float] = None
    status: str
    created_at: Optional[datetime] = None
    match_outcome: Optional[str] = None
    outcome_consent: Optional[int] = None


class UpdateRequestStatus(BaseModel):
    status: str


class UpdateMatchOutcome(BaseModel):
    outcome: str

    @field_validator("outcome")
    @classmethod
    def valid_outcome(cls, v):
        allowed = {"Successful", "Unsuccessful"}
        if v not in allowed:
            raise ValueError(f"outcome must be one of {allowed}")
        return v


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
    exclude_ids: List[int] = []


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
    about_me: Optional[str] = None
    expertise_tags: Optional[str] = None
    helpful_thought_1: Optional[str] = None
    helpful_thought_2: Optional[str] = None
    modality_desc: Optional[str] = None
    image: Optional[str] = None
    compatibility_score: float
    issue_match: float
    modality_match: int
    gender_match: int
    ethnicity_match: int
    features: Optional[Dict[str, float]] = None


class MatchResponse(BaseModel):
    top_match: Optional[MatchedCounselor] = None
    second_match: Optional[MatchedCounselor] = None
    matches: Optional[List[MatchedCounselor]] = None
    best_features: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class ReferenceDataResponse(BaseModel):
    client_gender: List[str]
    client_ethnicity: List[str]
    client_issue: List[str]
    preferred_modality: List[str]
    preferred_language: List[str]
    preferred_counselor_gender: List[str]


class ShapRequest(BaseModel):
    features: Dict[str, float]


class ShapResponse(BaseModel):
    shap_values: List[float]
    base_value: float
    feature_names: List[str]
    feature_values: List[float]
    error: Optional[str] = None


class ModelPerformanceResponse(BaseModel):
    models: List[Dict[str, Any]]
    best_model: str
    best_roc_auc: float
    model_count: int
    deployed_model: str
    tuning_models: List[Dict[str, Any]]
