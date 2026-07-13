import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.ui.components import page_header, metric_card, friendly_error_box
from src.database.project_repository import get_all_projects, get_project_by_id, delete_project


def render_comparison():
    page_header(
        "Compare Projects",
        "Compare multiple road construction alternatives side by side"
    )

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning("No projects available. Create projects first.")
        return

    completed_projects = projects_df[
        projects_df["prediction_status"] == "Completed"
    ]

    if completed_projects.empty:
        st.warning("No completed predictions available. Run predictions first.")
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": row.id
        for row in completed_projects.itertuples()
    }

    selected_labels = st.multiselect(
        "Select projects to compare",
        list(project_options.keys()),
        default=list(project_options.keys())[:2]
    )

    if len(selected_labels) < 2:
        st.info("Select at least two completed projects for comparison.")
        return

    comparison_rows = []

    for label in selected_labels:
        project_id = project_options[label]
        project_data = get_project_by_id(project_id)

        selected_row = completed_projects[
            completed_projects["id"] == project_id
        ].iloc[0]

        prediction_data = {
            "total_cost": selected_row["total_cost_lakhs"],
            "duration": selected_row["construction_duration_months"],
            "material_index": selected_row["material_index"],
            "manpower_hours_per_km": selected_row["manpower_hours_per_km"],
            "machinery_hours_per_km": selected_row["machinery_hours_per_km"],
        }

        road_length = project_data.get("road_length_km", 0)
        total_cost = prediction_data.get("total_cost", 0)
        duration = prediction_data.get("duration", 0)

        cost_per_km = total_cost / road_length if road_length else 0

        comparison_rows.append({
            "Project ID": project_id,
            "Project Name": project_data.get("project_name"),
            "Location": project_data.get("location"),
            "Road Category": project_data.get("road_category"),
            "Terrain Type": project_data.get("terrain_type"),
            "Road Length (km)": road_length,
            "Risk Level": project_data.get("risk_level", "Unknown"),
            "Total Cost": total_cost/100,
            "Cost per km": cost_per_km/100,
            "Duration (months)": duration,
            "Material Index": prediction_data.get("material_index", 0),
            "Manpower Hours/km": prediction_data.get("manpower_hours_per_km", 0),
            "Machinery Hours/km": prediction_data.get("machinery_hours_per_km", 0),
        })

    try:
        comparison_df = pd.DataFrame(comparison_rows)
        if comparison_df.empty:
            st.warning("No comparable prediction data available.")
            return

    except Exception as e:
        friendly_error_box(
            "Project comparison could not be prepared.",
            possible_reasons=[
                "Selected projects do not have completed predictions",
                "Prediction data is missing or corrupted",
                "Comparison fields are incomplete",
            ],
            technical_error=e,
        )
        return

    st.markdown("## Comparison Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Projects Compared",
            len(comparison_df),
            "Completed prediction cases"
        )

    with c2:
        metric_card(
            "Lowest Cost/km",
            f"₹{comparison_df['Cost per km'].min():,.2f} Cr",
            "Best normalized cost"
        )

    with c3:
        metric_card(
            "Shortest Duration",
            f"{comparison_df['Duration (months)'].min():.2f} months",
            "Fastest delivery estimate"
        )

    with c4:
        risk_order = {"Low": 1, "Medium": 2, "High": 3}
        risk_mapping = {
            "Low": 1,
            "Medium": 2,
            "High": 3
        }
        comparison_df["Risk Score"] = (comparison_df["Risk Level"].map(risk_mapping).fillna(0))
        lowest_risk_project = comparison_df.sort_values(
            "Risk Score"
        ).iloc[0]["Project Name"]

        metric_card(
            "Reference Project",
            lowest_risk_project,
            "Compare against alternatives"
        )

    st.markdown("## Side-by-Side Comparison Table")

    display_df = comparison_df.copy()

    display_df["Total Cost"] = display_df["Total Cost"].apply(
        lambda x: f"₹{x:,.2f} Cr"
    )

    display_df["Cost per km"] = display_df["Cost per km"].apply(
        lambda x: f"₹{x:,.2f} Cr"
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )

    st.markdown("## Cost Comparison")

    cost_df = comparison_df.melt(
        id_vars="Project Name",
        value_vars=["Total Cost", "Cost per km"],
        var_name="Cost Metric",
        value_name="Amount"
    )

    cost_fig = px.bar(
        cost_df,
        x="Project Name",
        y="Amount",
        color="Cost Metric",
        barmode="group",
        title="Total Cost and Cost per km Comparison"
    )

    cost_fig.update_layout(
        height=450,
        xaxis_title="Project",
        yaxis_title="Amount (₹ Cr)",
        title_x=0.02
    )

    st.plotly_chart(cost_fig, width="stretch", key="comparison_cost_chart")

    st.markdown("## Duration Comparison")

    duration_fig = px.bar(
        comparison_df,
        x="Project Name",
        y="Duration (months)",
        text="Duration (months)",
        title="Construction Duration Comparison"
    )

    duration_fig.update_layout(
        height=420,
        xaxis_title="Project",
        yaxis_title="Duration (months)",
        title_x=0.02
    )

    st.plotly_chart(duration_fig, width="stretch", key="comparison_duration_chart")

    st.markdown("## Material and Resource Intensity Comparison")

    resource_df = comparison_df.melt(
        id_vars="Project Name",
        value_vars=[
            "Material Index",
            "Manpower Hours/km",
            "Machinery Hours/km",
        ],
        var_name="Resource Metric",
        value_name="Predicted Value"
    )

    resource_fig = px.bar(
        resource_df,
        x="Project Name",
        y="Predicted Value",
        color="Resource Metric",
        barmode="group",
        title="Material, Manpower, and Machinery Intensity Comparison"
    )

    resource_fig.update_layout(
        height=460,
        xaxis_title="Project",
        yaxis_title="Predicted Value",
        title_x=0.02
    )

    st.plotly_chart(resource_fig, width="stretch", key="comparison_resource_chart")

    st.markdown("## Cost vs Duration Scatter Plot")

    scatter_fig = px.scatter(
        comparison_df,
        x="Duration (months)",
        y="Total Cost",
        size="Road Length (km)",
        color="Risk Level",
        hover_name="Project Name",
        title="Cost vs Duration Planning Trade-off"
    )

    scatter_fig.update_layout(
        height=480,
        xaxis_title="Duration (months)",
        yaxis_title="Total Cost (₹ Cr)",
        title_x=0.02
    )

    st.plotly_chart(scatter_fig, width="stretch", key="comparison_scatter_chart")

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
        max_value = radar_df[metric].max()
        if max_value == 0:
            radar_df[metric + " Normalized"] = 0
        else:
            radar_df[metric + " Normalized"] = radar_df[metric] / max_value

    radar_fig = go.Figure()

    for _, row in radar_df.iterrows():
        radar_fig.add_trace(
            go.Scatterpolar(
                r=[
                    row["Cost per km Normalized"],
                    row["Duration (months) Normalized"],
                    row["Material Index Normalized"],
                    row["Manpower Hours/km Normalized"],
                    row["Machinery Hours/km Normalized"],
                ],
                theta=[
                    "Cost/km",
                    "Duration",
                    "Material",
                    "Manpower",
                    "Machinery",
                ],
                fill="toself",
                name=row["Project Name"],
            )
        )

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        height=520,
        title="Normalized Project Intensity Radar"
    )

    st.plotly_chart(radar_fig, width="stretch", key="comparison_radar_chart")

    st.markdown("## Planning Interpretation")

    best_cost_project = comparison_df.sort_values("Cost per km").iloc[0]["Project Name"]
    fastest_project = comparison_df.sort_values("Duration (months)").iloc[0]["Project Name"]
    lowest_resource_project = comparison_df.assign(
        resource_score=(
            comparison_df["Manpower Hours/km"]
            + comparison_df["Machinery Hours/km"]
        )
    ).sort_values("resource_score").iloc[0]["Project Name"]

    st.markdown(
        f"""
        - **Lowest cost per km:** {best_cost_project}
        - **Shortest estimated duration:** {fastest_project}
        - **Lowest combined manpower and machinery intensity:** {lowest_resource_project}
        - Use the scatter plot to identify projects with high cost but low delivery advantage.
        - Use the radar chart to compare overall planning intensity across alternatives.
        """
    )