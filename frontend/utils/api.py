import streamlit as st
import requests

BASE_URL = "http://localhost:8000"
_BACKEND_CONN_ERROR = "Cannot connect to the backend. Make sure FastAPI is running: `uvicorn backend.main:app --reload`"


def _get(path: str) -> dict | list:
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(_BACKEND_CONN_ERROR)
        st.stop()
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"Backend error: {detail}")
        st.stop()


def _post(path: str, body: dict) -> dict:
    try:
        r = requests.post(f"{BASE_URL}{path}", json=body, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(_BACKEND_CONN_ERROR)
        st.stop()
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"Backend error: {detail}")
        st.stop()


def _put(path: str, body: dict) -> dict:
    try:
        r = requests.put(f"{BASE_URL}{path}", json=body, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(_BACKEND_CONN_ERROR)
        st.stop()
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"Backend error: {detail}")
        st.stop()


def _delete(path: str) -> dict:
    try:
        r = requests.delete(f"{BASE_URL}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(_BACKEND_CONN_ERROR)
        st.stop()
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        st.error(f"Backend error: {detail}")
        st.stop()


# ── Counselors ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_counselors() -> list[dict]:
    return _get("/counselors/")


def add_counselor(data: dict):
    _post("/counselors/", data)


def update_counselor(counselor_id: int, data: dict):
    _put(f"/counselors/{counselor_id}", data)


def delete_counselor(counselor_id: int):
    _delete(f"/counselors/{counselor_id}")


# ── Auth ───────────────────────────────────────────────────────────────────────

def login(email: str, password: str) -> bool:
    result = _post("/auth/login", {"email": email, "password": password})
    return result.get("success", False)


# ── Requests ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_requests() -> list[dict]:
    return _get("/requests/")


def save_intro_request(client_name: str, client_email: str, counselor_id: int, compatibility_score: float):
    _post("/requests/", {
        "client_name": client_name,
        "client_email": client_email,
        "counselor_id": counselor_id,
        "compatibility_score": compatibility_score,
    })


def approve_request(request_id: int):
    _put(f"/requests/{request_id}/approve", {"status": "Approved"})


def send_approval_email(request_id: int, client_name: str, client_email: str, counselor_name: str):
    try:
        r = requests.post(
            f"{BASE_URL}/requests/{request_id}/send-approval-email",
            json={"client_name": client_name, "client_email": client_email, "counselor_name": counselor_name},
            timeout=15,
        )
        r.raise_for_status()
    except Exception as e:
        st.warning(f"Email could not be sent: {e}")


# ── Contact ────────────────────────────────────────────────────────────────────

def send_enquiry_email(name: str, email: str, subject: str, message: str):
    r = requests.post(
        f"{BASE_URL}/contact/send-enquiry",
        json={"name": name, "email": email, "subject": subject, "message": message},
        timeout=15,
    )
    r.raise_for_status()


# ── Matching ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_reference_data() -> dict:
    return _get("/matching/reference-data")


def post_match(data: dict) -> dict:
    return _post("/matching/", data)


def post_shap(features: dict) -> dict:
    return _post("/matching/shap", {"features": features})


# ── Model Performance ──────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def get_model_performance() -> dict:
    return _get("/model-performance/")
