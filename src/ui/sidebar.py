import streamlit as st


PAGES = [
    "Dashboard",
    "New Project",
    "Prediction",
    "Results Dashboard",
    "Compare Projects",
    "Reports",
    "Settings",
]


def render_sidebar():
    if "navigation_page" not in st.session_state:
        st.session_state.navigation_page = "Dashboard"

    if st.session_state.navigation_page not in PAGES:
        st.session_state.navigation_page = "Dashboard"

    with st.sidebar:
        st.markdown("## 🛣️ RoadPlan AI")
        st.caption("Infrastructure Planning Intelligence")

        st.markdown("---")

        st.radio(
            "Navigation",
            PAGES,
            key="navigation_page",
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption("Prototype v1.0")

    return st.session_state.navigation_page