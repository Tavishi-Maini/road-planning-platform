import streamlit as st

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.database.db import init_database
from src.pages.dashboard import render_dashboard
from src.pages.new_project import render_new_project
from src.pages.prediction import render_prediction
from src.pages.results import render_results
from src.pages.comparison import render_comparison
from src.pages.reports import render_reports
from src.pages.settings import render_settings
from src.database.demo_seed import seed_demo_projects
from src.database.project_repository import delete_duplicate_projects

st.set_page_config(
    page_title="RoadPlan AI",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
init_database()
if "demo_seeded" not in st.session_state:
    seed_demo_projects()
    st.session_state["demo_seeded"] = True

page = render_sidebar()

if page == "Dashboard":
    render_dashboard()
elif page == "New Project":
    render_new_project()
elif page == "Prediction":
    render_prediction()
elif page == "Results Dashboard":
    render_results()
elif page == "Compare Projects":
    render_comparison()
elif page == "Reports":
    render_reports()
elif page == "Settings":
    render_settings()