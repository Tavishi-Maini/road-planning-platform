import json

import pandas as pd
import streamlit as st

from src.database.project_repository import (
    get_all_projects,
    get_project_by_id,
)
from src.ml.feature_importance import (
    get_model_feature_importance,
)
from src.reports.excel_generator import (
    generate_excel_report,
)
from src.reports.pdf_generator import (
    generate_pdf_report,
)
from src.ui.components import (
    friendly_error_box,
    page_header,
)


REQUIRED_PREDICTION_FIELDS = [
    "total_cost",
    "duration",
    "material_index",
    "manpower_hours_per_km",
    "machinery_hours_per_km",
]


def normalize_prediction_data(data):
    """
    Convert old and new prediction field names into one standard format.
    """

    if not isinstance(data, dict):
        return {}

    return {
        "total_cost": data.get(
            "total_cost",
            data.get("total_cost_lakhs"),
        ),
        "duration": data.get(
            "duration",
            data.get("construction_duration_months"),
        ),
        "material_index": data.get(
            "material_index"
        ),
        "manpower_hours_per_km": data.get(
            "manpower_hours_per_km"
        ),
        "machinery_hours_per_km": data.get(
            "machinery_hours_per_km"
        ),
    }


def load_prediction_data(raw_prediction_data):
    """
    Load prediction data stored as JSON text or a Python dictionary.
    """

    if raw_prediction_data is None:
        return None

    try:
        if pd.isna(raw_prediction_data):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(raw_prediction_data, str):
        data = json.loads(raw_prediction_data)

    elif isinstance(raw_prediction_data, dict):
        data = raw_prediction_data

    else:
        raise TypeError(
            "Saved prediction data has an unsupported format."
        )

    return normalize_prediction_data(data)


def safe_file_name(value):
    """
    Create a safe file name from a project name.
    """

    value = str(value or "road_project").strip()

    safe_characters = []

    for character in value:
        if character.isalnum() or character in {
            "-",
            "_",
        }:
            safe_characters.append(character)
        elif character.isspace():
            safe_characters.append("_")

    file_name = "".join(safe_characters).strip("_")

    return file_name or "road_project"


def render_reports():
    page_header(
        "Reports",
        "Generate downloadable PDF and Excel planning reports",
    )

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning("No projects are available.")
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
            "No completed predictions were found. "
            "Run predictions first."
        )
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": int(row.id)
        for row in completed_projects.itertuples()
    }

    project_labels = list(project_options.keys())

    requested_project_id = st.session_state.get(
        "selected_report_project_id"
    )

    default_index = 0

    if requested_project_id is not None:
        for index, label in enumerate(project_labels):
            if (
                project_options[label]
                == int(requested_project_id)
            ):
                default_index = index
                break

    selected_project_label = st.selectbox(
        "Select project for report generation",
        options=project_labels,
        index=default_index,
        key="report_project_selector",
    )

    selected_project_id = project_options[
        selected_project_label
    ]

    st.session_state[
        "selected_report_project_id"
    ] = selected_project_id

    project_data = get_project_by_id(
        selected_project_id
    )

    if project_data is None:
        st.error(
            "The selected project could not be loaded. "
            "It may have been deleted or the database record "
            "may be unavailable."
        )
        return

    matching_rows = completed_projects[
        completed_projects["id"]
        == selected_project_id
    ]

    if matching_rows.empty:
        st.error(
            "The completed prediction record for the selected "
            "project could not be found."
        )
        return

    selected_row = matching_rows.iloc[0]

    raw_prediction_data = selected_row.get(
        "prediction_data"
    )

    try:
        prediction_data = load_prediction_data(
            raw_prediction_data
        )

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ) as error:
        friendly_error_box(
            "Prediction data could not be loaded for report generation.",
            possible_reasons=[
                "Saved prediction data is corrupted",
                "The selected project has incomplete prediction results",
                "The saved prediction format is unsupported",
            ],
            technical_error=error,
        )
        return

    if prediction_data is None:
        st.warning(
            "This project does not have saved prediction data. "
            "Run the prediction again before generating reports."
        )
        return

    missing_fields = [
        field
        for field in REQUIRED_PREDICTION_FIELDS
        if prediction_data.get(field) is None
    ]

    if missing_fields:
        st.warning(
            "This project has incomplete prediction data. "
            "Run the prediction again before generating reports."
        )

        st.write("Missing prediction fields:")
        st.json(missing_fields)
        return

    try:
        prediction_data = {
            "total_cost": float(
                prediction_data["total_cost"]
            ),
            "duration": float(
                prediction_data["duration"]
            ),
            "material_index": float(
                prediction_data["material_index"]
            ),
            "manpower_hours_per_km": float(
                prediction_data[
                    "manpower_hours_per_km"
                ]
            ),
            "machinery_hours_per_km": float(
                prediction_data[
                    "machinery_hours_per_km"
                ]
            ),
        }

    except (TypeError, ValueError) as error:
        friendly_error_box(
            "Prediction values could not be prepared for report generation.",
            possible_reasons=[
                "One or more prediction values are not numeric",
                "The prediction data is incomplete",
                "The saved prediction format is invalid",
            ],
            technical_error=error,
        )
        return

    st.markdown("## Report Options")

    include_pdf = st.checkbox(
        "Generate PDF Report",
        value=True,
    )

    include_excel = st.checkbox(
        "Generate Excel Workbook",
        value=True,
    )

    include_feature_importance = st.checkbox(
        "Include Feature Importance",
        value=True,
    )

    feature_importance_df = None

    if include_feature_importance:
        try:
            importance_dict = (
                get_model_feature_importance()
            )

            feature_importance_df = (
                importance_dict.get("total_cost")
            )

            if (
                feature_importance_df is None
                or feature_importance_df.empty
            ):
                st.info(
                    "Total-cost feature importance is unavailable. "
                    "The report will be generated without it."
                )
                feature_importance_df = None

        except Exception as error:
            st.warning(
                "Feature importance could not be loaded. "
                "The report will still be generated."
            )

            with st.expander(
                "Feature importance error details"
            ):
                st.exception(error)

            feature_importance_df = None

    st.markdown("## Project Preview")

    preview_data = {
        "Project Name": project_data.get(
            "project_name",
            "Unknown",
        ),
        "Location": project_data.get(
            "location",
            "Unknown",
        ),
        "Road Length": (
            f"{project_data.get('road_length_km', 0)} km"
        ),
        "Road Category": project_data.get(
            "road_category",
            "Unknown",
        ),
        "Terrain": project_data.get(
            "terrain_type",
            "Unknown",
        ),
        "Prediction Status": selected_row.get(
            "prediction_status",
            "Completed",
        ),
        "Total Cost": (
            f"₹{prediction_data['total_cost'] / 100:,.2f} Cr"
        ),
        "Duration": (
            f"{prediction_data['duration']:,.2f} months"
        ),
    }

    st.write(preview_data)

    st.markdown("## Generate Downloads")

    if not include_pdf and not include_excel:
        st.info(
            "Select at least one report format."
        )
        return

    project_file_name = safe_file_name(
        project_data.get("project_name")
    )

    if include_pdf:
        pdf_buffer = None

        try:
            with st.spinner(
                "Generating professional PDF report..."
            ):
                pdf_buffer = generate_pdf_report(
                    project_data=project_data,
                    prediction_data=prediction_data,
                    feature_importance_df=(
                        feature_importance_df
                    ),
                )

            if pdf_buffer is None:
                raise ValueError(
                    "The PDF generator returned no report data."
                )

            st.success(
                "PDF report generated successfully."
            )

        except Exception as error:
            friendly_error_box(
                "PDF report could not be generated.",
                possible_reasons=[
                    "Prediction data is missing",
                    "Report template generation failed",
                    "Chart or table data is incomplete",
                    "The PDF generator returned no output",
                ],
                technical_error=error,
            )

        if pdf_buffer is not None:
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name=(
                    f"{project_file_name}_report.pdf"
                ),
                mime="application/pdf",
                width="stretch",
                key=(
                    f"download_pdf_"
                    f"{selected_project_id}"
                ),
            )

    if include_excel:
        excel_buffer = None

        try:
            with st.spinner(
                "Preparing Excel workbook..."
            ):
                excel_buffer = generate_excel_report(
                    project_data=project_data,
                    prediction_data=prediction_data,
                    feature_importance_df=(
                        feature_importance_df
                    ),
                )

            if excel_buffer is None:
                raise ValueError(
                    "The Excel generator returned no workbook data."
                )

            st.success(
                "Excel workbook generated successfully."
            )

        except Exception as error:
            friendly_error_box(
                "Excel report could not be generated.",
                possible_reasons=[
                    "Prediction data is missing",
                    "Workbook formatting failed",
                    "Feature importance data is incomplete",
                    "The Excel generator returned no output",
                ],
                technical_error=error,
            )

        if excel_buffer is not None:
            st.download_button(
                label="Download Excel Report",
                data=excel_buffer,
                file_name=(
                    f"{project_file_name}_report.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                width="stretch",
                key=(
                    f"download_excel_"
                    f"{selected_project_id}"
                ),
            )

    st.info(
        "Reports are generated from saved project inputs "
        "and completed ML predictions."
    )