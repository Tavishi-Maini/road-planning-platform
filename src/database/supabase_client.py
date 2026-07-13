from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    url = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
    key = str(st.secrets["SUPABASE_KEY"]).strip()

    if "/rest/v1" in url:
        raise RuntimeError(
            "SUPABASE_URL must be the project URL only, without /rest/v1."
        )

    if "supabase.com/dashboard" in url:
        raise RuntimeError(
            "SUPABASE_URL is a dashboard URL. Use "
            "https://<project-ref>.supabase.co instead."
        )

    if not url.startswith("https://") or not url.endswith(".supabase.co"):
        raise RuntimeError(
            f"Invalid SUPABASE_URL format: {url!r}. "
            "Expected https://<project-ref>.supabase.co"
        )

    return create_client(url, key)