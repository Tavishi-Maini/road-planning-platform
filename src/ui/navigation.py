import streamlit as st


VALID_PAGES = {
    "Dashboard",
    "New Project",
    "Prediction",
    "Results Dashboard",
    "Compare Projects",
    "Reports",
    "Settings",
}


def navigate_to(page_name: str, **state_values) -> None:
    if page_name not in VALID_PAGES:
        raise ValueError(f"Unknown page: {page_name}")

    for key, value in state_values.items():
        st.session_state[key] = value

    st.session_state["active_page"] = page_name
    st.rerun()