import requests
from django.http import JsonResponse
from django.conf import settings

GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY

# ------------------------------
# 1️⃣ Distance et durée
# ------------------------------
def get_distance_duration(request):
    origin = request.GET.get('origin')   # ex: "Douala"
    destination = request.GET.get('destination')  # ex: "Bonnamoussadi"

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",  # peut être walking, bicycling, transit
        "language": "fr"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        return JsonResponse({"error": data.get("error_message", "Erreur")}, status=400)

    element = data["rows"][0]["elements"][0]
    result = {
        "distance": element["distance"]["text"],
        "duration": element["duration"]["text"],
        "status": element["status"]
    }
    return JsonResponse(result)


# ------------------------------
# 2️⃣ Autocomplete place
# ------------------------------
def search_quarters_douala(request):
    """
    Recherche des quartiers à Douala via l'API Google Maps Text Search
    """
    query = request.GET.get("query", "quartiers à Douala, Cameroun")  # possibilité de customiser la recherche

    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress"
    }

    data = {
        "textQuery": query
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse(result, json_dumps_params={"ensure_ascii": False, "indent": 2})


def autocomplete_place(request):
    input_text = request.GET.get("input")

    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": f"{input_text} Douala",  # inclut la ville
        "types": "geocode",
        "components": "country:cm",
        "key": GOOGLE_MAPS_API_KEY,
        "language": "fr"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        return JsonResponse({"error": data.get("error_message", "Erreur")}, status=400)

    predictions = [{"description": p["description"], "place_id": p["place_id"]} for p in data["predictions"]]
    return JsonResponse({"predictions": predictions})


# ------------------------------
# 3️⃣ Geocoding
# ------------------------------
def geocode_address(request):
    address = request.GET.get("address")  # ex: "Bonnamoussadi, Douala"

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY,
        "language": "fr"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "OK":
        return JsonResponse({"error": data.get("error_message", "Erreur")}, status=400)

    results = []
    for r in data.get("results", []):
        results.append({
            "formatted_address": r["formatted_address"],
            "location": r["geometry"]["location"]  # {lat, lng}
        })

    return JsonResponse({"results": results})
