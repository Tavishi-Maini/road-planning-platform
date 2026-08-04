from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    url = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
    key = str(st.secrets["SUPABASE_KEY"]).strip()

    return create_client(url, key)