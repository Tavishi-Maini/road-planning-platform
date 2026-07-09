import streamlit as st


def render_sidebar():
    pages = [
        "Dashboard",
        "New Project",
        "Prediction",
        "Results Dashboard",
        "Compare Projects",
        "Reports",
        "Settings",
    ]

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Dashboard"

    with st.sidebar:
        st.markdown("## 🛣️ RoadPlan AI")
        st.caption("Infrastructure Planning Intelligence")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            pages,
            index=pages.index(st.session_state.active_page),
            label_visibility="collapsed",
        )

        st.session_state.active_page = page

        st.markdown("---")
        st.caption("Prototype v1.0")

    return st.session_state.active_page