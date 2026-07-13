import json
import io

import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont

from src.ui.components import page_header, metric_card
from src.database.project_repository import get_all_projects


def format_cr(value):
    return f"₹{value:,.2f} Cr"


def parse_prediction_data(row):
    try:
        if pd.isna(row["prediction_data"]) or row["prediction_data"] is None:
            return {}
        return json.loads(row["prediction_data"])
    except Exception:
        return {}


def fig_to_png_bytes(fig):
    try:
        return fig.to_image(format="png", scale=2)
    except Exception:
        return None


def safe_download_plotly_chart(fig, label, file_name, key):
    png_bytes = fig_to_png_bytes(fig)

    if png_bytes is not None:
        st.download_button(
            label=label,
            data=png_bytes,
            file_name=file_name,
            mime="image/png",
            width="stretch",
            key=key,
        )
    else:
        st.caption(
            "PNG export requires Chrome/Kaleido and may not be available on Streamlit Cloud."
        )


def load_fonts():
    try:
        title_font = ImageFont.truetype("DejaVuSans.ttf", 48)
        heading_font = ImageFont.truetype("DejaVuSans.ttf", 30)
        value_font = ImageFont.truetype("DejaVuSans.ttf", 34)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 22)
    except Exception:
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    return title_font, heading_font, value_font, small_font


def create_dashboard_summary_png(
    total_projects,
    completed_count,
    pending_count,
    avg_cost,
    avg_cost_per_km,
    avg_duration,
    most_expensive_project,
):
    width, height = 1400, 800
    image = Image.new("RGB", (width, height), "#F5F7FA")
    draw = ImageDraw.Draw(image)

    title_font, heading_font, value_font, small_font = load_fonts()

    draw.text(
        (60, 50),
        "RoadPlan AI - Dashboard Summary",
        fill="#111827",
        font=title_font,
    )

    cards = [
        ("Total Projects", str(total_projects)),
        ("Projects Completed", str(completed_count)),
        ("Pending Prediction", str(pending_count)),
        ("Average Cost", format_cr(avg_cost) if pd.notna(avg_cost) else "N/A"),
        ("Average Cost/km", format_cr(avg_cost_per_km) if pd.notna(avg_cost_per_km) else "N/A"),
        ("Average Duration", f"{avg_duration:.2f} months" if pd.notna(avg_duration) else "N/A"),
        ("Most Expensive Project", most_expensive_project),
    ]

    x_positions = [60, 500, 940]
    y_positions = [170, 380, 590]

    card_width = 360
    card_height = 150
    index = 0

    for y in y_positions:
        for x in x_positions:
            if index >= len(cards):
                break

            title, value = cards[index]

            draw.rounded_rectangle(
                (x, y, x + card_width, y + card_height),
                radius=20,
                fill="#FFFFFF",
                outline="#E5E7EB",
                width=2,
            )

            draw.rectangle(
                (x, y, x + 8, y + card_height),
                fill="#F59E0B",
            )

            draw.text(
                (x + 25, y + 25),
                title,
                fill="#6B7280",
                font=heading_font,
            )

            draw.text(
                (x + 25, y + 75),
                str(value)[:28],
                fill="#111827",
                font=value_font,
            )

            index += 1

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def render_dashboard():
    page_header(
        "Dashboard",
        "Executive overview of road planning projects, predictions, and infrastructure analytics",
    )

    projects = get_all_projects()

    if projects.empty:
        st.warning("No projects saved yet. Create your first road project from the New Project page.")
        return

    projects = projects.copy()
    projects["prediction_dict"] = projects.apply(parse_prediction_data, axis=1)

    projects["total_cost_lakhs"] = projects["prediction_dict"].apply(
        lambda x: x.get("total_cost", None)
    )

    projects["duration_months"] = projects["prediction_dict"].apply(
        lambda x: x.get("duration", None)
    )

    projects["total_cost_cr"] = projects["total_cost_lakhs"].apply(
        lambda x: x / 100 if pd.notna(x) else None
    )

    projects["cost_per_km_cr"] = projects.apply(
        lambda row: (
            row["total_cost_cr"] / row["road_length_km"]
            if pd.notna(row["total_cost_cr"]) and row["road_length_km"] > 0
            else None
        ),
        axis=1,
    )

    st.markdown("## Search & Filter Projects")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        search_query = st.text_input(
            "Search project",
            placeholder="Search by project name or location",
        )

    with filter_col2:
        selected_state = st.selectbox(
            "Filter by State / Location",
            ["All"] + sorted(projects["location"].dropna().unique().tolist()),
        )

    with filter_col3:
        selected_status = st.selectbox(
            "Filter by Prediction Status",
            ["All"] + sorted(projects["prediction_status"].dropna().unique().tolist()),
        )

    filter_col4, filter_col5, filter_col6 = st.columns(3)

    with filter_col4:
        selected_road_type = st.selectbox(
            "Filter by Road Type",
            ["All"] + sorted(projects["road_category"].dropna().unique().tolist()),
        )

    with filter_col5:
        selected_terrain = st.selectbox(
            "Filter by Terrain",
            ["All"] + sorted(projects["terrain_type"].dropna().unique().tolist()),
        )

    with filter_col6:
        selected_risk = st.selectbox(
            "Filter by Risk Level",
            ["All"] + sorted(projects["risk_level"].dropna().unique().tolist()),
        )

    filtered_projects = projects.copy()

    if search_query:
        filtered_projects = filtered_projects[
            filtered_projects["project_name"].str.contains(search_query, case=False, na=False)
            | filtered_projects["location"].str.contains(search_query, case=False, na=False)
        ]

    if selected_state != "All":
        filtered_projects = filtered_projects[filtered_projects["location"] == selected_state]

    if selected_status != "All":
        filtered_projects = filtered_projects[
            filtered_projects["prediction_status"] == selected_status
        ]

    if selected_road_type != "All":
        filtered_projects = filtered_projects[
            filtered_projects["road_category"] == selected_road_type
        ]

    if selected_terrain != "All":
        filtered_projects = filtered_projects[
            filtered_projects["terrain_type"] == selected_terrain
        ]

    if selected_risk != "All":
        filtered_projects = filtered_projects[
            filtered_projects["risk_level"] == selected_risk
        ]

    if filtered_projects.empty:
        st.warning("No projects match the selected filters.")
        return

    completed_projects = filtered_projects[
        filtered_projects["prediction_status"] == "Completed"
    ]

    pending_projects = filtered_projects[
        filtered_projects["prediction_status"] != "Completed"
    ]

    total_projects = len(filtered_projects)
    completed_count = len(completed_projects)
    pending_count = len(pending_projects)

    avg_cost = completed_projects["total_cost_cr"].mean()
    avg_duration = completed_projects["duration_months"].mean()
    avg_cost_per_km = completed_projects["cost_per_km_cr"].mean()

    if not completed_projects.empty:
        most_expensive_project = completed_projects.sort_values(
            "total_cost_cr",
            ascending=False,
        ).iloc[0]["project_name"]
    else:
        most_expensive_project = "N/A"

    st.markdown("## Portfolio Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Total Projects", total_projects, "Saved planning cases")

    with c2:
        metric_card("Projects Completed", completed_count, "Predictions available")

    with c3:
        metric_card("Pending Prediction", pending_count, "Awaiting AI estimation")

    with c4:
        metric_card("Most Expensive Project", most_expensive_project, "Highest predicted cost")

    c5, c6, c7 = st.columns(3)

    with c5:
        metric_card(
            "Average Cost",
            format_cr(avg_cost) if pd.notna(avg_cost) else "N/A",
            "Across completed projects",
        )

    with c6:
        metric_card(
            "Average Cost/km",
            format_cr(avg_cost_per_km) if pd.notna(avg_cost_per_km) else "N/A",
            "Normalized project cost",
        )

    with c7:
        metric_card(
            "Average Duration",
            f"{avg_duration:.2f} months" if pd.notna(avg_duration) else "N/A",
            "Across completed projects",
        )

    st.markdown("## Project Portfolio")

    display_df = filtered_projects[
        [
            "id",
            "project_name",
            "location",
            "road_category",
            "terrain_type",
            "road_length_km",
            "risk_level",
            "prediction_status",
            "total_cost_cr",
            "cost_per_km_cr",
            "duration_months",
            "created_at",
        ]
    ].copy()

    display_df.rename(
        columns={
            "id": "ID",
            "project_name": "Project Name",
            "location": "Location",
            "road_category": "Road Category",
            "terrain_type": "Terrain",
            "road_length_km": "Length (km)",
            "risk_level": "Risk Level",
            "prediction_status": "Prediction Status",
            "total_cost_cr": "Total Cost",
            "cost_per_km_cr": "Cost/km",
            "duration_months": "Duration",
            "created_at": "Created At",
        },
        inplace=True,
    )

    display_df["Total Cost"] = display_df["Total Cost"].apply(
        lambda x: format_cr(x) if pd.notna(x) else "Pending"
    )

    display_df["Cost/km"] = display_df["Cost/km"].apply(
        lambda x: format_cr(x) if pd.notna(x) else "Pending"
    )

    display_df["Duration"] = display_df["Duration"].apply(
        lambda x: f"{x:.2f} months" if pd.notna(x) else "Pending"
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
    )

    if completed_projects.empty:
        st.info("Charts will appear after at least one project prediction is completed.")
        return

    st.markdown("## Cost Analytics")

    cost_fig = px.bar(
        completed_projects,
        x="project_name",
        y="total_cost_cr",
        color="risk_level",
        title="Predicted Total Cost by Project",
        text="total_cost_cr",
    )

    cost_fig.update_traces(
        texttemplate="₹%{y:.2f} Cr",
        textposition="outside",
    )

    cost_fig.update_layout(
        height=450,
        xaxis_title="Project",
        yaxis_title="Total Cost (₹ Cr)",
        title_x=0.02,
    )

    st.plotly_chart(
        cost_fig,
        width="stretch",
        key="dashboard_total_cost_chart",
        config={
            "displaylogo": False,
            "modeBarButtonsToAdd": ["toImage"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "roadplan_total_cost",
                "scale": 2,
            },
        },
    )

    st.markdown("## Cost per km Analytics")

    cost_per_km_fig = px.bar(
        completed_projects,
        x="project_name",
        y="cost_per_km_cr",
        color="terrain_type",
        title="Predicted Cost per km by Project",
        text="cost_per_km_cr",
    )

    cost_per_km_fig.update_traces(
        texttemplate="₹%{y:.2f} Cr/km",
        textposition="outside",
    )

    cost_per_km_fig.update_layout(
        height=450,
        xaxis_title="Project",
        yaxis_title="Cost per km (₹ Cr/km)",
        title_x=0.02,
    )

    st.plotly_chart(
        cost_per_km_fig,
        width="stretch",
        key="dashboard_cost_per_km_chart",
        config={
            "displaylogo": False,
            "modeBarButtonsToAdd": ["toImage"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "roadplan_cost_per_km",
                "scale": 2,
            },
        },
    )

    st.markdown("## Duration Analytics")

    duration_fig = px.bar(
        completed_projects,
        x="project_name",
        y="duration_months",
        color="road_category",
        title="Predicted Construction Duration by Project",
        text="duration_months",
    )

    duration_fig.update_traces(
        texttemplate="%{y:.2f} months",
        textposition="outside",
    )

    duration_fig.update_layout(
        height=450,
        xaxis_title="Project",
        yaxis_title="Duration (months)",
        title_x=0.02,
    )

    st.plotly_chart(
        duration_fig,
        width="stretch",
        key="dashboard_duration_chart",
        config={
            "displaylogo": False,
            "modeBarButtonsToAdd": ["toImage"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "roadplan_duration",
                "scale": 2,
            },
        },
    )

    st.markdown("## Project Status Distribution")

    status_df = filtered_projects["prediction_status"].value_counts().reset_index()
    status_df.columns = ["Prediction Status", "Count"]

    status_fig = px.pie(
        status_df,
        names="Prediction Status",
        values="Count",
        title="Completed vs Pending Projects",
    )

    status_fig.update_layout(
        height=420,
        title_x=0.02,
    )

    st.plotly_chart(
        status_fig,
        width="stretch",
        key="dashboard_status_distribution_chart",
        config={
            "displaylogo": False,
            "modeBarButtonsToAdd": ["toImage"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "roadplan_status_distribution",
                "scale": 2,
            },
        },
    )

    st.markdown("## Export Dashboard")

    dashboard_png = create_dashboard_summary_png(
        total_projects=total_projects,
        completed_count=completed_count,
        pending_count=pending_count,
        avg_cost=avg_cost,
        avg_cost_per_km=avg_cost_per_km,
        avg_duration=avg_duration,
        most_expensive_project=most_expensive_project,
    )

    st.download_button(
        label="📥 Download Dashboard Summary as PNG",
        data=dashboard_png,
        file_name="roadplan_dashboard_summary.png",
        mime="image/png",
        width="stretch",
        key="download_dashboard_summary",
    )

    safe_download_plotly_chart(
        cost_fig,
        "📥 Download Cost Chart PNG",
        "cost_chart.png",
        "download_cost_chart",
    )

    safe_download_plotly_chart(
        cost_per_km_fig,
        "📥 Download Cost per km Chart PNG",
        "cost_per_km_analytics.png",
        "download_cost_per_km_chart",
    )

    safe_download_plotly_chart(
        duration_fig,
        "📥 Download Duration Chart PNG",
        "duration_analytics.png",
        "download_duration_chart",
    )

    safe_download_plotly_chart(
        status_fig,
        "📥 Download Status Distribution PNG",
        "project_status_distribution.png",
        "download_status_chart",
    )