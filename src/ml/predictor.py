import pandas as pd
import streamlit as st
import numpy as np

from src.ml.feature_schema import MODEL_FEATURES
from src.ml.model_loader import load_models
from src.ml.engineering_features import add_engineered_features

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
    road_length = float(project_data.get("road_length_km", 50))
    lanes = int(project_data.get("number_of_lanes", 4))
    terrain = project_data.get("terrain_type", "Plain")
    risk = project_data.get("risk_level", "Medium")
    rainfall_zone = project_data.get("rainfall_zone", "Moderate")
    road_category = project_data.get("road_category", "National Highway")
    project_type = project_data.get("project_type", "New Construction")
    utility_yes = (
        str(project_data.get("utility_shifting_required", "No")).strip().lower() == "yes"
    )
    
    project_type_config = {
        "New Construction": {
            "traffic_complexity_add": 0,
            "utility_add": 0,
            "working_days_penalty": 0,
        },
        "Road Upgrade": {
            "traffic_complexity_add": 0,
            "utility_add": 3,
            "working_days_penalty": 0,
        },
        "Rehabilitation": {
            "traffic_complexity_add": 1,
            "utility_add": 3,
            "working_days_penalty": 1,
        },
        "Widening": {
            "traffic_complexity_add": 1,
            "utility_add": 12,
            "working_days_penalty": 2,
        },
        "Elevated Corridor": {
            "traffic_complexity_add": 2,
            "utility_add": 25,
            "working_days_penalty": 4,
        },
        "Expressway": {
            "traffic_complexity_add": 0,
            "utility_add": 5,
            "working_days_penalty": 0,
        },
        "Bypass": {
            "traffic_complexity_add": 0,
            "utility_add": 2,
            "working_days_penalty": 0,
        },
    }

    type_cfg = project_type_config.get(
        project_type,
        project_type_config["New Construction"],
    )

    terrain_map = {
        "Plain": 0,
        "Rolling": 1,
        "Hilly": 2,
        "Mountainous": 3,
    }

    terrain_class = terrain_map.get(terrain, 0)

    rainfall_map = {
        "Low": 800,
        "Moderate": 1300,
        "High": 2000,
        "Very High": 2800,
    }

    rain_delay_map = {
        "Low": 4,
        "Moderate": 10,
        "High": 24,
        "Very High": 40,
    }

    risk_map = {
        "Low": 0,
        "Medium": 1,
        "High": 2,
    }

    road_category_base_cost = {
        "Rural Road": 120,
        "Urban Road": 180,
        "State Highway": 220,
        "National Highway": 280,
        "Expressway": 650,
    }

    pavement_type_map = {
        "Flexible": 0,
        "Rigid": 1,
        "Composite": 2,
    }

    soil_map = {
        "Clayey": "CL",
        "Silty": "ML",
        "Sandy": "SM",
        "Gravelly": "GP",
        "Black Cotton Soil": "CH",
        "Rocky": "GW",
    }

    bridges_culverts = int(project_data.get("bridges_culverts", 0))

    if terrain_class == 0:  # Plain
        num_major_bridges = max(0, int(bridges_culverts * 0.03))
        num_minor_bridges = max(0, int(bridges_culverts * 0.12))
    elif terrain_class == 1:  # Rolling
        num_major_bridges = max(0, int(bridges_culverts * 0.05))
        num_minor_bridges = max(0, int(bridges_culverts * 0.18))
    elif terrain_class == 2:  # Hilly
        num_major_bridges = max(0, int(bridges_culverts * 0.08))
        num_minor_bridges = max(0, int(bridges_culverts * 0.25))
    else:  # Mountainous
        num_major_bridges = max(0, int(bridges_culverts * 0.10))
        num_minor_bridges = max(0, int(bridges_culverts * 0.30))

    num_culverts = max(0, bridges_culverts - num_major_bridges - num_minor_bridges) 
        
    carriageway_width = float(project_data.get("carriageway_width_m", 14))
    shoulder_width = float(project_data.get("shoulder_width_m", 2.5))

    gsb = float(project_data.get("gsb_thickness_mm", 200))
    wmm = float(project_data.get("wmm_thickness_mm", 250))
    dbm = float(project_data.get("dbm_thickness_mm", 100))
    bc = float(project_data.get("bc_thickness_mm", 40))
    concrete = float(project_data.get("concrete_thickness_mm", 0))

    material_quality = float(project_data.get("material_quality_index", 80))
    aggregate_distance = float(project_data.get("aggregate_source_distance_km", 25))
    fuel_cost = float(project_data.get("fuel_cost_inr_litre", 95))
    
    if terrain_class == 0:
        average_haul_distance = max(8, aggregate_distance*0.6)
        quarry_distance = max(8, aggregate_distance*0.6)
        borrow_distance = max(5, aggregate_distance*0.3)
    else:
        average_haul_distance = aggregate_distance
        quarry_distance = aggregate_distance
        borrow_distance = max(8, aggregate_distance * 0.55)
    
    contractor_exp = float(project_data.get("contractor_experience_index", 80))
    equipment_prod = float(project_data.get("equipment_productivity_index", 80))
    machinery_avail = float(project_data.get("machinery_availability_pct", 85))
    skilled_labour = float(project_data.get("skilled_labour_pct", 40))

    stabilization_yes = project_data.get("soil_stabilization_required", "No") == "Yes"

    avg_rainfall = rainfall_map.get(rainfall_zone, 1300)
    rain_delay = rain_delay_map.get(rainfall_zone, 25)

    # Terrain-dependent quantities
    cut_volume = road_length * (1800 + 900 * terrain_class)
    fill_volume = road_length * (1600 + 700 * terrain_class)
    rock_excavation = min(75, 4 + terrain_class * 18 + (10 if stabilization_yes else 0))

    avg_gradient = {
        0: 1.5,
        1: 3.5,
        2: 6.0,
        3: 9.0,
    }[terrain_class]

    avg_side_slope = {
        0: 2.0,
        1: 1.8,
        2: 1.5,
        3: 1.2,
    }[terrain_class]

    project_type_multiplier = {
        "New Construction": 1.00,
        "Road Upgrade": 0.55,
        "Rehabilitation": 0.45,
        "Widening": 0.75,
        "Elevated Corridor": 2.80,
        "Expressway": 1.80,
        "Bypass": 1.20,
    }

    base_cost = road_category_base_cost.get(road_category, 280)
    base_cost *= project_type_multiplier.get(project_type, 1.0)
    base_cost *= 1 + terrain_class * 0.25
    base_cost *= 1 + risk_map.get(risk, 1) * 0.08

    # Convert GUI cost/resource inputs into model-style indices
    quality_factor = material_quality / 100 if material_quality > 0 else 0.8

    # Convert quality and logistics into market-style price indices.
    distance_factor = min(0.25, aggregate_distance / 200)
    quality_penalty = (100 - material_quality) / 100
    
    # -------------------------------------------------
    # MARKET PRICE INDICES
    # (Matches training dataset scale ~60–200)
    # -------------------------------------------------

    quality = float(project_data.get("material_quality_index", 80))
    aggregate_distance = float(project_data.get("aggregate_source_distance_km", 20))
    fuel_cost = float(project_data.get("fuel_cost_inr_litre", 95))

    terrain_multiplier = {
        0: 1.00,
        1: 1.05,
        2: 1.12,
        3: 1.20,
    }[terrain_class]

    risk_multiplier = {
        "Low": 1.00,
        "Medium": 1.05,
        "High": 1.12,
    }.get(risk, 1.00)

    distance_factor = aggregate_distance / 100.0
    quality_penalty = (100 - quality) / 100.0
    regional_cost_index = (
        100
        * terrain_multiplier
        * risk_multiplier
    )
    bitumen_price_index = (
        100
        + 0.60 * quality
        + 0.35 * aggregate_distance
    )
    cement_price_index = (
        100
        + 0.40 * quality
        + 0.22 * aggregate_distance
    )
    steel_price_index = (
        100
        + 0.45 * quality
        + 0.30 * aggregate_distance
    )
    diesel_price_index = (
        fuel_cost * 1.18
    )

    regional_cost_index = np.clip(regional_cost_index, 70, 190)
    bitumen_price_index = np.clip(bitumen_price_index, 50, 200)
    cement_price_index = np.clip(cement_price_index, 60, 200)
    steel_price_index = np.clip(steel_price_index, 50, 200)
    diesel_price_index = np.clip(diesel_price_index, 60, 200)

    base_traffic_complexity = risk_map.get(risk, 1)
    traffic_management_complexity = min(
        3,
        base_traffic_complexity + type_cfg["traffic_complexity_add"]
    )
    base_utility_index = 45 if utility_yes else 8
    utility_relocation_index = min(
        100,
        base_utility_index + type_cfg["utility_add"]
    )
    working_days_per_month = (
        24 if rainfall_zone in ["Low", "Moderate"] else 21
    )
    working_days_per_month = max(
        18,
        working_days_per_month - type_cfg["working_days_penalty"]
    )

    feature_values = {
        "project_year": 2026,
        "length_km": road_length,
        "num_lanes": lanes,
        "design_speed_kmh": float(project_data.get("design_speed_kmph", 100)),
        "carriageway_width_m": carriageway_width,
        "shoulder_width_m": shoulder_width,
        "median_width_m": 1.5 if lanes <= 4 else 3.0,

        "terrain_class": terrain_class,
        "state_region": project_data.get("location", "Uttar Pradesh"),
        "pavement_type": pavement_type_map.get(project_data.get("pavement_type", "Flexible"), 0),
        "design_life_years": 20,
        "reliability_pct": 90,
        "serviceability_loss": 2.0,

        "subgrade_cbr": float(project_data.get("subgrade_cbr_pct", 8)),
        "soil_type_predominant": soil_map.get(project_data.get("soil_type", "Sandy"), "SM"),

        "avg_annual_rainfall_mm": avg_rainfall,
        "groundwater_depth_m": max(1.5, float(project_data.get("water_body_distance_m", 500)) / 200),
        "seismic_zone": 3 + (1 if terrain_class >= 2 else 0),

        "avg_gradient_pct": avg_gradient,
        "avg_side_slope_ratio": avg_side_slope,
        "drainage_coefficient": 0.9 if rainfall_zone in ["High", "Very High"] else 1.0,

        "gsb_thickness_mm": gsb,
        "wmm_thickness_mm": wmm,
        "dbm_thickness_mm": dbm,
        "bc_thickness_mm": bc,
        "rigid_pavement_thickness_mm": concrete,
        "total_pavement_thickness_mm": gsb + wmm + dbm + bc + concrete,

        "aadt": float(project_data.get("aadt", 10000)),
        "vdf": float(project_data.get("vdf", 3.5)),
        "pct_commercial_vehicles": min(55, 25 + float(project_data.get("traffic_growth_rate_pct", 5)) * 2),
        "traffic_management_complexity": traffic_management_complexity,

        "num_major_bridges": num_major_bridges,
        "num_minor_bridges": num_minor_bridges,
        "num_culverts": num_culverts,
        "total_bridge_deck_area_sqm": num_major_bridges * 600 + num_minor_bridges * 120,
        "total_culvert_length_m": num_culverts * 8,

        "num_tunnels": 0 if terrain_class < 2 else max(0, int(road_length / 80)),
        "total_tunnel_length_m": 0 if terrain_class < 2 else max(0, int(road_length / 80)) * 700,
        "retaining_wall_length_m": road_length * terrain_class * 15,

        "num_interchanges": 0 if road_category not in ["Expressway", "National Highway"] else max(1, int(road_length / 50)),
        "has_toll_plaza": 1 if road_category in ["Expressway", "National Highway"] else 0,
        "has_truck_laybys": 1 if road_category in ["Expressway", "National Highway"] else 0,
        "has_rest_areas": 1 if road_category == "Expressway" else 0,

        "cut_volume_cum": cut_volume,
        "fill_volume_cum": fill_volume,
        "net_earthwork_cum": abs(cut_volume - fill_volume),
        "rock_excavation_pct": rock_excavation,
        "swell_factor_pct": 12 + terrain_class * 2,
        "shrinkage_factor_pct": 8 + terrain_class,

        "average_haul_distance_km": average_haul_distance,
        "borrow_area_distance_km": borrow_distance,
        "quarry_distance_km": quarry_distance,

        "blasting_required": 1 if terrain_class >= 2 or rock_excavation > 30 else 0,
        "utility_relocation_index": utility_relocation_index,
        "working_days_per_month": working_days_per_month,
        "rain_delay_days_per_year": rain_delay,

        "crew_size": 80 + road_length * 0.8 + terrain_class * 20,
        "labour_productivity_index": contractor_exp * 0.6 + skilled_labour * 0.4,
        "equipment_availability_pct": machinery_avail,
        "equipment_utilization_pct": equipment_prod,
        "contractor_efficiency_score": contractor_exp,

        "base_cost_lakhs_per_km": base_cost,
        "regional_cost_index": regional_cost_index,
        "diesel_price_index": diesel_price_index,
        "bitumen_price_index": bitumen_price_index,
        "cement_price_index": cement_price_index,
        "steel_price_index": steel_price_index,

        "foreign_currency_component_pct": 5 if road_category == "Expressway" else 2,
        "gst_pct": 18,
        "labour_cess_pct": 1,
        "overhead_pct": 8 + risk_map.get(risk, 1),
        "profit_pct": 8,
        "contingency_pct": float(project_data.get("contingency_pct", 5)),
        "escalation_pct_per_annum": float(project_data.get("escalation_pct", 5)),
        "price_escalation_years": 2,
    }

    input_df = pd.DataFrame([feature_values])

    # Ensure all training features exist
    for feature in MODEL_FEATURES:
        if feature not in input_df.columns:
            if feature == "state_region":
                input_df[feature] = "Uttar Pradesh"
            elif feature == "soil_type_predominant":
                input_df[feature] = "SM"
            else:
                input_df[feature] = 0

    input_df = input_df[MODEL_FEATURES]

    categorical_columns = ["state_region", "soil_type_predominant"]

    for col in input_df.columns:
        if col in categorical_columns:
            input_df[col] = input_df[col].astype(str)
        else:
            input_df[col] = pd.to_numeric(input_df[col], errors="coerce").fillna(0)

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
    input_df = add_engineered_features(input_df)

    models = load_models()
    predictions = {}

    # Model predictions
    for target_name, model in models.items():
        prediction = float(model.predict(input_df)[0])
        predictions[target_name] = prediction

    # Project-specific rules
    project_type = str(
        project_data.get("project_type", "")
    ).strip()

    road_category = str(
        project_data.get("road_category", "")
    ).strip()

    length_km = float(
        project_data.get("road_length_km", 0) or 0
    )

    if (
        road_category == "Rural Road"
        and project_type == "Road Upgrade"
    ):
        predictions["total_cost"] = length_km * 180.0
        predictions["duration"] = max(
            12.0,
            length_km * 1.2,
        )
        predictions["manpower_hours_per_km"] = min(
            predictions["manpower_hours_per_km"],
            5900.0,
        )
        predictions["machinery_hours_per_km"] = min(
            predictions["machinery_hours_per_km"],
            4400.0,
        )
    elif (
        road_category == "National Highway"
        and project_type == "Widening"
    ):
        predictions["total_cost"] *= 1.30
        predictions["duration"] *= 1.20

    # Final prediction guards
    predictions["total_cost"] = float(
        max(predictions["total_cost"], 1000.0)
    )

    predictions["duration"] = float(
        np.clip(
            predictions["duration"],
            12.0,
            220.0,
        )
    )

    predictions["material_index"] = float(
        np.clip(
            predictions["material_index"],
            123.0,
            150.0,
        )
    )

    predictions["manpower_hours_per_km"] = float(
        np.clip(
            predictions["manpower_hours_per_km"],
            5000.0,
            8000.0,
        )
    )

    predictions["machinery_hours_per_km"] = float(
        np.clip(
            predictions["machinery_hours_per_km"],
            3500.0,
            6500.0,
        )
    )

    return {
        "success": True,
        "missing_features": [],
        "predictions": predictions,
    }