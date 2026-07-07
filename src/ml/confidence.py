def calculate_prediction_confidence(prediction_data, project_data):
    """
    Heuristic confidence estimator.
    Can later be replaced with SHAP uncertainty,
    ensemble variance, prediction intervals, etc.
    """

    score = 100

    # Risk penalty
    risk = project_data.get("risk_level", "Medium")

    if risk == "High":
        score -= 15
    elif risk == "Medium":
        score -= 7

    # Terrain penalty
    terrain = project_data.get("terrain_type", "")

    if terrain in ["Hilly", "Mountainous"]:
        score -= 10

    # Long projects
    if project_data.get("road_length_km", 0) > 80:
        score -= 10

    # Large cost projects
    total_cost = prediction_data.get("total_cost", 0) / 100

    if total_cost > 500:
        score -= 10

    score = max(60, min(score, 99))

    if score >= 90:
        quality = "Excellent"
        status = "High"

    elif score >= 80:
        quality = "Good"
        status = "High"

    elif score >= 70:
        quality = "Moderate"
        status = "Medium"

    else:
        quality = "Low"
        status = "Low"

    return {
        "confidence": score,
        "status": status,
        "quality": quality
    }