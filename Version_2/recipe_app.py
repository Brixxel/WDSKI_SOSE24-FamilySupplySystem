import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import requests
import webbrowser
from api_module import search_recipes
from deep_translator import DeeplTranslator
import json
from google_sheet_db import GoogleSheetDB  

script_dir = os.path.dirname(__file__)
credentials_file = os.path.join(script_dir, "credentials.json")
with open(credentials_file, "r") as file:
    data = json.load(file)
    deepL_key = data["api_key_deepL"]

class RecipeApp(ctk.CTkFrame):
    def __init__(self, parent, account):
        super().__init__(parent)
        
        self.account = account
        self.sheet_id = data["sheet_id"]
        self.credentials_file = os.path.join(script_dir, "credentials.json")
        self.db = GoogleSheetDB(self.sheet_id, self.credentials_file)
        self.hits = []


        self.group_names = self.account["groups"]

        # Variablen für die gewählte Gruppe und die Zutaten
        self.group_name_var = tk.StringVar(value=self.group_names[0] if self.group_names else "")
        self.storage_name_var = tk.StringVar()
        self.ingredients = []
        self.selected_ingredients = {}
        self.images = []
        self.selected_recipes = {}
        self.deepL_key = data["api_key_deepL"]

        self.create_widgets()
        self.fill_storages() 

    def fill_storages(self, *args): #*args damit die Ereignisse von tkinter keine Probleme verursachen

        selected_group = self.group_name_var.get()
        self.storages = self.db.get_storage_names(selected_group)

        # UI-Elemente für Storage-Auswahl aktualisieren; damit Scrollbar geladen wird
        self.dropdown_storage_name.configure(values=self.storages)
        if self.storages:
            self.storage_name_var.set(self.storages[0])
            self.fill_ingredients()

    def fill_ingredients(self, *args):
        selected_group = self.group_name_var.get()
        selected_storage = self.storage_name_var.get()

        # Nur einige Zutaten werden angezeigt, damit man nicht Essen, was als gekocht gekennzeichnet ist auswählen kann
        desired_food_types = ['Rohkost', 'Zutat']  

        all_ingredients = self.db.get_food_items_from_storage(selected_group, selected_storage, desired_food_types)

        self.ingredients = [item['name'] for item in all_ingredients]

        for widget in self.check_buttons_frame.winfo_children():
            widget.destroy()
        self.selected_ingredients.clear()

        for ingredient in self.ingredients:
            var = tk.BooleanVar()
            self.selected_ingredients[ingredient] = var
            check_button = ctk.CTkCheckBox(self.check_buttons_frame, text=ingredient, variable=var)
            check_button.pack(anchor='w')



    def create_widgets(self):
        #Baut die gesammte GUI-Oberfläche auf für die Rezept-API
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self, width=200, height=600)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self.label = ctk.CTkLabel(self.input_frame, text="Select family group:")
        self.label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.dropdown_group_name = ctk.CTkOptionMenu(self.input_frame, variable=self.group_name_var, values=self.group_names, command=self.fill_storages)
        self.dropdown_group_name.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.label = ctk.CTkLabel(self.input_frame, text="Select storage:")
        self.label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.dropdown_storage_name = ctk.CTkOptionMenu(self.input_frame, variable=self.storage_name_var, command=self.fill_ingredients)
        self.dropdown_storage_name.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.label = ctk.CTkLabel(self.input_frame, text="Select ingredients:")
        self.label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.check_buttons_frame = ctk.CTkFrame(self.input_frame)
        self.check_buttons_frame.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.vegetarian_var = tk.BooleanVar()
        self.vegetarian_check = ctk.CTkCheckBox(self.input_frame, text="Vegetarian", variable=self.vegetarian_var)
        self.vegetarian_check.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.search_button = ctk.CTkButton(self.input_frame, text="Search Recipes", command=self.on_search_button_click)
        self.search_button.grid(row=7, column=0, padx=10, pady=10, sticky="w")

        self.save_button = ctk.CTkButton(self.input_frame, text="Save Selected Recipes", command=self.save_selected_recipes)
        self.save_button.grid(row=8, column=0, padx=10, pady=10, sticky="w")

        # Show Saved Recipes Button jetzt vor dem Delete Button
        self.show_saved_button = ctk.CTkButton(self.input_frame, text="Show Saved Recipes", command=self.show_saved_recipes)
        self.show_saved_button.grid(row=9, column=0, padx=10, pady=10, sticky="w")

        # Delete Selected Recipes Button jetzt nach dem Show Button
        self.delete_button = ctk.CTkButton(self.input_frame, text="Delete Selected Recipes", command=self.delete_selected_recipes)
        self.delete_button.grid(row=10, column=0, padx=10, pady=10, sticky="w")

        self.output_frame = ctk.CTkFrame(self, width=600, height=600)
        self.output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

        self.output_canvas = tk.Canvas(self.output_frame, bg="#2b2b2b", highlightthickness=0)
        self.output_canvas.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.output_frame, orient="vertical", command=self.output_canvas.yview, width=20)
        self.scrollbar.pack(side="right", fill="y")

        self.output_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_frame = tk.Frame(self.output_canvas, bg="#2b2b2b")
        self.output_canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

        self.canvas_frame.bind("<Configure>", self.on_canvas_configure)

        self.shopping_list_button = ctk.CTkButton(self.input_frame, text="Generate Shopping List", command=self.generate_shopping_list)
        self.shopping_list_button.grid(row=11, column=0, padx=10, pady=10, sticky="w")

        style = ttk.Style()
        style.configure("My.TSeparator", background="#2b2b2b")



    def on_canvas_configure(self, event=None):
        self.output_canvas.configure(scrollregion=self.output_canvas.bbox("all")) #Scrollbar wird dem Bereich angepasst

    def on_search_button_click(self):
        #Ruft die Rezepte ab mit den ausgwählten Zutaten
        selected = [ingredient for ingredient, var in self.selected_ingredients.items() if var.get()]

        if not selected:
            self.display_message("Please select at least one ingredient.")
            return

        try:
            self.hits = search_recipes(selected, self.vegetarian_var.get())  
            self.display_results(self.hits)
        except Exception as e:
            self.display_message(str(e))

    def display_message(self, message):
        #zeigt die Ergebnisse an und löscht bestehende Inhalte um neue zu laden
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.canvas_frame, text=message, bg_color="#2b2b2b")
        label.pack()

    def open_url(self, event):
        #damit man die Links von den Rezepten öffnen kann 
        url = event.widget.cget("text")
        webbrowser.open_new_tab(url)

    def display_results(self, hits):
        #Zeigt die Rezepte im Fenster an
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.images.clear()
        self.selected_recipes.clear()

        if hits:
            translator = DeeplTranslator(api_key=deepL_key, source="en", target="de")
            y_position = 0
            for hit in hits:
                recipe = hit['recipe']

                var = tk.BooleanVar()
                self.selected_recipes[recipe['label']] = var
                check_button = ctk.CTkCheckBox(self.canvas_frame, text="", variable=var)
                check_button.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")

                translated_label = translator.translate(recipe['label'])
                label = ctk.CTkLabel(self.canvas_frame, text=f"Rezept: {translated_label}", bg_color="#2b2b2b")
                label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                y_position += 1

                url_label = tk.Label(self.canvas_frame, text=recipe['url'], fg="#00bfff", cursor="hand2", background="#2b2b2b")
                url_label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                url_label.bind("<Button-1>", self.open_url)
                y_position += 1

                translated_ingredients = translator.translate(", ".join(recipe['ingredientLines']))
                ingredients_label = ctk.CTkLabel(self.canvas_frame, text=f"Zutaten: {translated_ingredients}", bg_color="#2b2b2b", wraplength=500)
                ingredients_label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                y_position += 1

                image_url = recipe['image']
                image_response = requests.get(image_url)
                image_data = image_response.content
                image = Image.open(io.BytesIO(image_data))
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)

                self.images.append(photo)

                image_label = tk.Label(self.canvas_frame, image=photo, bg="#2b2b2b")
                image_label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                y_position += 1

                separator = ttk.Separator(self.canvas_frame, orient='horizontal', style="My.TSeparator")
                separator.grid(row=y_position, column=0, columnspan=2, padx=10, pady=10, sticky="we")
                y_position += 1

            self.canvas_frame.after(100, self.on_canvas_configure, None)
        else:
            self.display_message("Keine Rezepte gefunden.")

    def save_selected_recipes(self):
        #Speichert die ausgewählten Rezepte in Sheet Tabelle
        selected_recipes = [label for label, var in self.selected_recipes.items() if var.get()]

        if not selected_recipes:
            self.display_message("Please select at least one recipe to save.")
            return
        
        #try and error besonders fürs Programmieren, aber auch für nachher nicht schlecht
        try:
            translator = DeeplTranslator(api_key=self.deepL_key, source="en", target="de")
            for recipe_name in selected_recipes:
                recipe_data = next((recipe for recipe in self.hits if recipe['recipe']['label'] == recipe_name), None)
                if recipe_data:
                    recipe = recipe_data['recipe']
                    
                    # Übersetze den Rezeptnamen und Zutaten auf deutsch
                    translated_recipe_name = translator.translate(recipe_name)
                    translated_ingredients = translator.translate(", ".join(recipe['ingredientLines'])).split(", ")
                    
                    # Speichern der Rezeptnamen und Zutaten
                    self.db.save_recipe(
                        recipe_name=translated_recipe_name,  
                        ingredients=translated_ingredients,
                        url=recipe['url'],
                        image_url=recipe['image'],
                        group_name=self.group_name_var.get()
                    )
            self.display_message("Recipes saved successfully.")
        except Exception as e:
            self.display_message(f"Error saving recipes: {str(e)}")


    def show_saved_recipes(self):
        #Zeigt die gespeicherten Rezepte an 
        try:
            saved_recipes = self.db.get_saved_recipes(self.group_name_var.get())

            if not saved_recipes:
                self.display_message("Keine gespeicherten Rezepte gefunden.")
                return

            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            self.images.clear()
            self.selected_recipes.clear()

            y_position = 0
            for recipe in saved_recipes:
                # Variable für die Auswahl des Rezepts
                var = tk.BooleanVar()
                self.selected_recipes[recipe['recipe_name']] = var
                check_button = ctk.CTkCheckBox(self.canvas_frame, text="", variable=var)
                check_button.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")

                label = ctk.CTkLabel(self.canvas_frame, text=f"Rezept: {recipe['recipe_name']}", bg_color="#2b2b2b")
                label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                y_position += 1

                url_label = tk.Label(self.canvas_frame, text=recipe['url'], fg="#00bfff", cursor="hand2", background="#2b2b2b")
                url_label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                url_label.bind("<Button-1>", self.open_url)
                y_position += 1

                ingredients_label = ctk.CTkLabel(self.canvas_frame, text=f"Zutaten: {recipe['ingredients']}", bg_color="#2b2b2b", wraplength=500)
                ingredients_label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                y_position += 1

                image_url = recipe['image_url']
                if image_url:
                    try:
                        image_response = requests.get(image_url)
                        image_data = image_response.content
                        image = Image.open(io.BytesIO(image_data))
                        image.thumbnail((100, 100))
                        photo = ImageTk.PhotoImage(image)

                        self.images.append(photo)

                        image_label = tk.Label(self.canvas_frame, image=photo, bg="#2b2b2b")
                        image_label.grid(row=y_position, column=1, padx=10, pady=10, sticky="w")
                        y_position += 1
                    except Exception as e:
                        pass
                        # Da die Bilder von der API nach einiger Zeit nicht mehr geladen werden und dadurch ne Error kommt, wird dann kein Bild mehr angezeigt

                separator = ttk.Separator(self.canvas_frame, orient='horizontal', style="My.TSeparator")
                separator.grid(row=y_position, column=0, columnspan=2, padx=10, pady=10, sticky="we")
                y_position += 1

            self.canvas_frame.after(100, self.on_canvas_configure, None)
        #wieder try and error zum testen
        except Exception as e:
            self.display_message(f"Fehler beim Laden der gespeicherten Rezepte: {str(e)}")


    def delete_selected_recipes(self):
        #löscht die gespeicherten Rezepte aus der Datenbank
        selected_recipes = [label for label, var in self.selected_recipes.items() if var.get()]

        if not selected_recipes:
            self.display_message("Please select at least one recipe to delete.")
            return

        try:
            for recipe_name in selected_recipes:
                self.db.delete_recipe(recipe_name, self.group_name_var.get())
            
            self.display_message("Selected recipes deleted successfully.")
            self.show_saved_recipes() 
        except Exception as e:
            self.display_message(f"Error deleting recipes: {str(e)}")

    def generate_shopping_list(self):
        #erstellt eine Einkaufliste aus den gespeicherten Rezepten
        shopping_list = self.db.generate_shopping_list(self.group_name_var.get())
        self.display_shopping_list(shopping_list)

    def display_shopping_list(self, shopping_list):
        #die generierte Einkausliste wird angezeigt
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        if not shopping_list:
            self.display_message("Alle Zutaten sind verfügbar, keine Einkäufe erforderlich!")
            return

        y_position = 0
        for ingredient in shopping_list:
            text = f"Zutat: {ingredient}"
            
            label = ctk.CTkLabel(self.canvas_frame, text=text, bg_color="#2b2b2b")
            label.grid(row=y_position, column=0, padx=10, pady=10, sticky="w")
            y_position += 1

        self.canvas_frame.after(100, self.on_canvas_configure, None)



