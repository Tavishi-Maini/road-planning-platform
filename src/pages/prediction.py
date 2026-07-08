import streamlit as st
import pandas as pd
from src.ml.model_loader import load_models
from src.ml.predictor import prepare_features

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

    projects_df = get_all_projects()

    if projects_df.empty:
        st.warning("No saved projects found. Create a project first from the New Project page.")
        return

    project_options = {
        f"{row.project_name} | ID: {row.id}": row.id
        for row in projects_df.itertuples()
    }

    selected_project_label = st.selectbox(
        "Select saved project",
        list(project_options.keys())
    )

    selected_project_id = project_options[selected_project_label]
    project_data = get_project_by_id(selected_project_id)

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

    if st.button("Run AI Estimation", width="stretch"):
        try:
            with st.spinner("Running AI estimation models..."):
                result = run_prediction(project_data)

            if not result["success"]:
                friendly_error_box(
                    "Prediction could not be completed.",
                    possible_reasons=[
                        "Some required project fields are missing",
                        "Feature names do not match the trained model",
                        "One or more input values are outside the supported range",
                    ],
                )
                return

            predictions = result["predictions"]
            update_project_prediction(selected_project_id, predictions)

            st.success("Prediction completed successfully.")

            st.markdown("## Prediction Output")

            p1, p2, p3, p4, p5 = st.columns(5)

            with p1:
                metric_card("Total Cost", f"₹{predictions['total_cost']:.2f}", "Estimated project cost")

            with p2:
                metric_card("Duration", f"{predictions['duration']:.2f} months", "Estimated construction duration")

            with p3:
                metric_card("Material Index", f"{predictions['material_index']:.2f}", "Material intensity score")

            with p4:
                metric_card("Manpower Hours/km", f"{predictions['manpower_hours_per_km']:.2f}", "Labour intensity")

            with p5:
                metric_card("Machinery Hours/km", f"{predictions['machinery_hours_per_km']:.2f}", "Equipment intensity")

            st.info("These results are now saved locally and will be used in the Results Dashboard phase.")

        except FileNotFoundError as e:
            friendly_error_box(
                "Prediction could not be completed.",
                possible_reasons=[
                    "One or more .joblib model files are missing",
                    "The model directory path is incorrect",
                    "Model filenames do not match the configured names",
                ],
                technical_error=e,
            )

        except ValueError as e:
            friendly_error_box(
                "Prediction could not be completed.",
                possible_reasons=[
                    "Input columns do not match the trained model",
                    "A categorical value is unsupported",
                    "A numeric field contains an invalid value",
                ],
                technical_error=e,
            )

        except Exception as e:
            friendly_error_box(
                "Prediction could not be completed.",
                possible_reasons=[
                    "Missing project fields",
                    "Invalid model file",
                    "Unsupported input values",
                ],
                technical_error=e,
            )