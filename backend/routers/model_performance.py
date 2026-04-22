from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.schemas import ModelPerformanceResponse
import pandas as pd

router = APIRouter(prefix="/model-performance", tags=["model-performance"])

BASE_DIR = Path(__file__).parent.parent.parent


@router.get("/", response_model=ModelPerformanceResponse)
def get_model_performance():
    csv_path = BASE_DIR / "model_results.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="model_results.csv not found. Please run training first.")
    try:
        df = pd.read_csv(str(csv_path))
        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df["Overall"] = df[metric_cols].mean(axis=1)
        top = df.sort_values("Overall", ascending=False).iloc[0]
        return {
            "models": df.drop(columns=["Overall"]).to_dict(orient="records"),
            "best_model": str(top["Model"]),
            "best_roc_auc": float(df["ROC-AUC"].max()),
            "model_count": len(df),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
