import json
import streamlit as st
import time
from src.ui.components import page_header, friendly_error_box
from src.database.project_repository import get_all_projects, get_project_by_id
from src.reports.pdf_generator import generate_pdf_report
from src.reports.excel_generator import generate_excel_report
from src.ml.feature_importance import get_model_feature_importance


def render_reports():
    page_header(
        "Reports",
        "Generate downloadable PDF and Excel planning reports"
    )

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning("No projects available.")
        return

    completed_projects = projects_df[
        projects_df["prediction_status"] == "Completed"
    ]

    if completed_projects.empty:
        st.warning("No completed predictions found. Run predictions first.")
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": row.id
        for row in completed_projects.itertuples()
    }

    selected_project_label = st.selectbox(
        "Select project for report generation",
        list(project_options.keys())
    )

    selected_project_id = project_options[selected_project_label]

    selected_row = completed_projects[
        completed_projects["id"] == selected_project_id
    ].iloc[0]

    project_data = get_project_by_id(selected_project_id)
    prediction_data = json.loads(selected_row["prediction_data"])

    st.markdown("## Report Options")

    include_pdf = st.checkbox("Generate PDF Report", value=True)
    include_excel = st.checkbox("Generate Excel Workbook", value=True)
    include_feature_importance = st.checkbox("Include Feature Importance", value=True)

    feature_importance_df = None

    if include_feature_importance:
        try:
            importance_dict = get_model_feature_importance()
            feature_importance_df = importance_dict.get("total_cost")
        except Exception as e:
            st.warning("Feature importance could not be loaded.")
            st.exception(e)

    st.markdown("## Project Preview")

    st.write({
        "Project Name": project_data.get("project_name"),
        "Location": project_data.get("location"),
        "Road Length": project_data.get("road_length_km"),
        "Prediction Status": selected_row["prediction_status"],
    })

    st.markdown("## Generate Downloads")

    if include_pdf:
        try:
            with st.spinner("Generating professional PDF report..."):
                pdf_buffer = generate_pdf_report(
                    project_data=project_data,
                    prediction_data=prediction_data,
                    feature_importance_df=feature_importance_df,
                )

            st.success("PDF report generated successfully.")

        except Exception as e:
            friendly_error_box(
                "PDF report could not be generated.",
                possible_reasons=[
                    "Prediction data is missing",
                    "Report template failed",
                    "Chart or table data is incomplete",
                ],
                technical_error=e,
            )

        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name=f"{project_data.get('project_name', 'road_project')}_report.pdf",
            mime="application/pdf",
            width="stretch",
        )

    if include_excel:
        try:
            with st.spinner("Preparing Excel workbook..."):
                excel_buffer = generate_excel_report(
                    project_data=project_data,
                    prediction_data=prediction_data,
                    feature_importance_df=feature_importance_df,
                )
            st.success("Excel report generated successfully.")

        except Exception as e:
            friendly_error_box(
                "Excel report could not be generated.",
                possible_reasons=[
                    "Prediction data is missing",
                    "Workbook formatting failed",
                    "Feature importance table is incomplete",
                ],
                technical_error=e,
            )

        st.download_button(
            label="Download Excel Report",
            data=excel_buffer,
            file_name=f"{project_data.get('project_name', 'road_project')}_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.info(
        "Reports are generated from saved project inputs and completed ML predictions."
    )