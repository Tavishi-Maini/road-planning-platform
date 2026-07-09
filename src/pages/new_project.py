import streamlit as st
from src.ui.components import page_header
from src.database.project_repository import save_project, project_exists
from src.database.project_repository import get_all_projects, delete_project, get_project_by_id

def validate_numeric_inputs(project_data):
    errors = []

    rules = {
        "road_length_km": ("Road Length", 0.1, 5000),
        "carriageway_width_m": ("Carriageway Width", 1, 100),
        "number_of_lanes": ("Number of Lanes", 1, 12),
        "shoulder_width_m": ("Shoulder Width", 0, 20),
        "design_speed_kmph": ("Design Speed", 10, 160),
        "bridges_culverts": ("Bridges/Culverts", 0, 10000),
        "aadt": ("AADT", 1, 500000),
        "traffic_growth_rate_pct": ("Traffic Growth Rate", 0, 20),
        "vdf": ("Vehicle Damage Factor", 0, 20),
        "gsb_thickness_mm": ("GSB Thickness", 0, 1000),
        "wmm_thickness_mm": ("WMM Thickness", 0, 1000),
        "dbm_thickness_mm": ("DBM Thickness", 0, 500),
        "bc_thickness_mm": ("BC Thickness", 0, 200),
        "concrete_thickness_mm": ("Concrete Thickness", 0, 1000),
        "subgrade_cbr_pct": ("Subgrade CBR", 1, 100),
        "aggregate_source_distance_km": ("Aggregate Source Distance", 0, 500),
        "material_quality_index": ("Material Quality Index", 0, 100),
        "water_body_distance_m": ("Water Body Distance", 0, 100000),
        "labour_rate_inr_day": ("Labour Rate", 1, 10000),
        "skilled_labour_pct": ("Skilled Labour Percentage", 0, 100),
        "machinery_availability_pct": ("Machinery Availability", 0, 100),
        "fuel_cost_inr_litre": ("Fuel Cost", 1, 300),
        "equipment_productivity_index": ("Equipment Productivity Index", 0, 100),
        "contractor_experience_index": ("Contractor Experience Index", 0, 100),
        "contingency_pct": ("Contingency", 0, 50),
        "escalation_pct": ("Price Escalation", 0, 50),
    }

    for key, (label, min_value, max_value) in rules.items():
        value = project_data.get(key)

        if value is None:
            errors.append(f"{label} is missing.")
            continue

        if value < min_value:
            errors.append(f"{label} must be at least {min_value}.")

        if value > max_value:
            errors.append(f"{label} must not exceed {max_value}.")

    return errors


def render_new_project():
    page_header("New Project", "Create and validate a new road construction project")

    if "projects" not in st.session_state:
        st.session_state.projects = []
        
    if "delete_project_id" not in st.session_state:
        st.session_state.delete_project_id = None

    st.info("Fields marked with * are required.")

    with st.form("new_project_form"):
        st.markdown("## 1. Basic Project Details")

        col1, col2 = st.columns(2)

        with col1:
            project_name = st.text_input("Project Name *")
            location = st.text_input("Location / District *")
            road_category = st.selectbox(
                "Road Category *",
                ["National Highway", "State Highway", "Urban Road", "Rural Road", "Expressway"]
            )

        with col2:
            project_owner = st.text_input("Project Owner / Authority")
            terrain_type = st.selectbox(
                "Terrain Type *",
                ["Plain", "Rolling", "Hilly", "Mountainous"]
            )
            project_stage = st.selectbox(
                "Project Stage",
                ["Concept", "DPR", "Tender", "Execution", "Monitoring"]
            )

        st.markdown("## 2. Road Geometry")

        col1, col2, col3 = st.columns(3)

        with col1:
            road_length = st.number_input("Road Length (km) *", min_value=0.1, step=0.1)
            carriageway_width = st.number_input("Carriageway Width (m) *", min_value=1.0, step=0.5)

        with col2:
            lanes = st.number_input("Number of Lanes *", min_value=1, max_value=12, step=1)
            shoulder_width = st.number_input("Shoulder Width (m)", min_value=0.0, step=0.5)

        with col3:
            design_speed = st.number_input("Design Speed (km/h) *", min_value=10, max_value=160, step=5)
            bridges_culverts = st.number_input("Number of Bridges/Culverts", min_value=0, step=1)

        st.markdown("## 3. Traffic Inputs")

        col1, col2, col3 = st.columns(3)

        with col1:
            aadt = st.number_input("AADT *", min_value=0, step=100, help="Average Annual Daily Traffic")
        with col2:
            traffic_growth = st.number_input("Traffic Growth Rate (%) *", min_value=0.0, max_value=20.0, step=0.5)
        with col3:
            vdf = st.number_input("Vehicle Damage Factor", min_value=0.0, step=0.1)

        st.markdown("## 4. Pavement Design")

        col1, col2, col3 = st.columns(3)

        with col1:
            pavement_type = st.selectbox("Pavement Type *", ["Flexible", "Rigid", "Composite"])
            gsb_thickness = st.number_input("GSB Thickness (mm)", min_value=0, step=10)

        with col2:
            wmm_thickness = st.number_input("WMM Thickness (mm)", min_value=0, step=10)
            dbm_thickness = st.number_input("DBM Thickness (mm)", min_value=0, step=10)

        with col3:
            bc_thickness = st.number_input("BC Thickness (mm)", min_value=0, step=5)
            concrete_thickness = st.number_input("Concrete Thickness (mm)", min_value=0, step=10)

        st.markdown("## 5. Material Properties")

        col1, col2, col3 = st.columns(3)

        with col1:
            soil_type = st.selectbox(
                "Soil Type *",
                ["Clayey", "Silty", "Sandy", "Gravelly", "Black Cotton Soil", "Rocky"]
            )
            cbr = st.number_input("Subgrade CBR (%) *", min_value=1.0, max_value=100.0, step=0.5)

        with col2:
            bitumen_grade = st.selectbox("Bitumen Grade", ["VG-10", "VG-20", "VG-30", "VG-40", "NA"])
            aggregate_distance = st.number_input("Aggregate Source Distance (km)", min_value=0.0, step=1.0)

        with col3:
            material_quality_index = st.slider("Material Quality Index", 0, 100, 70)
            cement_grade = st.selectbox("Cement Grade", ["OPC 43", "OPC 53", "PPC", "NA"])

        st.markdown("## 6. Site Conditions")

        col1, col2, col3 = st.columns(3)

        with col1:
            land_acquisition = st.selectbox("Land Acquisition Complexity", ["Low", "Medium", "High"])
            rainfall_zone = st.selectbox("Rainfall Zone", ["Low", "Moderate", "High", "Very High"])

        with col2:
            utility_shifting = st.selectbox("Utility Shifting Required", ["No", "Yes"])
            environmental_sensitivity = st.selectbox("Environmental Sensitivity", ["Low", "Medium", "High"])

        with col3:
            water_body_distance = st.number_input("Nearest Water Body Distance (m)", min_value=0.0, step=10.0)
            soil_stabilization = st.selectbox("Soil Stabilization Required", ["No", "Yes"])

        st.markdown("## 7. Resource Inputs")

        col1, col2, col3 = st.columns(3)

        with col1:
            labour_rate = st.number_input("Labour Rate (₹/day)", min_value=0, step=100)
            skilled_labour_pct = st.slider("Skilled Labour (%)", 0, 100, 40)

        with col2:
            machinery_availability = st.slider("Machinery Availability (%)", 0, 100, 80)
            fuel_cost = st.number_input("Fuel Cost (₹/litre)", min_value=0.0, step=1.0)

        with col3:
            equipment_productivity = st.slider("Equipment Productivity Index", 0, 100, 75)
            contractor_experience = st.slider("Contractor Experience Index", 0, 100, 70)

        st.markdown("## 8. Risk & Contingency")

        col1, col2, col3 = st.columns(3)

        with col1:
            risk_level = st.selectbox("Overall Risk Level *", ["Low", "Medium", "High"])
        with col2:
            contingency_pct = st.number_input("Contingency (%)", min_value=0.0, max_value=50.0, step=0.5)
        with col3:
            escalation_pct = st.number_input("Price Escalation (%)", min_value=0.0, max_value=50.0, step=0.5)

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted=st.form_submit_button(
                "💾 Save Project",
                width="stretch"
            )
        with col2:
            reset=st.form_submit_button(
                "🔄 Reset Form",
                width="stretch"
            )
            
    if reset:
        st.session_state.clear()
        st.rerun()

    required_fields = {
        "Project Name": project_name,
        "Location": location,
        "Road Length": road_length,
        "Carriageway Width": carriageway_width,
        "Number of Lanes": lanes,
        "Design Speed": design_speed,
        "AADT": aadt,
        "Traffic Growth Rate": traffic_growth,
        "Subgrade CBR": cbr,
    }

    completed = sum(
        1 for value in required_fields.values()
        if value not in ["", None, 0, 0.0]
    )

    progress = completed / len(required_fields)

    st.markdown("## Form Completion")
    st.progress(progress)
    st.caption(f"{completed}/{len(required_fields)} required fields completed")

    st.markdown("---")
    st.markdown("## Project Manager")
    st.info(
        "Manage saved road projects here. You can load details, review saved inputs, or delete outdated test projects."
    )

    projects_df = get_all_projects()

    if projects_df.empty:
        st.info("No saved projects available.")
    else:
        st.dataframe(projects_df, width="stretch", hide_index=True)

        project_options = {
            f"{row.project_name} | ID: {row.id}": row.id
            for row in projects_df.itertuples()
        }

        selected_project = st.selectbox(
            "Select project to manage",
            list(project_options.keys())
        )

        selected_project_id = project_options[selected_project]

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👁 Load Details", width="stretch"):
                project_data = get_project_by_id(selected_project_id)
                st.json(project_data)
        with col2:
            if st.button("➡️ Predict This Project", width="stretch"):
                st.session_state.active_page = "Prediction"
                st.rerun()
        with col3:
            if st.button(
                "🗑 Delete Project",
                key=f"delete_btn_{selected_project_id}",
                width="stretch"
            ):
                st.session_state.delete_project_id = selected_project_id
    
    if st.session_state.delete_project_id is not None:
        project = get_project_by_id(
            st.session_state.delete_project_id
        )
        st.warning(
            f"Are you sure you want to permanently delete "
            f"**{project['project_name']}**? This action cannot be undone."
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "✅ Yes, Delete",
                type="primary",
                key="confirm_delete"
            ):
                delete_project(
                    st.session_state.delete_project_id
                )
                st.session_state.delete_project_id = None
                st.success("Project deleted successfully.")
                st.rerun()

        with c2:
            if st.button(
                "❌ Cancel",
                key="cancel_delete"
            ):
                st.session_state.delete_project_id = None
                st.rerun()

    if submitted:
        missing_fields = [
            field for field, value in required_fields.items()
            if value in ["", None, 0, 0.0]
        ]

        if missing_fields:
            st.error(
                "Please complete the following required fields: "
                + ", ".join(missing_fields)
            )
            return

        project_data = {
            "project_name": project_name,
            "location": location,
            "project_owner": project_owner,
            "road_category": road_category,
            "terrain_type": terrain_type,
            "project_stage": project_stage,
            "road_length_km": road_length,
            "carriageway_width_m": carriageway_width,
            "number_of_lanes": lanes,
            "shoulder_width_m": shoulder_width,
            "design_speed_kmph": design_speed,
            "bridges_culverts": bridges_culverts,
            "aadt": aadt,
            "traffic_growth_rate_pct": traffic_growth,
            "vdf": vdf,
            "pavement_type": pavement_type,
            "gsb_thickness_mm": gsb_thickness,
            "wmm_thickness_mm": wmm_thickness,
            "dbm_thickness_mm": dbm_thickness,
            "bc_thickness_mm": bc_thickness,
            "concrete_thickness_mm": concrete_thickness,
            "soil_type": soil_type,
            "subgrade_cbr_pct": cbr,
            "bitumen_grade": bitumen_grade,
            "aggregate_source_distance_km": aggregate_distance,
            "material_quality_index": material_quality_index,
            "cement_grade": cement_grade,
            "land_acquisition_complexity": land_acquisition,
            "rainfall_zone": rainfall_zone,
            "utility_shifting_required": utility_shifting,
            "environmental_sensitivity": environmental_sensitivity,
            "water_body_distance_m": water_body_distance,
            "soil_stabilization_required": soil_stabilization,
            "labour_rate_inr_day": labour_rate,
            "skilled_labour_pct": skilled_labour_pct,
            "machinery_availability_pct": machinery_availability,
            "fuel_cost_inr_litre": fuel_cost,
            "equipment_productivity_index": equipment_productivity,
            "contractor_experience_index": contractor_experience,
            "risk_level": risk_level,
            "contingency_pct": contingency_pct,
            "escalation_pct": escalation_pct,
            "prediction_status": "Pending",
        }
        
        numeric_errors = validate_numeric_inputs(project_data)
        
        if numeric_errors:
            st.error("Please fix the following input errors before saving:")
            for error in numeric_errors:
                st.write(f"- {error}")
            return

        if project_exists(project_name, location):
            st.warning("A project with the same name and location already exists. Duplicate not saved.")
        else:
            save_project(project_data)
            st.success("Project saved successfully in SQLite database.")
            st.rerun()
            
        st.markdown("### Saved Project Preview")
        st.json(project_data)

        if st.button("➡️ Proceed to Prediction", width="stretch"):
            st.session_state.active_page = "Prediction"
            st.rerun()