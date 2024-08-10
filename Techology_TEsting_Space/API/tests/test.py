import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
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

class RecipeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Recipe Finder")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        self.label = ctk.CTkLabel(self.input_frame, text="Enter ingredients (comma-separated):")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.entry = ctk.CTkEntry(self.input_frame, width=400)
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.vegetarian_var = tk.BooleanVar()
        self.vegetarian_check = ctk.CTkCheckBox(self.input_frame, text="Vegetarian", variable=self.vegetarian_var)
        self.vegetarian_check.grid(row=2, column=0, padx=10, pady=10)

        self.search_button = ctk.CTkButton(self.input_frame, text="Search Recipes", command=self.search_recipes)
        self.search_button.grid(row=3, column=0, padx=10, pady=10)

        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nswe")

        self.output_text = tk.Text(self.output_frame, wrap="word")
        self.output_text.pack(expand=True, fill="both", padx=10, pady=10)

    def search_recipes(self):
        ingredients = self.entry.get()
        ingredients_list = [item.strip() for item in ingredients.split(',')]
        
        # Übersetze die Zutaten
        translator = DeeplTranslator(api_key=deepL_key, source="de", target="en")
        translated = translator.translate_batch(ingredients_list)

        # Erstelle die API-Anfrage
        query = ",".join(translated)
        url = f"https://api.edamam.com/search?q={query}&from=0&to=10&app_id={edamam_app_id}&app_key={edamam_app_key}"
        
        if self.vegetarian_var.get():
            url += "&health=vegetarian"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            hits = data.get('hits', [])
            self.display_results(hits)
        else:
            self.output_text.insert("1.0", f"Fehler bei der Anfrage: {response.status_code}\n")

    def display_results(self, hits):
        self.output_text.delete("1.0", tk.END)
        if hits:
            self.output_text.insert(tk.END, f"Anzahl der Treffer: {len(hits)}\n\n")
            for hit in hits:
                recipe = hit['recipe']
                self.output_text.insert(tk.END, f"Rezept: {recipe['label']}\n")
                self.output_text.insert(tk.END, f"URL: {recipe['url']}\n")
                self.output_text.insert(tk.END, f"Zutaten: {', '.join(recipe['ingredientLines'])}\n")
                self.output_text.insert(tk.END, "-" * 40 + "\n")
        else:
            self.output_text.insert(tk.END, "Keine Rezepte gefunden.\n")

if __name__ == "__main__":
    app = RecipeApp()
    app.mainloop()
