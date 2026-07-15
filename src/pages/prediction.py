import streamlit as st
import pandas as pd
from src.ui.navigation import navigate_to
from src.ml.model_loader import load_models
from src.ml.predictor import prepare_features
from src.utils.formatters import format_cost_lakhs_as_cr

from src.ui.components import page_header, metric_card, friendly_error_box
from src.database.project_repository import (
    get_all_projects,
    get_project_by_id,
    update_project_prediction,
    delete_project
)
from src.ml.predictor import run_prediction, validate_project_features
    
    
def render_prediction():
    page_header(
        "Prediction",
        "Run AI-based cost, duration, material, manpower, and machinery estimation"
    )
    
    if "completed_prediction_project_id" not in st.session_state:
        st.session_state.completed_prediction_project_id = None

    if "latest_predictions" not in st.session_state:
        st.session_state.latest_predictions = None

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning("No saved projects found. Create a project first from the New Project page.")
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": row.id
        for row in projects_df.itertuples()
    }

    project_labels = list(project_options.keys())

    requested_project_id = st.session_state.get(
        "selected_prediction_project_id"
    )

    requested_label = None

    if requested_project_id is not None:
        for label, project_id in project_options.items():
            if project_id == requested_project_id:
                requested_label = label
                break

    # Set the widget value before the selectbox is created
    if requested_label is not None:
        st.session_state["prediction_project_selector"] = requested_label
    elif "prediction_project_selector" not in st.session_state:
        st.session_state["prediction_project_selector"] = project_labels[0]

    selected_project_label = st.selectbox(
        "Select saved project",
        project_labels,
        key="prediction_project_selector",
    )

    selected_project_id = project_options[selected_project_label]
    
    project_data = get_project_by_id(selected_project_id)
    if project_data is None:
        st.error(
            f"Project ID {selected_project_id} no longer exists in the database."
        )
        st.session_state.pop(
            "prediction_project_selector",
            None,
        )
        st.session_state.pop(
            "selected_prediction_project_id",
            None,
        )
        return

    st.session_state.selected_prediction_project_id = selected_project_id
    
    # if (
    #     st.session_state.completed_prediction_project_id is not None
    #    and st.session_state.completed_prediction_project_id != selected_project_id
    # ):
    #     st.session_state.completed_prediction_project_id = None
    #     st.session_state.latest_predictions = None

    st.markdown("## Selected Project Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Project", project_data["project_name"], "Selected project")

    with col2:
        metric_card("Road Length", f"{project_data['road_length_km']} km", "Input feature")

    with col3:
        metric_card("AADT", project_data["aadt"], "Traffic demand")

    with col4:
        metric_card("Risk Level", project_data["risk_level"], "Planning risk")

    st.markdown("## Feature Validation")

    missing_features = validate_project_features(project_data)

    if missing_features:
        st.error("Some required ML features are missing.")
        st.write(missing_features)
        st.info("Go back to New Project and complete these fields before prediction.")
        return

    st.success("All required ML features are available.")

    with st.expander("View model input features"):
        input_preview = pd.DataFrame([{
            feature: project_data.get(feature)
            for feature in project_data.keys()
            if isinstance(project_data.get(feature), (int, float))
        }])
        st.dataframe(input_preview, width="stretch", hide_index=True)

    st.markdown("## Run Prediction")

    run_prediction_clicked = st.button(
        "Run AI Estimation",
        type="primary",
        width="stretch",
        key=f"run_prediction_{selected_project_id}",
    )

    if run_prediction_clicked:
        try:
            with st.spinner("Running AI estimation models..."):
                result = run_prediction(project_data)

            if not result.get("success"):
                friendly_error_box(
                    "Prediction could not be completed.",
                    possible_reasons=[
                        "Some required project fields are missing",
                        "Feature names do not match the trained model",
                        "One or more input values are unsupported",
                    ],
                )
                return

            predictions = result["predictions"]

            update_project_prediction(
                selected_project_id,
                predictions,
            )

            st.session_state["latest_prediction_project_id"] = selected_project_id
            st.session_state["latest_predictions"] = predictions
            st.session_state["prediction_just_completed"] = True

        except FileNotFoundError as error:
            friendly_error_box(
                "Prediction could not be completed.",
                possible_reasons=[
                    "One or more model files are missing",
                    "The model directory is incorrect",
                    "A configured model filename is invalid",
                ],
                technical_error=error,
            )
            return

        except ValueError as error:
            friendly_error_box(
                "Prediction could not be completed.",
                possible_reasons=[
                    "Input columns do not match the trained model",
                    "A categorical value is unsupported",
                    "A numeric field contains an invalid value",
                ],
                technical_error=error,
            )
            return

        except Exception as error:
            friendly_error_box(
                "Prediction could not be completed.",
                possible_reasons=[
                    "Project inputs are incomplete",
                    "A trained model could not be loaded",
                    "The model received an unsupported value",
                ],
                technical_error=error,
            )
            return

    prediction_is_available = (
        st.session_state.get("latest_prediction_project_id")
        == selected_project_id
        and st.session_state.get("latest_predictions") is not None
    )

    if prediction_is_available:
        predictions = st.session_state["latest_predictions"]

        if st.session_state.get("prediction_just_completed"):
            st.success("Prediction completed successfully.")
            st.session_state["prediction_just_completed"] = False

        st.markdown("## Prediction Output")

        p1, p2, p3, p4, p5 = st.columns(5)

        with p1:
            metric_card(
                "Total Cost",
                format_cost_lakhs_as_cr(predictions["total_cost"]),
                "Estimated project cost",
            )

        with p2:
            metric_card(
                "Duration",
                f"{predictions['duration']:.2f} months",
                "Estimated construction duration",
            )

        with p3:
            metric_card(
                "Material Index",
                f"{predictions['material_index']:.2f}",
                "Material intensity score",
            )

        with p4:
            metric_card(
                "Manpower Hours/km",
                f"{predictions['manpower_hours_per_km']:.2f}",
                "Labour intensity",
            )

        with p5:
            metric_card(
                "Machinery Hours/km",
                f"{predictions['machinery_hours_per_km']:.2f}",
                "Equipment intensity",
            )

        st.markdown("---")

        if st.button(
            "View Results Dashboard →",
            type="primary",
            width="stretch",
            key=f"view_results_{selected_project_id}",
        ):
            navigate_to(
                "Results Dashboard",
                selected_result_project_id=selected_project_id,
            )