"""Optional Supabase persistence adapter. Requires matching SQL schema and RLS."""
from .config import get_secret

def client():
    url=get_secret("SUPABASE_URL"); key=get_secret("SUPABASE_KEY")
    if not url or not key: return None
    from supabase import create_client
    return create_client(url,key)

def save_advisory(record: dict):
    sb=client()
    if sb is None: return False
    sb.table("advisories").insert(record).execute()
    return True

def save_feedback(record: dict):
    sb=client()
    if sb is None: return False
    sb.table("feedback").insert(record).execute()
    return True
