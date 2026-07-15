import streamlit as st


PAGES = [
    ("📊", "Dashboard"),
    ("➕", "New Project"),
    ("🤖", "Prediction"),
    ("📈", "Results Dashboard"),
    ("⚖️", "Compare Projects"),
    ("📄", "Reports"),
    ("⚙️", "Settings"),
]


def select_page(page_name: str) -> None:
    st.session_state["active_page"] = page_name


def render_sidebar() -> str:
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"

    with st.sidebar:
        st.markdown("## 🛣️ RoadPlan AI")
        st.caption("Infrastructure Planning Intelligence")
        st.markdown("---")

        for icon, page_name in PAGES:
            is_active = st.session_state["active_page"] == page_name

            st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                type="primary" if is_active else "secondary",
                width="stretch",
                on_click=select_page,
                args=(page_name,),
            )

        st.markdown("---")
        st.caption("Prototype v1.0")

    return st.session_state["active_page"]