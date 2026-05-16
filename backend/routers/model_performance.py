from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.schemas import ModelPerformanceResponse
import pandas as pd

router = APIRouter(prefix="/model-performance", tags=["model-performance"])

BASE_DIR = Path(__file__).parent.parent.parent

DEPLOYED_MODEL = "Tuned LightGBM"


@router.get("/", response_model=ModelPerformanceResponse)
def get_model_performance():
    csv_path     = BASE_DIR / "ml" / "train_result.csv"
    tuning_csv   = BASE_DIR / "ml" / "tuned_result.csv"

    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="train_result.csv not found. Please run trainmodels.py first.")

    try:
        df = pd.read_csv(str(csv_path))
        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df["Overall"] = df[metric_cols].mean(axis=1)
        top_baseline = df.sort_values("Overall", ascending=False).iloc[0]

        tuning_models = []
        best_roc = float(df["ROC-AUC"].max())

        if tuning_csv.exists():
            df_tuning    = pd.read_csv(str(tuning_csv))
            tuning_models = df_tuning.to_dict(orient="records")
            tuned_row = df_tuning[df_tuning["Model"].str.contains("Tuned LightGBM", case=False)]
            if not tuned_row.empty:
                best_roc = float(tuned_row["ROC-AUC"].iloc[0])

        return {
            "models": df.drop(columns=["Overall"]).to_dict(orient="records"),
            "best_model": str(top_baseline["Model"]),
            "best_roc_auc": best_roc,
            "model_count": len(df),
            "deployed_model": DEPLOYED_MODEL,
            "tuning_models": tuning_models,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
