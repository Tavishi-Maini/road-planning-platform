from src.database.project_repository import save_project, get_all_projects


def seed_demo_projects():
    existing = get_all_projects()

    if not existing.empty:
        return

    demo_projects = [
        {
            "project_name": "NH-27 Demo Expansion",
            "location": "Uttar Pradesh",
            "project_owner": "NHAI",
            "road_category": "National Highway",
            "project_type": "New Construction",
            "terrain_type": "Plain",
            "project_stage": "DPR",
            "road_length_km": 42,
            "carriageway_width_m": 14,
            "number_of_lanes": 4,
            "shoulder_width_m": 2.5,
            "design_speed_kmph": 100,
            "bridges_culverts": 8,
            "aadt": 28000,
            "traffic_growth_rate_pct": 6,
            "vdf": 3.5,
            "pavement_type": "Flexible",
            "gsb_thickness_mm": 200,
            "wmm_thickness_mm": 250,
            "dbm_thickness_mm": 110,
            "bc_thickness_mm": 40,
            "concrete_thickness_mm": 0,
            "soil_type": "Sandy",
            "subgrade_cbr_pct": 8,
            "bitumen_grade": "VG-30",
            "aggregate_source_distance_km": 22,
            "material_quality_index": 78,
            "cement_grade": "OPC 53",
            "land_acquisition_complexity": "Medium",
            "rainfall_zone": "Moderate",
            "utility_shifting_required": "Yes",
            "environmental_sensitivity": "Medium",
            "water_body_distance_m": 500,
            "soil_stabilization_required": "No",
            "labour_rate_inr_day": 650,
            "skilled_labour_pct": 45,
            "machinery_availability_pct": 82,
            "fuel_cost_inr_litre": 92,
            "equipment_productivity_index": 76,
            "contractor_experience_index": 80,
            "risk_level": "Medium",
            "contingency_pct": 8,
            "escalation_pct": 6,
            "prediction_status": "Pending",
        }
    ]

    for project in demo_projects:
        save_project(project)