import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        /* ---------- App Background ---------- */
        [data-testid="stAppViewContainer"] {
            background-color: #F5F7FA;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 1.5rem;
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1F2937;
        }

        [data-testid="stSidebarContent"] {
            background-color: #111827 !important;
        }

        /* Sidebar headings and normal text */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] small {
            color: #F9FAFB !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: #374151 !important;
        }

        /* ---------- Sidebar Navigation Buttons ---------- */
        [data-testid="stSidebar"] div.stButton > button {
            width: 100% !important;
            min-height: 2.8rem;
            justify-content: flex-start !important;
            text-align: left !important;

            background-color: #1F2937 !important;
            color: #F9FAFB !important;

            border: 1px solid #374151 !important;
            border-radius: 10px !important;

            padding: 0.65rem 0.9rem !important;
            font-weight: 600 !important;

            transition:
                background-color 0.2s ease,
                border-color 0.2s ease,
                transform 0.2s ease;
        }

        [data-testid="stSidebar"] div.stButton > button p,
        [data-testid="stSidebar"] div.stButton > button span {
            color: #F9FAFB !important;
        }

        /* Sidebar button hover */
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #374151 !important;
            border-color: #F59E0B !important;
            color: #FFFFFF !important;
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] div.stButton > button:hover p,
        [data-testid="stSidebar"] div.stButton > button:hover span {
            color: #FFFFFF !important;
        }

        /* Active sidebar button */
        [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background-color: #F59E0B !important;
            color: #111827 !important;
            border-color: #F59E0B !important;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
        }

        [data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
        [data-testid="stSidebar"] div.stButton > button[kind="primary"] span {
            color: #111827 !important;
        }

        [data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
            background-color: #D97706 !important;
            border-color: #D97706 !important;
        }

        /* ---------- Cards ---------- */
        .metric-card {
            background: #FFFFFF;
            color: #111827;
            padding: 1.2rem;
            border-radius: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-left: 5px solid #F59E0B;
        }

        .metric-card h1,
        .metric-card h2,
        .metric-card h3,
        .metric-card h4,
        .metric-card p,
        .metric-card span {
            color: #111827 !important;
        }

        .section-card {
            background: #FFFFFF;
            color: #111827;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            margin-bottom: 1rem;
        }

        .section-card h1,
        .section-card h2,
        .section-card h3,
        .section-card h4,
        .section-card p,
        .section-card span {
            color: #111827 !important;
        }

        /* ---------- Form ---------- */
        [data-testid="stForm"] {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
        }

        [data-testid="stForm"] label p {
            color: #111827 !important;
        }

        /* ---------- Inputs ---------- */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            color: #111827 !important;
            caret-color: #111827 !important;
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
        }

        [data-baseweb="select"] > div {
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
        }

        [data-baseweb="select"] span {
            color: #111827 !important;
        }

        /* ---------- Input Focus ---------- */
        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-baseweb="select"] > div:focus-within {
            border: 2px solid #F59E0B !important;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15) !important;
        }

        /* ---------- Main Buttons ---------- */
        [data-testid="stMain"] div.stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
        }

        [data-testid="stMain"] div.stButton > button[kind="primary"] {
            background-color: #F59E0B !important;
            color: #111827 !important;
            border: 1px solid #F59E0B !important;
        }

        [data-testid="stMain"] div.stButton > button[kind="primary"] p,
        [data-testid="stMain"] div.stButton > button[kind="primary"] span {
            color: #111827 !important;
        }

        [data-testid="stMain"] div.stButton > button[kind="primary"]:hover {
            background-color: #D97706 !important;
            border-color: #D97706 !important;
        }

        /* ---------- Download Buttons ---------- */
        [data-testid="stDownloadButton"] button {
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )