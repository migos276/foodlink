from supabase import create_client
import psycopg2
from django.conf import settings

import os
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(supabase_url=SUPABASE_URL,supabase_key= SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Supabase client: {e}")
        supabase = None
def sync_table(table_name, data, row_id=None):
    """
    Synchronise une ligne vers Supabase.
    Si row_id est fourni → update, sinon → insert/upsert.
    """
    if supabase is None:
        return None
    if row_id:
        response = supabase.table(table_name).update(data).eq("id", str(row_id)).execute()
    else:
        response = supabase.table(table_name).upsert(data).execute()
    return response




def delete_from_supabase(table: str, match: dict):
    """
    Supprime une ligne de Supabase
    """
    if supabase is None:
        return None
    response = supabase.table(table).delete().match(match).execute()
    return response
