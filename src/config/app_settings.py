import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
SETTINGS_PATH = BASE_DIR / "data" / "app_settings.json"


DEFAULT_SETTINGS = {
    "model_dir": "models",
    "database_path": "data/road_projects.db",
    "currency_format": "INR Crore",
    "unit_system": "Metric",
    "theme_mode": "Light",
    "organization_name": "RoadPlan AI",
    "report_title": "Road Construction Planning Report",
    "prepared_by": "Infrastructure Planning Team",
    "show_confidence": True,
}


def load_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

    with open(SETTINGS_PATH, "r") as file:
        saved_settings = json.load(file)

    return {**DEFAULT_SETTINGS, **saved_settings}


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SETTINGS_PATH, "w") as file:
        json.dump(settings, file, indent=4)