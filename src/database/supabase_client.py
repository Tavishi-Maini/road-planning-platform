from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    try:
        url = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
        key = str(st.secrets["SUPABASE_KEY"]).strip()
    except KeyError as exc:
        raise RuntimeError(
            "Supabase credentials are missing. Add SUPABASE_URL and "
            "SUPABASE_KEY in Streamlit Cloud → App Settings → Secrets."
        ) from exc

    return create_client(url, key)