import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB

class FoodItemApp(ctk.CTkFrame):

    def __init__(self, parent, sheet_id, credentials_file, Account):
        super().__init__(parent)
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.Account = Account
        self.create_widgets()

    def create_widgets(self):

        #TODO  Familien Auswahl hier nur die Familien die der Account auch angehört
        group_names = self.Account["groups"]
        
        #TODO hier später FamilienName vom Account auswählen
        storage_names = self.db.get_all_storages_from_family("dieReglers")

        self.group_name_var = tk.StringVar(value=group_names[0] if group_names else "")
        self.dropdown_group_name = ctk.CTkOptionMenu(self, variable=self.group_name_var, values=group_names, command=self.update_storage_names)
        self.dropdown_group_name.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky='ew')

        self.label_storage_name = ctk.CTkLabel(self, text="Storage Name")
        self.label_storage_name.grid(row=1, column=0, padx=20, pady=10, sticky='w')

        self.storage_name_var = tk.StringVar(value=storage_names[0] if storage_names else "")
        self.dropdown_storage_name = ctk.CTkOptionMenu(self, variable=self.storage_name_var, values=storage_names)
        self.dropdown_storage_name.grid(row=1, column=1, padx=20, pady=10, sticky='ew')

        # self.label_location = ctk.CTkLabel(self, text="Location")
        # self.label_location.grid(row=2, column=0, padx=20, pady=10, sticky='w')

        # self.entry_location = ctk.CTkEntry(self)
        # self.entry_location.grid(row=2, column=1, padx=20, pady=10, sticky='ew')
        
        self.label_explanation = ctk.CTkLabel(self, text="Füge hier noch ein paar Informationen über das Essen ein:")
        self.label_explanation.grid(row=2, column=1, padx=20, pady=10, sticky='nsew')

        self.label_food = ctk.CTkLabel(self, text="Food")
        self.label_food.grid(row=3, column=0, padx=20, pady=10, sticky='w')

        self.entry_food = ctk.CTkEntry(self)
        self.entry_food.grid(row=3, column=1, padx=20, pady=10, sticky='ew')

        # Die verschiedenen Arten von Essen:
        Food_Types = ["Rohkost", "Gekochtes", "Gegrilltes", "Gebratenes", "Gebäck", "Eingemachtes", "Zutat", "Fermentiertes",
                        "Süßes", "Snack", "Getränk", "Suppe", "Salat", "Kalte Speise", "Warme Speise"]
        
        self.label_food_type = ctk.CTkLabel(self, text="Essens-Arten")
        self.label_food_type.grid(row=4, column=0, padx=20, pady=10, sticky='w')

        self.type_food_var = tk.StringVar(value=Food_Types[0] if group_names else "")
        self.entry_food_type = ctk.CTkOptionMenu(self, variable=self.type_food_var, values=Food_Types)
        self.entry_food_type.grid(row=4, column=1, padx=20, pady=10, sticky='ew')
        

        self.label_food_ingredients = ctk.CTkLabel(self, text="Inhaltsstoffe")
        self.label_food_ingredients.grid(row=5, column=0, padx=20, pady=10, sticky='w')

        self.entry_food_ingredients = ctk.CTkEntry(self)
        self.entry_food_ingredients.grid(row=5, column=1, padx=20, pady=10, sticky='ew')

        # Festlegen der Menge:
         
        self.label_food_amount = ctk.CTkLabel(self, text="Menge")
        self.label_food_amount.grid(row=6, column=0, padx=20, pady=10, sticky='w')

        self.entry_food_amount = ctk.CTkEntry(self)
        self.entry_food_amount.grid(row=6, column=1, padx=20, pady=10, sticky='ew')
        
        amount_types = ["g", "kg", "l", "ml"]
        self.amount_type_var = tk.StringVar(value= amount_types[0] if group_names else "")

        self.label_amount_type = ctk.CTkLabel(self, text="Einheit")
        self.label_amount_type.grid(row=7, column=0, padx=20, pady=10, sticky='w')

        self.entry_amount_type = ctk.CTkOptionMenu(self, variable=self.amount_type_var, values=amount_types)
        self.entry_amount_type.grid(row=7, column=1, padx=20, pady=10, sticky='ew')

        self.label_expire_day = ctk.CTkLabel(self, text="Ablaufdatum")
        self.label_expire_day.grid(row=8, column=0, padx=20, pady=10, sticky='w')

        self.entry_expire_day = ctk.CTkEntry(self)
        self.entry_expire_day.grid(row=8, column=1, padx=20, pady=10, sticky='ew')

        self.label_sonst_info = ctk.CTkLabel(self, text="weitere Notizen")
        self.label_sonst_info.grid(row=9, column=0, padx=20, pady=10, sticky='w')

        self.entry_sonst_info = ctk.CTkEntry(self)
        self.entry_sonst_info.grid(row=9, column=1, padx=20, pady=10, sticky='ew')

        self.add_button = ctk.CTkButton(self, text="Add Food Item", command=self.add_food_item)
        self.add_button.grid(row=10, column=0, columnspan=2, padx=20, pady=20)

        # Set column weights so that widgets expand horizontally
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Expand to fill the whole screen
        self.pack(fill="both", expand=True)

    def update_storage_names(self, group_name):
        storage_names = self.db.get_all_storages_from_family(group_name)
        self.storage_name_var = tk.StringVar(value=storage_names[0] if storage_names else "")
        self.dropdown_storage_name.set("")
        self.dropdown_storage_name.configure(values=storage_names, variable=self.storage_name_var)


    def add_food_item(self):
        group_name = self.group_name_var.get()
        storage_name = self.storage_name_var.get()
        # location = self.entry_location.get()
        food = self.entry_food.get()
        food_type = self.entry_food_type.get()
        food_ingredients = self.entry_food_ingredients.get()
        food_amount = self.entry_food_amount.get()
        amount_type = self.entry_amount_type.get()
        expire_day = self.entry_expire_day.get()
        sonst_info = self.entry_sonst_info.get()

        if not all([group_name, storage_name, food, food_type, food_ingredients, food_amount, amount_type, expire_day]):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        food_item = [group_name, storage_name, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info]

        if not self.db.group_name_exists(group_name):
            messagebox.showerror("Error", "Group name does not exist!")
            return

        self.db.add_food_item(group_name, storage_name, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info)
        messagebox.showinfo("Success", "Food Item added successfully!")
        self.clear_entries()

    def clear_entries(self):
        self.group_name_var.set("")
        self.storage_name_var.set("")
        #self.entry_location.delete(0, tk.END)
        self.entry_food.delete(0, tk.END)
        self.entry_food_type.delete(0, tk.END)
        self.entry_food_ingredients.delete(0, tk.END)
        self.entry_food_amount.delete(0, tk.END)
        self.entry_amount_type.delete(0, tk.END)
        self.entry_expire_day.delete(0, tk.END)
        self.entry_sonst_info.delete(0, tk.END)
