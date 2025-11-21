from supabase import create_client
from users.models import Restaurant
import os
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def on_change(payload, table_name):
    ids = [row['restaurant_id'] for row in payload['new']]
    if ids:
        if table_name == 'restaurants_a_fermer':
            Restaurant.objects.filter(id__in=ids).update(est_ouvert=False)
            supabase.table('restaurants_a_fermer').delete().in_('restaurant_id', ids).execute()
        elif table_name == 'restaurants_a_ouvert':
            Restaurant.objects.filter(id__in=ids).update(est_ouvert=True)
            supabase.table('restaurants_a_ouvert').delete().in_('restaurant_id', ids).execute()
    print(f"{table_name} traité :", ids)

# S’abonner aux deux tables
supabase.table('restaurants_a_fermer').on('INSERT', lambda payload: on_change(payload, 'restaurants_a_fermer')).subscribe()
supabase.table('restaurants_a_ouvert').on('INSERT', lambda payload: on_change(payload, 'restaurants_a_ouvert')).subscribe()