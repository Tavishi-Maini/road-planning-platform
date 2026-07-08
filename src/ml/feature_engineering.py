import pandas as pd

def add_engineered_features(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    eps = 1e-6

    df["total_roadway_width_m"] = df["carriageway_width_m"] + 2 * df["shoulder_width_m"] + df["median_width_m"]
    df["lane_km"] = df["length_km"] * df["num_lanes"]
    df["road_surface_area_sqm"] = df["length_km"] * 1000 * df["carriageway_width_m"]

    df["flexible_pavement_thickness_mm"] = df["bc_thickness_mm"] + df["dbm_thickness_mm"] + df["wmm_thickness_mm"] + df["gsb_thickness_mm"]
    df["pavement_volume_index"] = df["road_surface_area_sqm"] * df["total_pavement_thickness_mm"] / 1000
    df["bituminous_thickness_mm"] = df["bc_thickness_mm"] + df["dbm_thickness_mm"]
    df["granular_thickness_mm"] = df["wmm_thickness_mm"] + df["gsb_thickness_mm"]

    df["total_earthwork_cum"] = df["cut_volume_cum"] + df["fill_volume_cum"]
    df["earthwork_per_km"] = df["total_earthwork_cum"] / (df["length_km"] + eps)
    df["cut_fill_ratio"] = df["cut_volume_cum"] / (df["fill_volume_cum"] + eps)
    df["rock_earthwork_index"] = df["earthwork_per_km"] * df["rock_excavation_pct"] / 100

    df["total_bridges"] = df["num_major_bridges"] + df["num_minor_bridges"]
    df["bridge_density_per_km"] = df["total_bridges"] / (df["length_km"] + eps)
    df["culvert_density_per_km"] = df["num_culverts"] / (df["length_km"] + eps)
    df["tunnel_density_per_km"] = df["num_tunnels"] / (df["length_km"] + eps)
    df["tunnel_length_ratio"] = df["total_tunnel_length_m"] / (df["length_km"] * 1000 + eps)
    df["bridge_area_per_km"] = df["total_bridge_deck_area_sqm"] / (df["length_km"] + eps)
    df["retaining_wall_per_km"] = df["retaining_wall_length_m"] / (df["length_km"] + eps)

    df["structure_complexity_index"] = (
        2.5 * df["num_major_bridges"]
        + 1.2 * df["num_minor_bridges"]
        + 0.4 * df["num_culverts"]
        + 4.0 * df["num_tunnels"]
        + df["total_tunnel_length_m"] / 1000
        + df["retaining_wall_length_m"] / 500
    )

    df["terrain_gradient_index"] = df["terrain_class"] * df["avg_gradient_pct"]
    df["terrain_rock_index"] = df["terrain_class"] * df["rock_excavation_pct"]

    df["weather_severity_index"] = (
        df["avg_annual_rainfall_mm"] / 1000
        + df["rain_delay_days_per_year"] / 30
        + df["seismic_zone"] / 5
    )

    df["commercial_traffic_index"] = df["aadt"] * df["pct_commercial_vehicles"] / 100
    df["traffic_loading_index"] = df["aadt"] * df["pct_commercial_vehicles"] / 100 * df["vdf"]

    df["logistics_distance_index"] = df["average_haul_distance_km"] + df["quarry_distance_km"] + df["borrow_area_distance_km"]
    df["material_transport_stress"] = df["logistics_distance_index"] * df["regional_cost_index"]

    df["productivity_efficiency_index"] = df["labour_productivity_index"] * df["contractor_efficiency_score"] / 100
    df["equipment_efficiency_index"] = df["equipment_utilization_pct"] * df["equipment_availability_pct"] / 100
    df["delay_productivity_penalty"] = df["rain_delay_days_per_year"] * (100 - df["labour_productivity_index"])

    df["economic_price_index"] = (
        df["diesel_price_index"]
        + df["steel_price_index"]
        + df["cement_price_index"]
        + df["bitumen_price_index"]
        + df["regional_cost_index"] * 100
    ) / 5

    df["base_project_cost_proxy"] = df["length_km"] * df["base_cost_lakhs_per_km"]

    df["commercial_markup_pct"] = (
        df["contingency_pct"]
        + df["overhead_pct"]
        + df["profit_pct"]
        + df["labour_cess_pct"]
        + df["gst_pct"]
    )

    df["escalation_factor"] = (1 + df["escalation_pct_per_annum"] / 100) ** df["price_escalation_years"]

    return df