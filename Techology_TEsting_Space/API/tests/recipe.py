import requests
import json
from deep_translator import DeeplTranslator

key = ""
with open("/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/Version_2/credentials.json", "r") as file:
    data = json.load(file)
    key = data["api_key_deepL"]

texts = ["apfel", "mehl", "zucker"]

translated = DeeplTranslator(api_key=key, source="de", target="en").translate_batch(texts)

zutaten = translated

app_key = ""
with open("/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/Version_2/credentials.json", "r") as file:
    data = json.load(file)
    app_key = data["app_key_edamam"]


app_id = ""
with open("/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/Version_2/credentials.json", "r") as file:
    data = json.load(file)
    app_id = data["app_id_edamam"]


query = ",".join(zutaten)
url = f"https://api.edamam.com/search?q={query}&from=0&to=10&app_id={app_id}&app_key={app_key}"


response = requests.get(url)


if response.status_code == 200:
    data = response.json()
    
    hits = data.get('hits', [])
    
    print(f"Anzahl der Treffer: {len(hits)}")
    
    for hit in hits:
        recipe = hit['recipe']
        print(f"Rezept: {recipe['label']}")
        print(f"URL: {recipe['url']}")
        print(f"Zutaten: {', '.join(recipe['ingredientLines'])}")
        print("-" * 40)
else:
    print(f"Fehler bei der Anfrage: {response.status_code}")


