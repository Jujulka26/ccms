from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.schemas import ModelPerformanceResponse
import pandas as pd

router = APIRouter(prefix="/model-performance", tags=["model-performance"])

BASE_DIR = Path(__file__).parent.parent.parent

DEPLOYED_MODEL = "Ensemble (LGBM+Cat)"


@router.get("/", response_model=ModelPerformanceResponse)
def get_model_performance():
    csv_path        = BASE_DIR / "model_results.csv"
    ensemble_csv    = BASE_DIR / "ensemble_comparison.csv"

    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="model_results.csv not found. Please run training first.")

    try:
        df = pd.read_csv(str(csv_path))
        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df["Overall"] = df[metric_cols].mean(axis=1)
        top_baseline = df.sort_values("Overall", ascending=False).iloc[0]

        tuning_models = []
        best_roc = float(df["ROC-AUC"].max())

        if ensemble_csv.exists():
            df_ensemble = pd.read_csv(str(ensemble_csv))
            tuning_models = df_ensemble.to_dict(orient="records")
            ens_row = df_ensemble[df_ensemble["Model"].str.contains("Ensemble", case=False)]
            if not ens_row.empty:
                best_roc = float(ens_row["ROC-AUC"].iloc[0])

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
