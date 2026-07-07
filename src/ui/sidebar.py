import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛣️ RoadPlan AI")
        st.caption("Infrastructure Planning Intelligence")

        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "New Project",
                "Prediction",
                "Results Dashboard",
                "Compare Projects",
                "Reports",
                "Settings",
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.caption("Built for infrastructure planning demos")
        st.caption("Local SQLite • ML-powered • Report-ready")

    return page