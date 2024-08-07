from deep_translator import DeeplTranslator
import json

key = ""
with open("/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/credentials.json", "r") as file:
    data = json.load(file)
    key = data["api_key_deepL"]



texts = ["apfel", "mehl", "zucker"]

translated = DeeplTranslator(api_key=key, source="de", target="en").translate_batch(texts)

print (translated)