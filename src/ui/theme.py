import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #111827;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        .metric-card {
            background: #FFFFFF;
            color: #111827;
            padding: 1.2rem;
            border-radius: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-left: 5px solid #F59E0B;
        }

        .section-card {
            background: #FFFFFF;
            color: #111827;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            margin-bottom: 1rem;
        }
        
        /* ---------- Text Input ---------- */
        [data-testid="stTextInput"] input {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
        }

        /* ---------- Number Input ---------- */
        [data-testid="stNumberInput"] input {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
        }

        /* ---------- Text Area ---------- */
        [data-testid="stTextArea"] textarea {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
        }

        /* ---------- Select Box ---------- */
        [data-baseweb="select"] > div {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
        }

        /* ---------- Focus State ---------- */
        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-baseweb="select"] > div:focus-within {
            border: 2px solid #F59E0B !important;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15) !important;
        }

        [data-testid="stForm"] {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        }

        button[kind="primary"] {
            background-color: #F59E0B !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }

        button[kind="primary"] * {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )