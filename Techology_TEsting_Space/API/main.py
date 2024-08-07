import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import requests  # Importiere requests für Bildanfragen
import webbrowser  # Importiere webbrowser für das Öffnen von Links
from api_module import search_recipes
from deep_translator import DeeplTranslator
import json

# Lade die API-Schlüssel aus der credentials.json Datei
credentials_file = "/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/Version_2/credentials.json"

with open(credentials_file, "r") as file:
    data = json.load(file)
    deepL_key = data["api_key_deepL"]

class RecipeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Recipe Finder")
        self.geometry("800x600")  # Setze die Fenstergröße auf 800x600

        self.ingredients = ["apfel", "mehl", "zucker", "milch", "ei", "butter", "honig"]
        self.selected_ingredients = {}
        self.images = []

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)  # Mach die zweite Spalte breiter
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self, width=200, height=600)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.label = ctk.CTkLabel(self.input_frame, text="Select ingredients:")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.check_buttons_frame = ctk.CTkFrame(self.input_frame)
        self.check_buttons_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        for ingredient in self.ingredients:
            var = tk.BooleanVar()
            self.selected_ingredients[ingredient] = var
            check_button = ctk.CTkCheckBox(self.check_buttons_frame, text=ingredient, variable=var)
            check_button.pack(anchor='w')

        self.vegetarian_var = tk.BooleanVar()
        self.vegetarian_check = ctk.CTkCheckBox(self.input_frame, text="Vegetarian", variable=self.vegetarian_var)
        self.vegetarian_check.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.search_button = ctk.CTkButton(self.input_frame, text="Search Recipes", command=self.on_search_button_click)
        self.search_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.output_frame = ctk.CTkFrame(self, width=600, height=600)
        self.output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

        self.output_canvas = tk.Canvas(self.output_frame)
        self.output_canvas.pack(expand=True, fill="both", padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_canvas.yview, width=20)  # Setze die Breite der Scrollbar auf 20
        self.scrollbar.pack(side="right", fill="y")

        self.output_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.output_canvas.bind('<Configure>', lambda e: self.output_canvas.configure(scrollregion=self.output_canvas.bbox("all")))

        self.canvas_frame = tk.Frame(self.output_canvas)
        self.output_canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

    def on_search_button_click(self):
        selected = [ingredient for ingredient, var in self.selected_ingredients.items() if var.get()]

        if not selected:
            self.display_message("Please select at least one ingredient.")
            return

        try:
            hits = search_recipes(selected, self.vegetarian_var.get())
            self.display_results(hits)
        except Exception as e:
            self.display_message(str(e))

    def display_message(self, message):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.canvas_frame, text=message)
        label.pack()

    def open_url(self, event):
        url = event.widget.cget("text")
        webbrowser.open_new_tab(url)

    def display_results(self, hits):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.images.clear()

        if hits:
            translator = DeeplTranslator(api_key=deepL_key, source="en", target="de")
            y_position = 0
            for hit in hits:
                recipe = hit['recipe']

                translated_label = translator.translate(recipe['label'])
                label = ctk.CTkLabel(self.canvas_frame, text=f"Rezept: {translated_label}")
                label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
                y_position += 1

                url_label = tk.Label(self.canvas_frame, text=recipe['url'], fg="blue", cursor="hand2")
                url_label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
                url_label.bind("<Button-1>", self.open_url)
                y_position += 1

                translated_ingredients = translator.translate(", ".join(recipe['ingredientLines']))
                ingredients_label = ctk.CTkLabel(self.canvas_frame, text=f"Zutaten: {translated_ingredients}")
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
