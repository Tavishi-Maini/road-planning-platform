import streamlit as st

def empty_state(title, message, icon="📭"):
    st.markdown(
        f"""
        <div class="section-card" style="text-align:center;">
            <h2>{icon}</h2>
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def success_alert(message):
    st.success(f"✅ {message}")


def warning_alert(message):
    st.warning(f"⚠️ {message}")


def error_alert(message):
    st.error(f"❌ {message}")


def info_alert(message):
    st.info(f"ℹ️ {message}")


def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.markdown("---")


def metric_card(title, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <p style="font-size: 0.85rem; color: #6B7280; margin-bottom: 0.3rem;">
                {title}
            </p>
            <h2 style="margin: 0; color: #111827;">
                {value}
            </h2>
            <p style="font-size: 0.8rem; color: #6B7280; margin-top: 0.4rem;">
                {note}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def placeholder_card(title, description):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def friendly_error_box(title, possible_reasons=None, technical_error=None):
    if possible_reasons is None:
        possible_reasons = [
            "Missing or incomplete project fields",
            "Invalid model file or model path",
            "Unsupported input values",
        ]

    reasons_html = "".join([f"<li>{reason}</li>" for reason in possible_reasons])

    st.markdown(
        f"""
        <div class="section-card" style="border-left: 5px solid #DC2626;">
            <h3>❌ {title}</h3>
            <p><b>Possible reasons:</b></p>
            <ul>
                {reasons_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    if technical_error:
        with st.expander("Show technical details"):
            st.exception(technical_error)