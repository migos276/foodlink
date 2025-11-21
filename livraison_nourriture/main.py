import requests
import json

# 🔹 URL de ton serveur Django
BASE_URL = "http://127.0.0.1:8000"  # ou l'adresse de ton serveur


def test_search_quarters(query=None):
    """
    Teste la vue search_quarters_douala et affiche le résultat
    """
    url = f"{BASE_URL}/maps/search_quarters/"
    params = {}

    if query:
        params["query"] = query

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")


# ------------------------------
# Exemple d'utilisation
# ------------------------------
if __name__ == "__main__":
    print("=== Test par défaut ===")
    test_search_quarters()  # Recherche "quartiers à Douala, Cameroun"

    print("\n=== Test avec query personnalisé ===")
    test_search_quarters("quartiers Bona, Douala")
