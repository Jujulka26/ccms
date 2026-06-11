import io
import json
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File

from schemas import ModelPerformanceResponse

_jobs: dict[str, dict] = {}

router = APIRouter(prefix="/model-performance", tags=["model-performance"])

# app/routers/model_performance.py → parent.parent.parent.parent = ccms/
BASE_DIR     = Path(__file__).parent.parent.parent.parent
ML_DIR       = BASE_DIR / "ml"
STORE_DIR    = BASE_DIR / "model_store"
VERSIONS_DIR = STORE_DIR / "versions"
ACTIVE_FILE  = STORE_DIR / "active_version.txt"

_BEST_MODEL     = ML_DIR / "ensemble_soft.pkl"
_TUNED_CSV      = ML_DIR / "tuned_result.csv"
_BEST_MODEL_BAK = STORE_DIR / "ensemble_soft_backup.pkl"
_TUNED_CSV_BAK  = STORE_DIR / "tuned_result_backup.csv"
_DATASET_CSV    = ML_DIR / "client_counselor_dataset.csv"
_DATASET_BAK    = STORE_DIR / "client_counselor_dataset_backup.csv"

# Raw columns the training scripts (trainmodels.py / tunemodels.py) need to
# engineer features and the target. An uploaded dataset must contain all of these.
REQUIRED_COLUMNS = {
    "client_age", "client_ethnicity", "client_issue",
    "preferred_modality", "preferred_counselor_gender",
    "previous_counseling_experience",
    "counselor_age", "counselor_gender", "counselor_ethnicity",
    "counselor_modality", "specialization", "experience_years",
    "match_success",
}


def _deployed_metrics(tuned_csv: Path) -> dict:
    if not tuned_csv.exists():
        return {}
    df      = pd.read_csv(str(tuned_csv))
    name    = "Soft Vote Ensemble"
    matched = df[df["Model"] == name]
    row     = matched.iloc[0] if not matched.empty else df.loc[df["ROC-AUC"].idxmax()]
    return {
        "accuracy": round(float(row.get("Accuracy", 0)), 3),
        "f1":       round(float(row.get("F1", 0)), 3),
        "roc_auc":  round(float(row.get("ROC-AUC", 0)), 3),
    }


def _get_active_version() -> str:
    return ACTIVE_FILE.read_text().strip() if ACTIVE_FILE.exists() else "legacy"


def _set_active_version(vid: str):
    ACTIVE_FILE.write_text(vid)


def _save_meta(version_dir: Path, meta: dict):
    with open(version_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)


def _load_meta(version_dir: Path) -> dict:
    p = version_dir / "metadata.json"
    return json.loads(p.read_text()) if p.exists() else {}


# ── GET / ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=ModelPerformanceResponse)
def get_model_performance():
    csv_path = ML_DIR / "train_result.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="train_result.csv not found. Run trainmodels.py first.")
    try:
        df = pd.read_csv(str(csv_path))
        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df["Overall"] = df[metric_cols].mean(axis=1)
        top = df.sort_values("Overall", ascending=False).iloc[0]

        tuning_models = []
        best_roc = float(df["ROC-AUC"].max())
        if _TUNED_CSV.exists():
            df_t = pd.read_csv(str(_TUNED_CSV))
            tuning_models = df_t.to_dict(orient="records")
            best_roc = float(df_t["ROC-AUC"].max())

        return {
            "models":         df.drop(columns=["Overall"]).to_dict(orient="records"),
            "best_model":     str(top["Model"]),
            "best_roc_auc":   best_roc,
            "model_count":    len(df),
            "deployed_model": "Soft Vote Ensemble",
            "tuning_models":  tuning_models,
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load model performance data.")


# ── GET /history ──────────────────────────────────────────────────────────────

def _ensure_initial_version():
    STORE_DIR.mkdir(exist_ok=True)
    VERSIONS_DIR.mkdir(exist_ok=True)
    initial_dir = VERSIONS_DIR / "v_initial"
    # Gate on the metadata file, not the directory — a half-created (empty)
    # v_initial dir must still be populated, otherwise history stays empty forever.
    if (initial_dir / "metadata.json").exists():
        return
    if not _BEST_MODEL.exists():
        return
    initial_dir.mkdir(exist_ok=True)
    shutil.copy2(str(_BEST_MODEL), str(initial_dir / "ensemble_soft.pkl"))
    if _TUNED_CSV.exists():
        shutil.copy2(str(_TUNED_CSV), str(initial_dir / "tuned_result.csv"))
    metrics = _deployed_metrics(_TUNED_CSV)
    meta = {
        "version_id":   "v_initial",
        "timestamp":    "2026-01-01T00:00:00",
        "display_date": "Initial model (synthetic baseline)",
        "mode":         "synthetic",
        "rows":         0,
        "metrics":      metrics,
        "is_active":    False,
    }
    _save_meta(initial_dir, meta)
    if not ACTIVE_FILE.exists():
        _set_active_version("v_initial")


@router.get("/history")
def get_history():
    _ensure_initial_version()
    active   = _get_active_version()
    versions = []
    for vdir in sorted(VERSIONS_DIR.iterdir(), reverse=True):
        if not vdir.is_dir():
            continue
        meta = _load_meta(vdir)
        if meta:
            meta["is_active"] = (meta.get("version_id") == active)
            versions.append(meta)
    versions.sort(
        key=lambda v: ("0" if v["version_id"] == "v_initial" else v["version_id"]),
        reverse=True,
    )
    return versions


# ── POST /retrain ─────────────────────────────────────────────────────────────

def _run_training(job_id: str, df: pd.DataFrame):
    job = _jobs[job_id]
    version_dir = None
    try:
        STORE_DIR.mkdir(exist_ok=True)
        VERSIONS_DIR.mkdir(exist_ok=True)

        job["step"]     = "Backing up current model and dataset..."
        job["progress"] = 0.05
        if _BEST_MODEL.exists():
            shutil.copy2(str(_BEST_MODEL), str(_BEST_MODEL_BAK))
        if _TUNED_CSV.exists():
            shutil.copy2(str(_TUNED_CSV), str(_TUNED_CSV_BAK))
        if _DATASET_CSV.exists():
            shutil.copy2(str(_DATASET_CSV), str(_DATASET_BAK))

        old_metrics = _deployed_metrics(_TUNED_CSV_BAK)
        version_id  = "v_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        version_dir = VERSIONS_DIR / version_id
        version_dir.mkdir(exist_ok=True)

        # The uploaded dataset becomes the training input both scripts read.
        row_count = len(df)
        df.to_csv(str(_DATASET_CSV), index=False)

        scripts        = [ML_DIR / "trainmodels.py", ML_DIR / "tunemodels.py"]
        labels         = [
            "Step 1 / 2 — Training models (trainmodels.py)",
            "Step 2 / 2 — Tuning hyperparameters (tunemodels.py)",
        ]
        progress_start = [0.15, 0.55]
        progress_after = [0.55, 0.85]
        output_parts = []

        for idx, (script, label) in enumerate(zip(scripts, labels)):
            if not script.exists():
                shutil.rmtree(str(version_dir), ignore_errors=True)
                job["status"] = "error"
                job["error"]  = f"{script.name} not found."
                return

            job["step"]     = label
            job["progress"] = progress_start[idx]

            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, cwd=str(BASE_DIR),
            )
            output_parts.append(f"=== {script.name} ===\n{result.stdout}")

            if result.returncode != 0:
                shutil.rmtree(str(version_dir), ignore_errors=True)
                job["status"] = "error"
                job["error"]  = f"{script.name} failed:\n{result.stderr}"
                return

            job["progress"] = progress_after[idx]

        job["step"]     = "Saving version artifacts..."
        job["progress"] = 0.90
        new_metrics = _deployed_metrics(_TUNED_CSV)
        if _BEST_MODEL.exists():
            shutil.copy2(str(_BEST_MODEL), str(version_dir / "ensemble_soft.pkl"))
        if _TUNED_CSV.exists():
            shutil.copy2(str(_TUNED_CSV), str(version_dir / "tuned_result.csv"))

        # Leave the active model and dataset exactly as they were — the new
        # version is only deployed when the admin explicitly chooses to.
        if _BEST_MODEL_BAK.exists():
            shutil.copy2(str(_BEST_MODEL_BAK), str(_BEST_MODEL))
        if _TUNED_CSV_BAK.exists():
            shutil.copy2(str(_TUNED_CSV_BAK), str(_TUNED_CSV))
        if _DATASET_BAK.exists():
            shutil.copy2(str(_DATASET_BAK), str(_DATASET_CSV))

        meta = {
            "version_id":   version_id,
            "timestamp":    datetime.now().isoformat(),
            "display_date": datetime.now().strftime("%d %b %Y, %H:%M"),
            "mode":         "uploaded",
            "rows":         row_count,
            "metrics":      new_metrics,
            "is_active":    False,
        }
        _save_meta(version_dir, meta)

        job["status"]   = "done"
        job["step"]     = "Complete"
        job["progress"] = 1.0
        job["result"]   = {
            "version_id":  version_id,
            "message":     "Training complete. Review metrics and deploy when ready.",
            "output":      "\n".join(output_parts),
            "old_metrics": old_metrics,
            "new_metrics": new_metrics,
            "rows":        row_count,
        }
    except Exception as e:
        if version_dir and version_dir.exists():
            shutil.rmtree(str(version_dir), ignore_errors=True)
        # Restore the dataset if training was interrupted mid-way.
        if _DATASET_BAK.exists():
            shutil.copy2(str(_DATASET_BAK), str(_DATASET_CSV))
        job["status"] = "error"
        job["error"]  = str(e)


@router.post("/retrain")
def retrain_model(file: UploadFile = File(...)):
    raw  = file.file.read()
    name = (file.filename or "").lower()
    try:
        if name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(raw))
        elif name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(raw))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload a .csv, .xlsx or .xls file.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the uploaded file. Make sure it is a valid CSV or Excel file.")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Dataset is missing required columns: {', '.join(sorted(missing))}",
        )
    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded dataset has no rows.")

    job_id = uuid.uuid4().hex[:12]
    _jobs[job_id] = {"status": "running", "step": "Initialising...", "progress": 0.0, "result": None, "error": None}
    threading.Thread(target=_run_training, args=(job_id, df), daemon=True).start()
    return {"job_id": job_id, "status": "running"}


@router.get("/retrain/status/{job_id}")
def retrain_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _jobs[job_id]


# ── POST /deploy/{version_id} ─────────────────────────────────────────────────

@router.post("/deploy/{version_id}")
def deploy_version(version_id: str):
    version_dir = VERSIONS_DIR / version_id
    if not version_dir.exists():
        raise HTTPException(status_code=404, detail=f"Version {version_id} not found.")
    pkl = version_dir / "ensemble_soft.pkl"
    csv = version_dir / "tuned_result.csv"
    if not pkl.exists():
        raise HTTPException(status_code=404, detail="ensemble_soft.pkl not found in this version.")
    STORE_DIR.mkdir(exist_ok=True)
    if _BEST_MODEL.exists():
        shutil.copy2(str(_BEST_MODEL), str(_BEST_MODEL_BAK))
    shutil.copy2(str(pkl), str(_BEST_MODEL))
    if csv.exists():
        shutil.copy2(str(csv), str(_TUNED_CSV))
    _set_active_version(version_id)
    return {"message": f"Version {version_id} is now the active model."}


# ── DELETE /versions/{version_id} ────────────────────────────────────────────

@router.delete("/versions/{version_id}")
def delete_version(version_id: str):
    if version_id == "v_initial":
        raise HTTPException(status_code=400, detail="Cannot delete the initial baseline version.")
    version_dir = VERSIONS_DIR / version_id
    if not version_dir.exists():
        raise HTTPException(status_code=404, detail=f"Version {version_id} not found.")
    if version_id == _get_active_version():
        raise HTTPException(status_code=400, detail="Cannot delete the currently active version.")
    shutil.rmtree(str(version_dir))
    return {"message": f"Version {version_id} deleted."}
