import joblib
import streamlit as st
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models"

MODEL_PATHS = {
    "total_cost": MODEL_DIR / "total_cost_model.joblib",
    "duration": MODEL_DIR / "duration_model.joblib",
    "material_index": MODEL_DIR / "material_index_model.joblib",
    "manpower_hours_per_km": MODEL_DIR / "manpower_model.joblib",
    "machinery_hours_per_km": MODEL_DIR / "machinery_model.joblib",
}


@st.cache_resource(show_spinner=False)
def load_models():
    models = {}

    for target_name, model_path in MODEL_PATHS.items():
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}"
            )

        models[target_name] = joblib.load(model_path)

    return models