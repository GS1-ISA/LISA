import os
from typing import Tuple


def verify_connection() -> Tuple[bool, str]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        return False, "Missing SUPABASE_URL or key"
    try:
        from supabase import create_client

        _ = create_client(url, key)
        return True, f"Supabase client for {url}"
    except Exception as e:
        return False, f"Init failed: {e}"
