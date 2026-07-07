import pandas as pd

from src.ml.feature_schema import MODEL_FEATURES
from src.ml.model_loader import load_models


def get_default_value_raw(feature):
    defaults = {
        "project_year": 2026,
        "length_km": 42,
        "num_lanes": 4,
        "design_speed_kmh": 100,
        "carriageway_width_m": 14,
        "shoulder_width_m": 2.5,
        "median_width_m": 1.5,
        "terrain_class": "Plain",
        "state_region": "Uttar Pradesh",
        "pavement_type": "Flexible",
        "design_life_years": 15,
        "reliability_pct": 90,
        "serviceability_loss": 1.7,
        "subgrade_cbr": 8,
        "soil_type_predominant": "Sandy",
        "avg_annual_rainfall_mm": 850,
        "groundwater_depth_m": 5,
        "seismic_zone": "Zone III",
        "avg_gradient_pct": 2,
        "avg_side_slope_ratio": 2,
        "drainage_coefficient": 1.0,
        "gsb_thickness_mm": 200,
        "wmm_thickness_mm": 250,
        "dbm_thickness_mm": 80,
        "bc_thickness_mm": 40,
        "rigid_pavement_thickness_mm": 0,
        "total_pavement_thickness_mm": 570,
        "vdf": 4.5,
        "pct_commercial_vehicles": 35,
        "traffic_management_complexity": "Medium",
        "num_major_bridges": 1,
        "num_minor_bridges": 3,
        "num_culverts": 8,
        "total_bridge_deck_area_sqm": 1200,
        "total_culvert_length_m": 240,
        "num_tunnels": 0,
        "total_tunnel_length_m": 0,
        "retaining_wall_length_m": 300,
        "num_interchanges": 1,
        "has_toll_plaza": "Yes",
        "has_truck_laybys": "Yes",
        "has_rest_areas": "No",
        "blasting_required": "No",
        "cut_volume_cum": 120000,
        "fill_volume_cum": 95000,
        "net_earthwork_cum": 25000,
        "rock_excavation_pct": 10,
        "swell_factor_pct": 12,
        "shrinkage_factor_pct": 8,
        "average_haul_distance_km": 15,
        "borrow_area_distance_km": 20,
        "quarry_distance_km": 35,
        "utility_relocation_index": 40,
        "working_days_per_month": 24,
        "rain_delay_days_per_year": 25,
        "crew_size": 120,
        "labour_productivity_index": 75,
        "equipment_availability_pct": 82,
        "equipment_utilization_pct": 78,
        "contractor_efficiency_score": 72,
        "base_cost_lakhs_per_km": 750,
        "regional_cost_index": 1.05,
        "diesel_price_index": 1.1,
        "bitumen_price_index": 1.08,
        "cement_price_index": 1.04,
        "steel_price_index": 1.07,
        "foreign_currency_component_pct": 5,
        "gst_pct": 18,
        "labour_cess_pct": 1,
        "overhead_pct": 8,
        "profit_pct": 10,
        "escalation_pct_per_annum": 5,
        "price_escalation_years": 2,
        "aadt": 32000,
        "contingency_pct": 8,
    }

    return defaults.get(feature, 0)


def validate_project_features(project_data):
    required_gui_fields = [
        "road_length_km",
        "number_of_lanes",
        "design_speed_kmph",
        "terrain_type",
        "location",
        "subgrade_cbr_pct",
        "soil_type",
        "risk_level",
    ]

    missing = []

    for field in required_gui_fields:
        value = project_data.get(field)
        if value is None or value == "":
            missing.append(field)

    return missing
    
def encode_categorical_value(feature, value):
    mappings = {
        "terrain_class": {
            "Plain": 1,
            "Rolling": 2,
            "Hilly": 3,
            "Mountainous": 4,
        },
        "state_region": {
            "Uttar Pradesh": 1,
            "Maharashtra": 2,
            "Rajasthan": 3,
            "Himachal Pradesh": 4,
            "Other": 5,
        },
        "pavement_type": {
            "Flexible": 1,
            "Rigid": 2,
            "Composite": 3,
        },
        "soil_type_predominant": {
            "Clayey": 1,
            "Sandy": 2,
            "Silty": 3,
            "Gravelly": 4,
            "Black Cotton Soil": 5,
            "Rocky": 6,
        },
        "seismic_zone": {
            "Zone II": 2,
            "Zone III": 3,
            "Zone IV": 4,
            "Zone V": 5,
        },
        "traffic_management_complexity": {
            "Low": 1,
            "Medium": 2,
            "High": 3,
        },
        "has_toll_plaza": {
            "No": 0,
            "Yes": 1,
        },
        "has_truck_laybys": {
            "No": 0,
            "Yes": 1,
        },
        "has_rest_areas": {
            "No": 0,
            "Yes": 1,
        },
        "blasting_required": {
            "No": 0,
            "Yes": 1,
        },
    }

    if feature in mappings and isinstance(value, str):
        return mappings[feature].get(value, 0)

    return value

CATEGORICAL_FEATURES = [
    "road_category",
    "terrain_type",
    "project_stage",
    "pavement_type",
    "soil_type",
    "bitumen_grade",
    "cement_grade",
    "land_acquisition_complexity",
    "rainfall_zone",
    "utility_shifting_required",
    "environmental_sensitivity",
    "soil_stabilization_required",
    "risk_level",
]

def prepare_features(project_data):
    feature_values = {
        "length_km": project_data.get("road_length_km", 10),
        "num_lanes": project_data.get("number_of_lanes", 2),
        "design_speed_kmh": project_data.get("design_speed_kmph", 80),
        "terrain_class": {
            "Plain": 0,
            "Rolling": 1,
            "Hilly": 2,
            "Mountainous": 3,
        }.get(project_data.get("terrain_type", "Plain"), 0),
        "state_region": "Uttar Pradesh",
        "avg_gradient_pct": 2.0,
        "avg_side_slope_ratio": 2.0,
        "median_width_m": 1.5,
        "design_life_years": 20,
        "serviceability_loss": 2.0,
        "reliability_pct": 90,
        "subgrade_cbr": project_data.get("subgrade_cbr_pct", 8),
        "soil_type_predominant": {
            "Clayey": "CL",
            "Silty": "ML",
            "Sandy": "SM",
            "Gravelly": "GP",
            "Black Cotton Soil": "CH",
            "Rocky": "GW",
        }.get(project_data.get("soil_type", "Sandy"), "SM"),
        "total_pavement_thickness_mm": (
            project_data.get("gsb_thickness_mm", 0)
            + project_data.get("wmm_thickness_mm", 0)
            + project_data.get("dbm_thickness_mm", 0)
            + project_data.get("bc_thickness_mm", 0)
            + project_data.get("concrete_thickness_mm", 0)
        ),
        "rigid_pavement_thickness_mm": project_data.get("concrete_thickness_mm", 0),
        "drainage_coefficient": 1.0,
        "avg_annual_rainfall_mm": 900,
        "groundwater_depth_m": 5.0,
        "seismic_zone": 3,
        "num_culverts": project_data.get("bridges_culverts", 0),
        "total_culvert_length_m": project_data.get("bridges_culverts", 0) * 8,
        "num_minor_bridges": 0,
        "num_major_bridges": 0,
        "total_bridge_deck_area_sqm": 0,
        "num_tunnels": 0,
        "total_tunnel_length_m": 0,
        "retaining_wall_length_m": 0,
        "num_interchanges": 0,
        
        "cut_volume_cum": project_data.get("road_length_km", 10) * 2500,
        "fill_volume_cum": project_data.get("road_length_km", 10) * 2200,
        "net_earthwork_cum": project_data.get("road_length_km", 10) * 300,
        "rock_excavation_pct": 5,
        "borrow_area_distance_km": 15,
        "quarry_distance_km": project_data.get("aggregate_source_distance_km", 20),
        "average_haul_distance_km": project_data.get("aggregate_source_distance_km", 20),
        "shrinkage_factor_pct": 8,
        "swell_factor_pct": 12,
        "blasting_required": 0,
        
        "has_toll_plaza": 0,
        "has_truck_laybys": 0,
        "has_rest_areas": 0,
        
        "pct_commercial_vehicles": 35,
        "traffic_management_complexity": {
            "Low": 0,
            "Medium": 1,
            "High": 2
        }.get(project_data.get("risk_level", "Medium"), 1),
        "utility_relocation_index": 30 if project_data.get("utility_shifting_required") == "Yes" else 5,
        "crew_size": 120,
        "working_days_per_month": 24,
        "labour_productivity_index": project_data.get("contractor_experience_index", 70),
        "equipment_utilization_pct": project_data.get("equipment_productivity_index", 75),
        "equipment_availability_pct": project_data.get("machinery_availability_pct", 80),
        "contractor_efficiency_score": project_data.get("contractor_experience_index", 70),
        "project_year": 2026,
        "price_escalation_years": 2,
        "base_cost_lakhs_per_km": 700,
        "regional_cost_index": 1.0,
        "diesel_price_index": project_data.get("fuel_cost_inr_litre", 90),
        "bitumen_price_index": 1.0,
        "cement_price_index": 1.0,
        "steel_price_index": 1.0,
        "gst_pct": 18,
        "labour_cess_pct": 1,
        "overhead_pct": 10,
        "profit_pct": 8,
        "foreign_currency_component_pct": 0,
        "escalation_pct_per_annum": project_data.get("escalation_pct", 5),
        "carriageway_width_m": project_data.get("carriageway_width_m", 7.0),
        "shoulder_width_m": project_data.get("shoulder_width_m", 1.5),
        "aadt": project_data.get("aadt", 10000),
        "vdf": project_data.get("vdf", 3.5),
        "pavement_type": {
            "Flexible": 0,
            "Rigid": 1,
            "Composite": 2,
        }.get(project_data.get("pavement_type", "Flexible"), 0),
        "gsb_thickness_mm": project_data.get("gsb_thickness_mm", 200),
        "wmm_thickness_mm": project_data.get("wmm_thickness_mm", 250),
        "dbm_thickness_mm": project_data.get("dbm_thickness_mm", 100),
        "bc_thickness_mm": project_data.get("bc_thickness_mm", 40),
        "contingency_pct": project_data.get("contingency_pct", 5),
        "rain_delay_days_per_year": 30,
    }
    
    CATEGORICAL_COLUMNS = [
        "state_region",
        "soil_type_predominant",
    ]

    input_df = pd.DataFrame([feature_values])
    for feature in MODEL_FEATURES:
        if feature not in input_df.columns:
            if feature in CATEGORICAL_COLUMNS:
                input_df[feature] = "Uttar Pradesh" if feature == "state_region" else "SM"  # Default categorical value
            else:
                input_df[feature] = 0
                
    input_df = input_df[MODEL_FEATURES]
    
    for col in input_df.columns:
        if col in CATEGORICAL_COLUMNS:
            input_df[col]=input_df[col].astype(str)
        else:
            input_df[col]=pd.to_numeric(input_df[col], errors="coerce").fillna(0)

    return input_df


def prepare_features_raw(project_data):
    feature_values = {}

    for feature in MODEL_FEATURES:
        value = project_data.get(feature, get_default_value_raw(feature))

        if feature in CATEGORICAL_FEATURES:
            value = str(value)

        feature_values[feature] = value

    input_df = pd.DataFrame([feature_values])
    input_df = input_df[MODEL_FEATURES]

    return input_df


def prepare_features_encoded(project_data):
    feature_values = {}

    for feature in MODEL_FEATURES:
        value = project_data.get(feature, get_default_value_raw(feature))
        value = encode_categorical_value(feature, value)
        feature_values[feature] = value

    input_df = pd.DataFrame([feature_values])
    input_df = input_df[MODEL_FEATURES]

    return input_df

def run_prediction(project_data):
    input_df = prepare_features(project_data)
    models = load_models()
    predictions = {}

    for target_name, model in models.items():
        prediction = model.predict(input_df)[0]
        predictions[target_name] = float(prediction)

    return {
        "success": True,
        "missing_features": [],
        "predictions": predictions,
    }