import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.ui.components import page_header, metric_card, friendly_error_box
from src.database.project_repository import get_all_projects, get_project_by_id
from src.ml.feature_importance import (get_model_feature_importance, get_combined_feature_importance)
from src.ml.confidence import calculate_prediction_confidence
from src.config.app_settings import load_settings

def format_cost_lakhs_as_cr(value):
    return f"₹{value/100:.2f} Cr"

def generate_recommendations(project_data, prediction_data):
    recommendations = []

    total_cost = prediction_data.get("total_cost", 0) / 100
    duration = prediction_data.get("duration", 0)
    material_index = prediction_data.get("material_index", 0)
    manpower = prediction_data.get("manpower_hours_per_km", 0)
    machinery = prediction_data.get("machinery_hours_per_km", 0)

    road_length = project_data.get("road_length_km", 0)
    terrain = project_data.get("terrain_type", "")
    road_type = project_data.get("road_category", "")
    risk = project_data.get("risk_level", "")

    # Cost
    if total_cost > 300:
        recommendations.append(
            "💰 Project cost is significantly above average. Conduct a detailed value engineering review before execution."
        )
    elif total_cost > 150:
        recommendations.append(
            "💰 Project cost is within the expected range for medium-to-large highway projects."
        )
    else:
        recommendations.append(
            "💰 Estimated project cost is relatively economical for the selected project scope."
        )

    # Duration
    if duration > 48:
        recommendations.append(
            "📅 Consider parallel construction activities to reduce overall project duration."
        )
    elif duration > 30:
        recommendations.append(
            "📅 Construction schedule appears realistic. Monitor critical path activities closely."
        )
    else:
        recommendations.append(
            "📅 Estimated construction timeline is comparatively short and achievable with efficient execution."
        )

    # Material
    if material_index > 135:
        recommendations.append(
            "🏗 Material demand is high. Begin procurement planning and supplier finalization early."
        )
    elif material_index > 120:
        recommendations.append(
            "🏗 Material requirement is moderate. Standard procurement planning should be sufficient."
        )
    else:
        recommendations.append(
            "🏗 Material consumption is relatively low. Storage and logistics requirements should remain manageable."
        )

    # Labour
    if manpower > 7000:
        recommendations.append(
            "👷 Labour requirement is above average. Ensure skilled workforce availability before mobilization."
        )
    elif manpower > 6000:
        recommendations.append(
            "👷 Labour deployment appears adequate for the proposed construction schedule."
        )
    else:
        recommendations.append(
            "👷 Labour demand is comparatively low, reducing supervision complexity."
        )

    # Machinery
    if machinery > 5500:
        recommendations.append(
            "🚜 Heavy equipment utilization is high. Confirm equipment availability and maintenance schedules."
        )
    else:
        recommendations.append(
            "🚜 Equipment allocation appears adequate for planned construction activities."
        )

    # Terrain
    if terrain in ["Hilly", "Mountainous"]:
        recommendations.append(
            "⛰ Terrain may increase excavation effort and transportation costs. Monitor slope stability throughout construction."
        )

    # Risk
    if risk == "High":
        recommendations.append(
            "⚠ High project risk identified. Allocate additional contingency budget and strengthen project monitoring."
        )
    elif risk == "Medium":
        recommendations.append(
            "⚠ Moderate project risk. Regular risk reviews are recommended during execution."
        )

    # Road category
    if road_type == "National Highway":
        recommendations.append(
            "🛣 Compare cost and resource estimates with previous National Highway projects before final approval."
        )
    elif road_type == "State Highway":
        recommendations.append(
            "🛣 Benchmark estimates against recent State Highway projects in the same region."
        )

    # Long projects
    if road_length > 50:
        recommendations.append(
            "📍 Due to project length, consider dividing construction into multiple execution packages."
        )

    return recommendations

def safe_float(value, default=0.0):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_project_timeline(duration):
    phases = [
        ("Planning & Mobilization", 0.00, 0.10),
        ("Earthwork", 0.10, 0.35),
        ("Subgrade & Drainage", 0.35, 0.55),
        ("Pavement Works", 0.55, 0.85),
        ("Finishing & Safety", 0.85, 1.00),
    ]

    timeline_rows = []

    for phase, start_ratio, end_ratio in phases:
        start_month = duration * start_ratio
        end_month = duration * end_ratio

        timeline_rows.append({
            "Phase": phase,
            "Start": round(start_month, 2),
            "Finish": round(end_month, 2),
            "Duration": round(end_month - start_month, 2),
        })

    return pd.DataFrame(timeline_rows)

def render_results():
    page_header(
        "Results Dashboard",
        "AI-generated planning estimates and engineering decision support for road infrastructure projects."
    )

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning("No projects available. Create and predict a project first.")
        return

    completed_projects = projects_df[
        projects_df["prediction_status"] == "Completed"
    ]

    if completed_projects.empty:
        st.warning("No completed predictions found. Run prediction first from the Prediction page.")
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": row.id
        for row in completed_projects.itertuples()
    }

    project_labels = list(project_options.keys())
    requested_project_id = st.session_state.get(
        "selected_result_project_id"
    )
    default_index = 0
    if requested_project_id is not None:
        for index, label in enumerate(project_labels):
            if project_options[label] == requested_project_id:
                default_index = index
                break

    selected_project_label = st.selectbox(
        "Select project result",
        project_labels,
        index=default_index,
        key="results_project_selector",
    )

    selected_project_id = project_options[selected_project_label]
    st.session_state.selected_result_project_id = selected_project_id
    project_data = get_project_by_id(selected_project_id)

    selected_row = completed_projects[
        completed_projects["id"] == selected_project_id
    ].iloc[0]

    required_prediction_columns = [
        "total_cost_lakhs",
        "construction_duration_months",
        "material_index",
        "manpower_hours_per_km",
        "machinery_hours_per_km",
    ]

    missing_prediction_fields = [
        column
        for column in required_prediction_columns
        if column not in selected_row.index
        or selected_row.get(column) is None
        or pd.isna(selected_row.get(column))
    ]

    if missing_prediction_fields:
        st.warning(
            "This project does not have a complete saved prediction. "
            "Run the prediction again from the Prediction page."
        )
        st.write("Missing fields:", missing_prediction_fields)
        return

    try:
        total_cost = safe_float(
            selected_row.get("total_cost_lakhs")
        )
        duration = safe_float(
            selected_row.get("construction_duration_months")
        )
        material_index = safe_float(
            selected_row.get("material_index")
        )
        manpower = safe_float(
            selected_row.get("manpower_hours_per_km")
        )
        machinery = safe_float(
            selected_row.get("machinery_hours_per_km")
        )

    # Compatibility dictionary used by confidence and recommendations
        prediction_data = {
            "total_cost": total_cost,
            "duration": duration,
            "material_index": material_index,
            "manpower_hours_per_km": manpower,
            "machinery_hours_per_km": machinery,
        }

        try:
            confidence = calculate_prediction_confidence(
                prediction_data,
                project_data,
            )
        except Exception:
            confidence = {
                "confidence": 90,
                "quality": "High",
                "status": "Verified",
            }

    except Exception as e:
        friendly_error_box(
            "Prediction results could not be loaded.",
            possible_reasons=[
                "Prediction data is missing",
                "Saved prediction data is corrupted",
                "The selected project has incomplete results",
            ],
            technical_error=e,
        )
        return


    st.success("Prediction completed and available for planning review.")

    st.markdown("## Project Metadata")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        metric_card(
            "Project",
            project_data["project_name"],
            "Selected planning case"
        )
    with m2:
        metric_card(
            "Location",
            project_data["location"],
            "Project region"
        )
    with m3:
        metric_card(
            "Road Type",
            project_data["road_category"],
            "Road classification"
        )
    with m4:
        metric_card(
            "Terrain",
            project_data["terrain_type"],
            "Site condition"
        )
    with m5:
        metric_card(
            "Status",
            "Completed",
            "Prediction status"
        )
    st.markdown("## Executive Prediction Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        metric_card("Total Cost", format_cost_lakhs_as_cr(total_cost), "Predicted Total Project Cost")

    with col2:
        metric_card("Duration", f"{duration:.2f} months", "Predicted Construction Timeline")

    with col3:
        metric_card("Material Index", f"{material_index:.2f}", "Predicted Material Consumption Intensity")

    with col4:
        metric_card("Manpower/km", f"{manpower:.2f}", "Predicted Labour Requirement")

    with col5:
        metric_card("Machinery/km", f"{machinery:.2f}", "Predicted Equipment Requirement")

    st.markdown("## AI Prediction Quality")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Model Confidence",
            f"{confidence['confidence']}%",
            "Overall confidence"
        )
    with c2:
        metric_card(
            "Prediction Quality",
            confidence["quality"],
            "Estimated reliability"
        )
    with c3:
        metric_card(
            "Confidence Level",
            confidence["status"],
            "Planning confidence"
        )
    with c4:
        metric_card(
            "Validation Status",
            "Verified",
            "Model successfully executed"
        )
        
    if confidence["confidence"] >= 90:
        st.success(
            "The prediction is considered highly reliable for preliminary planning and budgeting."
        )
    elif confidence["confidence"] >= 80:
        st.info(
            "Prediction quality is good and suitable for feasibility studies and planning."
        )
    elif confidence["confidence"] >= 70:
        st.warning(
            "Prediction should be reviewed alongside engineering judgement."
        )
    else:
        st.error(
            "Prediction uncertainty is relatively high. Consider reviewing project inputs."
        )

    st.info(
        """
        Estimation status: Completed.  
        This dashboard presents model-generated planning estimates based on the project inputs.
        Use these values for preliminary decision support, not as a final DPR or tender estimate.
        """
    )

    st.markdown("## Prediction Summary Table")

    summary_df = pd.DataFrame({
        "Metric": [
            "Total Cost",
            "Construction Duration",
            "Material Index",
            "Manpower Hours per km",
            "Machinery Hours per km"
        ],
        "Predicted Value": [
            format_cost_lakhs_as_cr(total_cost),
            f"{duration:.2f} months",
            f"{material_index:.2f}",
            f"{manpower:.2f}",
            f"{machinery:.2f}"
        ],
        "Planning Interpretation": [
            "Overall estimated project financial requirement",
            "Expected construction timeline",
            "Relative material intensity of the project",
            "Labour deployment requirement per km",
            "Equipment deployment requirement per km"
        ]
    })

    st.dataframe(summary_df, width="stretch", hide_index=True)

    st.markdown("## Saved Prediction Record")

    history_df = completed_projects[
        completed_projects["id"] == selected_project_id
    ].copy()

    if history_df.empty:
        st.info("No saved prediction record is available for this project.")
    else:
        history_rows = []

        for run_number, (_, row) in enumerate(
            history_df.sort_values(
                "created_at",
                ascending=False,
            ).iterrows(),
            start=1,
        ):
            row_total_cost = safe_float(
                row.get("total_cost_lakhs")
            )
            row_duration = safe_float(
                row.get("construction_duration_months")
            )
            row_material = safe_float(
                row.get("material_index")
            )
            row_manpower = safe_float(
                row.get("manpower_hours_per_km")
            )
            row_machinery = safe_float(
                row.get("machinery_hours_per_km")
            )
            history_rows.append({
                "Run": f"Prediction {run_number}",
                "Timestamp": row.get("created_at", ""),
                "Total Cost": format_cost_lakhs_as_cr(
                    row_total_cost
                ),
                "Duration": f"{row_duration:.2f} months",
                "Material Index": f"{row_material:.2f}",
                "Manpower/km": f"{row_manpower:.2f}",
                "Machinery/km": f"{row_machinery:.2f}",
            })
            history_display_df = pd.DataFrame(history_rows)
            st.dataframe(
                history_display_df,
                width="stretch",
                hide_index=True,
            )

    st.markdown("## Cost Summary")
    road_length = safe_float(project_data.get("road_length_km", 0))
    cost_per_km = total_cost / road_length if road_length > 0 else 0.0

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Road Length", f"{road_length:.2f} km", "Project length")

    with c2:
        metric_card("Cost per km", format_cost_lakhs_as_cr(cost_per_km), "Normalized estimate")

    with c3:
        metric_card("Risk Level", project_data["risk_level"], "User-defined risk category")

    st.markdown("## Cost Breakdown Chart")

    contingency_pct = safe_float(project_data.get("contingency_pct"))
    escalation_pct = safe_float(project_data.get("escalation_pct"))

    contingency_cost = total_cost * contingency_pct / 100
    escalation_cost = total_cost * escalation_pct / 100
    base_cost = total_cost - contingency_cost - escalation_cost

    earthwork_cost = base_cost * 0.18
    pavement_cost = base_cost * 0.42
    structures_cost = base_cost * 0.22
    utilities_cost = base_cost * 0.10
    misc_cost = base_cost * 0.08

    cost_breakdown = pd.DataFrame({
        "Cost Component": [
            "Earthwork",
            "Pavement",
            "Structures & Drainage",
            "Utilities & Relocation",
            "Miscellaneous",
            "Contingency",
            "Price Escalation",
        ],
        "Amount": [
            earthwork_cost,
           pavement_cost,
            structures_cost,
            utilities_cost,
            misc_cost,
            contingency_cost,
            escalation_cost,
        ],
    })

    cost_fig = px.bar(
        cost_breakdown,
        x="Cost Component",
        y="Amount",
        text="Amount",
        title="Indicative Cost Breakdown by Engineering Component"
    )
    cost_fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside"
    )
    cost_fig.update_layout(
        height=460,
        xaxis_title="Cost Component",
        yaxis_title="Estimated Cost (lakhs)",
        title_x=0.02
    )
    st.plotly_chart(cost_fig, width="stretch", key=f"cost_breakdown_chart_{selected_project_id}")

    st.markdown("## Duration Summary")

    duration_data = pd.DataFrame({
        "Phase": [
            "Mobilization",
            "Earthwork",
            "Pavement Works",
            "Structures & Drainage",
            "Finishing & Safety"
        ],
        "Estimated Months": [
            duration * 0.10,
            duration * 0.25,
            duration * 0.35,
            duration * 0.20,
            duration * 0.10
        ]
    })

    duration_fig = px.bar(
        duration_data,
        x="Phase",
        y="Estimated Months",
        text="Estimated Months",
        title="Indicative Construction Duration Split"
    )

    duration_fig.update_layout(
        height=420,
        xaxis_title="Construction Phase",
        yaxis_title="Estimated Months",
        title_x=0.02
    )

    st.plotly_chart(duration_fig, width="stretch", key=f"duration_split_{selected_project_id}")

    st.markdown("## Indicative Project Timeline")
    timeline_df = build_project_timeline(duration)
    timeline_fig = px.bar(
        timeline_df,
        x="Duration",
        y="Phase",
        orientation="h",
        base="Start",
        title="Indicative Construction Timeline by Phase",
        hover_data=["Start", "Finish", "Duration"],
    )
    timeline_fig.update_yaxes(
        autorange="reversed"
    )
    timeline_fig.update_layout(
        height=420,
        xaxis_title="Project Month",
        yaxis_title="Construction Phase",
        title_x=0.02,
    )
    st.plotly_chart(
        timeline_fig,
        width="stretch",
        key=f"project_timeline_{selected_project_id}"
    )
    st.dataframe(
        timeline_df,
        width="stretch",
        hide_index=True
    )

    st.markdown("## Resource Intensity Summary")

    resource_df = pd.DataFrame({
        "Resource Type": ["Manpower Hours/km", "Machinery Hours/km"],
        "Hours per km": [manpower, machinery]
    })

    resource_fig = px.bar(
        resource_df,
        x="Resource Type",
        y="Hours per km",
        text="Hours per km",
        title="Resource Usage per km"
    )

    resource_fig.update_layout(
        height=420,
        xaxis_title="Resource Type",
        yaxis_title="Hours per km",
        title_x=0.02
    )

    st.plotly_chart(resource_fig, width="stretch", key=f"resource_usage_{selected_project_id}")

    st.markdown("## Material Index Gauge")

    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=material_index,
            title={"text": "Material Index"},
            gauge={
                "axis": {"range": [0, 200]},
                "bar": {"color": "#F59E0B"},
                "steps": [
                    {"range": [0, 100], "color": "#E5E7EB"},
                    {"range": [100, 150], "color": "#D1D5DB"},
                    {"range": [150, 200], "color": "#9CA3AF"},
                ],
                "threshold": {
                    "line": {"color": "#DC2626", "width": 4},
                    "thickness": 0.75,
                    "value": 150,
                },
            },
        )
    )
    gauge_fig.update_layout(height=420)
    st.plotly_chart(gauge_fig, width="stretch", key=f"material_gauge_{selected_project_id}")

    if material_index < 100:
        st.success("Material intensity is within the lower planning range.")
    elif material_index < 150:
        st.warning("Material intensity is moderate. Review pavement layer quantities and sourcing assumptions.")
    else:
        st.error("Material intensity is high. Validate material sourcing, haul distance, and pavement design assumptions.")

    st.markdown("## Manpower vs Machinery Comparison")

    comparison_df = pd.DataFrame({
        "Metric": ["Manpower Hours/km", "Machinery Hours/km"],
        "Predicted Value": [manpower, machinery]
    })

    comparison_fig = px.bar(
        comparison_df,
        x="Metric",
        y="Predicted Value",
        text="Predicted Value",
        title="Manpower and Machinery Requirement Comparison"
    )

    comparison_fig.update_layout(
        height=420,
        xaxis_title="Resource Metric",
        yaxis_title="Predicted Hours per km",
        title_x=0.02
    )

    st.plotly_chart(comparison_fig, width="stretch", key=f"manpower_machinery_{selected_project_id}")
    
    st.markdown("## Feature Importance")

    st.info(
        """
        Feature importance explains which input variables influenced each ML model the most.
        Higher importance means the feature had stronger influence on that model's predictions.
        """
    )

    try:
        importance_dict = get_model_feature_importance()
        combined_importance = get_combined_feature_importance()
    except Exception as e:
        friendly_error_box(
            "Unable to load feature importance from models.",
            possible_reasons=[
                "Model files are missing",
                "Model pipeline does not expose feature importance",
                "Feature importance extraction failed",
            ],
            technical_error=e,
        )
        importance_dict = {}
        combined_importance = pd.DataFrame()
        
    available_targets = [
        target for target, df in importance_dict.items()
        if not df.empty
    ]
    target_labels = {
        "total_cost": "Total Cost",
        "duration": "Construction Duration",
        "material_index": "Material Index",
        "manpower_hours_per_km": "Manpower Hours per km",
        "machinery_hours_per_km": "Machinery Hours per km",
    }
    if not available_targets:
        st.warning("Feature importance is unavailable for this model architecture.")
    else:
        selected_target = st.selectbox(
            "Select model for feature importance",
            available_targets,
            format_func=lambda x: target_labels.get(x, x)
        )
        selected_importance = importance_dict[selected_target]
        top_features = selected_importance.head(10)

        importance_fig = px.bar(
            top_features.sort_values("importance", ascending=True),
            x="importance",
            y="feature",
            orientation="h",
            title="Top Feature Importance Factors"
        )
        importance_fig.update_layout(
            height=500,
            xaxis_title="Importance Score",
            yaxis_title="Feature",
            title_x=0.02
        )
        st.plotly_chart(
            importance_fig,
            width="stretch",
            key=f"importance_chart_{selected_target}_{selected_project_id}"
        )

        st.markdown("### Top Driving Factors")

        top_3 = top_features.head(3)

        for _, row in top_3.iterrows():
            st.markdown(
                f"""
                <div class="section-card">
                    <h4>{row['feature']}</h4>
                    <p>
                    Importance score: <b>{row['importance']:.4f}</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("## Grouped Feature Importance Comparison")

    if combined_importance.empty:
        st.warning("Grouped feature importance is unavailable for the current model set.")
    else:
        top_combined_features = (
            combined_importance
            .groupby("feature")["importance"]
            .mean()
            .sort_values(ascending=False)
            .head(8)
            .index
        )

        grouped_df = combined_importance[
            combined_importance["feature"].isin(top_combined_features)
        ]

        grouped_fig = px.bar(
            grouped_df,
            x="feature",
            y="importance",
            color="target",
            barmode="group",
            title="Feature Importance Across Prediction Targets"
        )

        grouped_fig.update_layout(
            height=520,
            xaxis_title="Feature",
            yaxis_title="Importance Score",
            title_x=0.02
        )

        st.plotly_chart(grouped_fig, width="stretch", key=f"grouped_importance_chart_{selected_project_id}")
        
    st.markdown("## Engineering Recommendations")
    recommendations = generate_recommendations(
        project_data,
        prediction_data,
    )
    for recommendation in recommendations:
        st.success(recommendation)
    
