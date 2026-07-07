import pandas as pd

from src.ml.model_loader import load_models


MODEL_TARGET_LABELS = {
    "total_cost": "Total Cost",
    "duration": "Construction Duration",
    "material_index": "Material Index",
    "manpower_hours_per_km": "Manpower Hours per km",
    "machinery_hours_per_km": "Machinery Hours per km",
}


def get_final_estimator(model):
    if hasattr(model, "steps"):
        return model.steps[-1][1]
    return model


def get_feature_names_from_pipeline(model):
    if not hasattr(model, "steps"):
        return None

    preprocessor = model.steps[0][1]

    if hasattr(preprocessor, "get_feature_names_out"):
        feature_names = preprocessor.get_feature_names_out()
        return [
            name.replace("cat__", "").replace("remainder__", "")
            for name in feature_names
        ]

    return None


def get_single_model_feature_importance(model):
    estimator = get_final_estimator(model)

    if not hasattr(estimator, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])

    importances = estimator.feature_importances_
    feature_names = get_feature_names_from_pipeline(model)

    if feature_names is None or len(feature_names) != len(importances):
        feature_names = [f"feature_{i}" for i in range(len(importances))]

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    })

    importance_df = (
        importance_df
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    return importance_df


def get_model_feature_importance():
    models = load_models()
    importance_dict = {}

    for target_name, model in models.items():
        importance_dict[target_name] = get_single_model_feature_importance(model)

    return importance_dict


def get_combined_feature_importance():
    importance_dict = get_model_feature_importance()

    rows = []

    for target_name, importance_df in importance_dict.items():
        if importance_df.empty:
            continue

        temp_df = importance_df.copy()
        temp_df["target"] = MODEL_TARGET_LABELS.get(target_name, target_name)
        rows.append(temp_df)

    if not rows:
        return pd.DataFrame(columns=["feature", "importance", "target"])

    return pd.concat(rows, ignore_index=True)