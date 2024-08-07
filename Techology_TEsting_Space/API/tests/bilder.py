import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import requests
import json
from deep_translator import DeeplTranslator
from PIL import Image, ImageTk
import io

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

        self.ingredients = ["apfel", "mehl", "zucker", "milch", "ei", "butter", "honig"]
        self.selected_ingredients = {}
        self.images = []

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        self.label = ctk.CTkLabel(self.input_frame, text="Select ingredients:")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.check_buttons_frame = ctk.CTkFrame(self.input_frame)
        self.check_buttons_frame.grid(row=1, column=0, padx=10, pady=10)

        for ingredient in self.ingredients:
            var = tk.BooleanVar()
            self.selected_ingredients[ingredient] = var
            check_button = ctk.CTkCheckBox(self.check_buttons_frame, text=ingredient, variable=var)
            check_button.pack(anchor='w')

        self.vegetarian_var = tk.BooleanVar()
        self.vegetarian_check = ctk.CTkCheckBox(self.input_frame, text="Vegetarian", variable=self.vegetarian_var)
        self.vegetarian_check.grid(row=2, column=0, padx=10, pady=10)

        self.search_button = ctk.CTkButton(self.input_frame, text="Search Recipes", command=self.search_recipes)
        self.search_button.grid(row=3, column=0, padx=10, pady=10)

        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nswe")

        self.output_canvas = tk.Canvas(self.output_frame)
        self.output_canvas.pack(expand=True, fill="both", padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.output_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.output_canvas.bind('<Configure>', lambda e: self.output_canvas.configure(scrollregion=self.output_canvas.bbox("all")))

        self.canvas_frame = tk.Frame(self.output_canvas)
        self.output_canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

    def search_recipes(self):
        selected = [ingredient for ingredient, var in self.selected_ingredients.items() if var.get()]

        if not selected:
            self.display_message("Please select at least one ingredient.")
            return

        # Übersetze die Zutaten
        translator = DeeplTranslator(api_key=deepL_key, source="de", target="en")
        translated = translator.translate_batch(selected)

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
            self.display_message(f"Fehler bei der Anfrage: {response.status_code}")

    def display_message(self, message):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.canvas_frame, text=message)
        label.pack()

    def display_results(self, hits):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.images.clear()

        if hits:
            y_position = 0
            for hit in hits:
                recipe = hit['recipe']

                label = ctk.CTkLabel(self.canvas_frame, text=f"Rezept: {recipe['label']}")
                label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
                y_position += 1

                url_label = ctk.CTkLabel(self.canvas_frame, text=f"URL: {recipe['url']}")
                url_label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
                y_position += 1

                ingredients_label = ctk.CTkLabel(self.canvas_frame, text=f"Zutaten: {', '.join(recipe['ingredientLines'])}")
                ingredients_label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
                y_position += 1

                # Lade das Bild
                image_url = recipe['image']
                image_response = requests.get(image_url)
                image_data = image_response.content
                image = Image.open(io.BytesIO(image_data))
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)

                self.images.append(photo)  # Halte eine Referenz auf das Bild

                image_label = tk.Label(self.canvas_frame, image=photo)
                image_label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
                y_position += 1

                separator = ttk.Separator(self.canvas_frame, orient='horizontal')
                separator.grid(row=y_position, column=0, padx=10, pady=10, sticky="we")
                y_position += 1

        else:
            self.display_message("Keine Rezepte gefunden.")

if __name__ == "__main__":
    app = RecipeApp()
    app.mainloop()
