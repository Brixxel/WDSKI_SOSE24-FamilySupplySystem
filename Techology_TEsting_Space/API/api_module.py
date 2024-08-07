import requests
import json
from deep_translator import DeeplTranslator

# Lade die API-Schlüssel aus der credentials.json Datei
credentials_file = "/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/Version_2/credentials.json"

with open(credentials_file, "r") as file:
    data = json.load(file)
    deepL_key = data["api_key_deepL"]
    edamam_app_key = data["app_key_edamam"]
    edamam_app_id = data["app_id_edamam"]

def translate_ingredients(ingredients):
    translator = DeeplTranslator(api_key=deepL_key, source="de", target="en")
    return translator.translate_batch(ingredients)

def search_recipes(ingredients, vegetarian=False):
    translated_ingredients = translate_ingredients(ingredients)
    query = ",".join(translated_ingredients)
    url = f"https://api.edamam.com/search?q={query}&from=0&to=10&app_id={edamam_app_id}&app_key={edamam_app_key}"
    
    if vegetarian:
        url += "&health=vegetarian"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('hits', [])
    else:
        raise Exception(f"Fehler bei der Anfrage: {response.status_code}")
