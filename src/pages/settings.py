import streamlit as st
from pathlib import Path

from src.ui.components import page_header
from src.config.app_settings import load_settings, save_settings


def render_settings():
    page_header(
        "Settings",
        "Configure model paths, storage, reporting, and display preferences"
    )

    settings = load_settings()

    st.markdown("## Model Configuration")

    model_dir = st.text_input(
        "Model Directory",
        value=settings["model_dir"],
        help="Folder where all .joblib ML model files are stored."
    )

    st.caption("Expected model files:")
    st.code(
        """
total_cost_model.joblib
duration_model.joblib
material_index_model.joblib
manpower_model.joblib
machinery_model.joblib
        """.strip()
    )

    model_path = Path(model_dir)

    if model_path.exists():
        st.success("Model directory found.")
    else:
        st.warning("Model directory does not currently exist.")

    st.markdown("---")
    st.markdown("## Database Configuration")

    database_path = st.text_input(
        "SQLite Database Path",
        value=settings["database_path"],
        help="Local SQLite database used for saved projects and predictions."
    )

    db_path = Path(database_path)

    if db_path.exists():
        st.success("Database file found.")
    else:
        st.info("Database file will be created automatically when the app runs.")

    st.markdown("---")
    st.markdown("## Display Preferences")

    col1, col2 = st.columns(2)

    with col1:
        currency_format = st.selectbox(
            "Currency Format",
            ["INR Lakhs", "INR Crore", "INR Raw"],
            index=["INR Lakhs", "INR Crore", "INR Raw"].index(settings["currency_format"])
        )

        unit_system = st.selectbox(
            "Unit System",
            ["Metric", "Mixed"],
            index=["Metric", "Mixed"].index(settings["unit_system"])
        )

    with col2:
        theme_mode = st.selectbox(
            "Theme Mode",
            ["Light", "Dark"],
            index=["Light", "Dark"].index(settings["theme_mode"])
        )

        show_confidence = st.checkbox(
            "Show Confidence / Status Messages",
            value=settings["show_confidence"]
        )

    st.markdown("---")
    st.markdown("## Report Branding")

    organization_name = st.text_input(
        "Organization / Product Name",
        value=settings["organization_name"]
    )

    report_title = st.text_input(
        "Default Report Title",
        value=settings["report_title"]
    )

    prepared_by = st.text_input(
        "Prepared By",
        value=settings["prepared_by"]
    )

    st.markdown("---")

    if st.button("Save Settings", width="stretch"):
        updated_settings = {
            "model_dir": model_dir,
            "database_path": database_path,
            "currency_format": currency_format,
            "unit_system": unit_system,
            "theme_mode": theme_mode,
            "organization_name": organization_name,
            "report_title": report_title,
            "prepared_by": prepared_by,
            "show_confidence": show_confidence,
        }

        save_settings(updated_settings)

        st.success("Settings saved successfully.")

    with st.expander("View Current Settings JSON"):
        st.json(load_settings())