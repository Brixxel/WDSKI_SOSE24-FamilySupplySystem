import requests
import json

# Ihre Zutatenliste
zutaten = ['apple', 'flour', 'sugar']

# Ihre Edamam API-Zugangsdaten
app_key = ""
with open("/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/credentials.json", "r") as file:
    data = json.load(file)
    app_key = data["app_key_edamam"]


app_id = ""
with open("/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/credentials.json", "r") as file:
    data = json.load(file)
    app_id = data["app_id_edamam"]


# Erstellen der Suchanfrage
query = ",".join(zutaten)
url = f"https://api.edamam.com/search?q={query}&from=0&to=10&app_id={app_id}&app_key={app_key}"

# Debug-Ausgabe: URL anzeigen
# print(f"URL: {url}")

# Senden der Anfrage an die Edamam API
response = requests.get(url)

# Debug-Ausgabe: Statuscode anzeigen
# print(f"Statuscode: {response.status_code}")

# Überprüfen, ob die Anfrage erfolgreich war
if response.status_code == 200:
    data = response.json()
    
    # Debug-Ausgabe: Rohdaten anzeigen
    # print("Rohdaten:")
    # print(data)

    # Verarbeiten der Rezeptdaten
    hits = data.get('hits', [])
    
    # Debug-Ausgabe: Anzahl der Treffer anzeigen
    print(f"Anzahl der Treffer: {len(hits)}")
    
    for hit in hits:
        recipe = hit['recipe']
        print(f"Rezept: {recipe['label']}")
        print(f"URL: {recipe['url']}")
        print(f"Zutaten: {', '.join(recipe['ingredientLines'])}")
        print("-" * 40)
else:
    print(f"Fehler bei der Anfrage: {response.status_code}")
    # print(response.text)  # Debug-Ausgabe: Fehlertext anzeigen

