import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.database.project_repository import (
    get_all_projects,
    get_project_by_id,
)
from src.ui.components import (
    friendly_error_box,
    metric_card,
    page_header,
)


REQUIRED_PREDICTION_FIELDS = [
    "total_cost",
    "duration",
    "material_index",
    "manpower_hours_per_km",
    "machinery_hours_per_km",
]


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_prediction_data(prediction_data):
    """
    Converts old and new prediction key formats into one standard format.
    """

    if not isinstance(prediction_data, dict):
        return {}

    return {
        "total_cost": prediction_data.get(
            "total_cost",
            prediction_data.get("total_cost_lakhs"),
        ),
        "duration": prediction_data.get(
            "duration",
            prediction_data.get(
                "construction_duration_months"
            ),
        ),
        "material_index": prediction_data.get(
            "material_index"
        ),
        "manpower_hours_per_km": prediction_data.get(
            "manpower_hours_per_km"
        ),
        "machinery_hours_per_km": prediction_data.get(
            "machinery_hours_per_km"
        ),
    }


def load_prediction_data(raw_prediction_data):
    """
    Reads prediction data stored either as JSON text or as a dictionary.
    """

    if raw_prediction_data is None:
        return None

    try:
        if pd.isna(raw_prediction_data):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(raw_prediction_data, str):
        prediction_data = json.loads(raw_prediction_data)

    elif isinstance(raw_prediction_data, dict):
        prediction_data = raw_prediction_data

    else:
        raise TypeError(
            "Saved prediction data has an unsupported format."
        )

    return normalize_prediction_data(prediction_data)


def get_missing_prediction_fields(prediction_data):
    """
    Returns required prediction fields that are missing.
    """

    if not prediction_data:
        return REQUIRED_PREDICTION_FIELDS.copy()

    return [
        field
        for field in REQUIRED_PREDICTION_FIELDS
        if prediction_data.get(field) is None
    ]


def render_comparison():
    page_header(
        "Compare Projects",
        "Compare multiple road construction alternatives side by side",
    )

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning(
            "No projects are available. Create projects first."
        )
        return

    if "prediction_status" not in projects_df.columns:
        st.warning(
            "Prediction status information is unavailable."
        )
        return

    completed_projects = projects_df[
        projects_df["prediction_status"] == "Completed"
    ].copy()

    if completed_projects.empty:
        st.warning(
            "No completed predictions are available. "
            "Run predictions first."
        )
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": int(row.id)
        for row in completed_projects.itertuples()
    }

    selected_labels = st.multiselect(
        "Select projects to compare",
        options=list(project_options.keys()),
        default=list(project_options.keys())[:2],
        key="comparison_project_selector",
    )

    if len(selected_labels) < 2:
        st.info(
            "Select at least two completed projects "
            "for comparison."
        )
        return

    comparison_rows = []
    excluded_projects = []

    for label in selected_labels:
        project_id = project_options[label]
        project_data = get_project_by_id(project_id)

        if project_data is None:
            excluded_projects.append(
                f"{label}: project record could not be loaded"
            )
            continue

        matching_rows = completed_projects[
            completed_projects["id"] == project_id
        ]

        if matching_rows.empty:
            excluded_projects.append(
                f"{label}: completed project record was not found"
            )
            continue

        selected_row = matching_rows.iloc[0]

        try:
            raw_prediction_data = selected_row.get(
                "prediction_data"
            )

            prediction_data = load_prediction_data(
                raw_prediction_data
            )

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as error:
            excluded_projects.append(
                f"{label}: prediction data could not be read "
                f"({error})"
            )
            continue

        missing_fields = get_missing_prediction_fields(
            prediction_data
        )

        if missing_fields:
            excluded_projects.append(
                f"{label}: missing "
                f"{', '.join(missing_fields)}"
            )
            continue

        road_length = safe_float(
            project_data.get("road_length_km")
        )

        total_cost_lakhs = safe_float(
            prediction_data.get("total_cost")
        )

        duration = safe_float(
            prediction_data.get("duration")
        )

        material_index = safe_float(
            prediction_data.get("material_index")
        )

        manpower = safe_float(
            prediction_data.get(
                "manpower_hours_per_km"
            )
        )

        machinery = safe_float(
            prediction_data.get(
                "machinery_hours_per_km"
            )
        )

        cost_per_km_lakhs = (
            total_cost_lakhs / road_length
            if road_length > 0
            else 0.0
        )

        comparison_rows.append(
            {
                "Project ID": project_id,
                "Project Name": project_data.get(
                    "project_name",
                    f"Project {project_id}",
                ),
                "Location": project_data.get(
                    "location",
                    "Unknown",
                ),
                "Road Category": project_data.get(
                    "road_category",
                    "Unknown",
                ),
                "Terrain Type": project_data.get(
                    "terrain_type",
                    "Unknown",
                ),
                "Road Length (km)": road_length,
                "Risk Level": project_data.get(
                    "risk_level",
                    "Unknown",
                ),
                "Total Cost": total_cost_lakhs / 100,
                "Cost per km": cost_per_km_lakhs / 100,
                "Duration (months)": duration,
                "Material Index": material_index,
                "Manpower Hours/km": manpower,
                "Machinery Hours/km": machinery,
            }
        )

    if excluded_projects:
        with st.expander(
            "Projects excluded from comparison",
            expanded=False,
        ):
            for excluded_project in excluded_projects:
                st.warning(excluded_project)

    try:
        comparison_df = pd.DataFrame(comparison_rows)

        if comparison_df.empty:
            st.warning(
                "None of the selected projects contain "
                "complete prediction data."
            )
            return

        if len(comparison_df) < 2:
            st.warning(
                "At least two projects with complete prediction "
                "data are required for comparison."
            )
            return

    except Exception as error:
        friendly_error_box(
            "Project comparison could not be prepared.",
            possible_reasons=[
                "Selected projects do not have completed predictions",
                "Prediction data is missing or corrupted",
                "Comparison fields are incomplete",
            ],
            technical_error=error,
        )
        return

    risk_mapping = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
    }

    comparison_df["Risk Score"] = (
        comparison_df["Risk Level"]
        .map(risk_mapping)
        .fillna(4)
    )

    st.markdown("## Comparison Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Projects Compared",
            len(comparison_df),
            "Completed prediction cases",
        )

    with c2:
        metric_card(
            "Lowest Cost/km",
            (
                f"₹{comparison_df['Cost per km'].min():,.2f} Cr"
            ),
            "Best normalized cost",
        )

    with c3:
        metric_card(
            "Shortest Duration",
            (
                f"{comparison_df['Duration (months)'].min():.2f} "
                "months"
            ),
            "Fastest delivery estimate",
        )

    with c4:
        lowest_risk_project = (
            comparison_df
            .sort_values(
                by=[
                    "Risk Score",
                    "Cost per km",
                ]
            )
            .iloc[0]["Project Name"]
        )

        metric_card(
            "Reference Project",
            lowest_risk_project,
            "Lowest-risk comparison case",
        )

    st.markdown("## Side-by-Side Comparison Table")

    display_df = comparison_df.drop(
        columns=["Risk Score"],
        errors="ignore",
    ).copy()

    display_df["Total Cost"] = display_df[
        "Total Cost"
    ].apply(
        lambda value: f"₹{value:,.2f} Cr"
    )

    display_df["Cost per km"] = display_df[
        "Cost per km"
    ].apply(
        lambda value: f"₹{value:,.2f} Cr"
    )

    display_df["Road Length (km)"] = display_df[
        "Road Length (km)"
    ].apply(
        lambda value: f"{value:,.2f}"
    )

    display_df["Duration (months)"] = display_df[
        "Duration (months)"
    ].apply(
        lambda value: f"{value:,.2f}"
    )

    display_df["Material Index"] = display_df[
        "Material Index"
    ].apply(
        lambda value: f"{value:,.2f}"
    )

    display_df["Manpower Hours/km"] = display_df[
        "Manpower Hours/km"
    ].apply(
        lambda value: f"{value:,.2f}"
    )

    display_df["Machinery Hours/km"] = display_df[
        "Machinery Hours/km"
    ].apply(
        lambda value: f"{value:,.2f}"
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("## Cost Comparison")

    cost_df = comparison_df.melt(
        id_vars="Project Name",
        value_vars=[
            "Total Cost",
            "Cost per km",
        ],
        var_name="Cost Metric",
        value_name="Amount",
    )

    cost_fig = px.bar(
        cost_df,
        x="Project Name",
        y="Amount",
        color="Cost Metric",
        barmode="group",
        text="Amount",
        title="Total Cost and Cost per km Comparison",
    )

    cost_fig.update_traces(
        texttemplate="₹%{y:,.2f}",
        textposition="outside",
    )

    cost_fig.update_layout(
        height=450,
        xaxis_title="Project",
        yaxis_title="Amount (₹ Cr)",
        title_x=0.02,
    )

    st.plotly_chart(
        cost_fig,
        width="stretch",
        key="comparison_cost_chart",
    )

    st.markdown("## Duration Comparison")

    duration_fig = px.bar(
        comparison_df,
        x="Project Name",
        y="Duration (months)",
        text="Duration (months)",
        title="Construction Duration Comparison",
    )

    duration_fig.update_traces(
        texttemplate="%{y:,.2f}",
        textposition="outside",
    )

    duration_fig.update_layout(
        height=420,
        xaxis_title="Project",
        yaxis_title="Duration (months)",
        title_x=0.02,
    )

    st.plotly_chart(
        duration_fig,
        width="stretch",
        key="comparison_duration_chart",
    )

    st.markdown(
        "## Material and Resource Intensity Comparison"
    )

    resource_df = comparison_df.melt(
        id_vars="Project Name",
        value_vars=[
            "Material Index",
            "Manpower Hours/km",
            "Machinery Hours/km",
        ],
        var_name="Resource Metric",
        value_name="Predicted Value",
    )

    resource_fig = px.bar(
        resource_df,
        x="Project Name",
        y="Predicted Value",
        color="Resource Metric",
        barmode="group",
        title=(
            "Material, Manpower, and Machinery "
            "Intensity Comparison"
        ),
    )

    resource_fig.update_layout(
        height=460,
        xaxis_title="Project",
        yaxis_title="Predicted Value",
        title_x=0.02,
    )

    st.plotly_chart(
        resource_fig,
        width="stretch",
        key="comparison_resource_chart",
    )

    st.markdown("## Cost vs Duration Scatter Plot")

    scatter_fig = px.scatter(
        comparison_df,
        x="Duration (months)",
        y="Total Cost",
        size="Road Length (km)",
        color="Risk Level",
        hover_name="Project Name",
        hover_data={
            "Cost per km": ":.2f",
            "Road Length (km)": ":.2f",
            "Material Index": ":.2f",
            "Manpower Hours/km": ":.2f",
            "Machinery Hours/km": ":.2f",
        },
        category_orders={
            "Risk Level": [
                "Low",
                "Medium",
                "High",
                "Unknown",
            ]
        },
        title="Cost vs Duration Planning Trade-off",
    )

    scatter_fig.update_layout(
        height=480,
        xaxis_title="Duration (months)",
        yaxis_title="Total Cost (₹ Cr)",
        title_x=0.02,
    )

    st.plotly_chart(
        scatter_fig,
        width="stretch",
        key="comparison_scatter_chart",
    )

    st.markdown("## Radar Chart")

    radar_df = comparison_df.copy()

    radar_metrics = [
        "Cost per km",
        "Duration (months)",
        "Material Index",
        "Manpower Hours/km",
        "Machinery Hours/km",
    ]

    for metric in radar_metrics:
        max_value = safe_float(
            radar_df[metric].max()
        )

        normalized_column = f"{metric} Normalized"

        if max_value <= 0:
            radar_df[normalized_column] = 0.0
        else:
            radar_df[normalized_column] = (
                radar_df[metric] / max_value
            )

    radar_fig = go.Figure()

    radar_categories = [
        "Cost/km",
        "Duration",
        "Material",
        "Manpower",
        "Machinery",
    ]

    for _, row in radar_df.iterrows():
        radar_values = [
            row["Cost per km Normalized"],
            row["Duration (months) Normalized"],
            row["Material Index Normalized"],
            row["Manpower Hours/km Normalized"],
            row["Machinery Hours/km Normalized"],
        ]

        radar_values.append(radar_values[0])
        closed_categories = (
            radar_categories + [radar_categories[0]]
        )

        radar_fig.add_trace(
            go.Scatterpolar(
                r=radar_values,
                theta=closed_categories,
                fill="toself",
                name=row["Project Name"],
            )
        )

    radar_fig.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 1],
            }
        },
        height=520,
        title="Normalized Project Intensity Radar",
        title_x=0.02,
    )

    st.plotly_chart(
        radar_fig,
        width="stretch",
        key="comparison_radar_chart",
    )

    st.markdown("## Planning Interpretation")

    best_cost_row = comparison_df.sort_values(
        "Cost per km"
    ).iloc[0]

    fastest_row = comparison_df.sort_values(
        "Duration (months)"
    ).iloc[0]

    lowest_risk_row = comparison_df.sort_values(
        [
            "Risk Score",
            "Cost per km",
        ]
    ).iloc[0]

    resource_comparison_df = comparison_df.assign(
        resource_score=(
            comparison_df["Manpower Hours/km"]
            + comparison_df["Machinery Hours/km"]
        )
    )

    lowest_resource_row = (
        resource_comparison_df
        .sort_values("resource_score")
        .iloc[0]
    )

    st.markdown(
        f"""
- **Lowest cost per km:** {best_cost_row["Project Name"]} at ₹{best_cost_row["Cost per km"]:,.2f} Cr/km
- **Shortest estimated duration:** {fastest_row["Project Name"]} at {fastest_row["Duration (months)"]:,.2f} months
- **Lowest-risk alternative:** {lowest_risk_row["Project Name"]} with a {lowest_risk_row["Risk Level"]} risk rating
- **Lowest combined manpower and machinery intensity:** {lowest_resource_row["Project Name"]}
- Use the scatter plot to identify projects with high costs but limited delivery-time advantages.
- Use the radar chart to compare the overall planning intensity of each alternative.
        """
    )