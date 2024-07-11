import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB

class FoodItemApp(ctk.CTkFrame):

    def __init__(self, parent, sheet_id, credentials_file):
        super().__init__(parent)
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.create_widgets()

    def create_widgets(self):

    

        group_names = self.db.get_all_group_names()

        self.group_name_var = tk.StringVar(value=group_names[0] if group_names else "")
        self.dropdown_group_name = ctk.CTkOptionMenu(self, variable=self.group_name_var, values=group_names, command=self.update_storage_names)
        self.dropdown_group_name.pack(pady=(5, 20))

        self.label_storage_name = ctk.CTkLabel(self, text="Storage Name")
        self.label_storage_name.pack(pady=(0, 0))

        self.storage_name_var = tk.StringVar(value="")
        self.dropdown_storage_name = ctk.CTkOptionMenu(self, variable=self.storage_name_var, values=["option1","option2"])
        self.dropdown_storage_name.pack(pady=(5, 20))

        self.label_location = ctk.CTkLabel(self, text="Location")
        self.label_location.pack(pady=(0, 0))

        self.entry_location = ctk.CTkEntry(self)
        self.entry_location.pack(pady=(5, 20))

        self.label_food = ctk.CTkLabel(self, text="Food")
        self.label_food.pack(pady=(0, 0))

        self.entry_food = ctk.CTkEntry(self)
        self.entry_food.pack(pady=(5, 20))

        self.label_food_type = ctk.CTkLabel(self, text="Food Type")
        self.label_food_type.pack(pady=(0, 0))

        self.entry_food_type = ctk.CTkEntry(self)
        self.entry_food_type.pack(pady=(5, 20))

        self.label_food_ingredients = ctk.CTkLabel(self, text="Food Ingredients")
        self.label_food_ingredients.pack(pady=(0, 0))

        self.entry_food_ingredients = ctk.CTkEntry(self)
        self.entry_food_ingredients.pack(pady=(5, 20))

        self.label_food_amount = ctk.CTkLabel(self, text="Food Amount")
        self.label_food_amount.pack(pady=(0, 0))

        self.entry_food_amount = ctk.CTkEntry(self)
        self.entry_food_amount.pack(pady=(5, 20))

        self.label_amount_type = ctk.CTkLabel(self, text="Amount Type")
        self.label_amount_type.pack(pady=(0, 0))

        self.entry_amount_type = ctk.CTkEntry(self)
        self.entry_amount_type.pack(pady=(5, 20))

        self.label_expire_day = ctk.CTkLabel(self, text="Expire Day")
        self.label_expire_day.pack(pady=(0, 0))

        self.entry_expire_day = ctk.CTkEntry(self)
        self.entry_expire_day.pack(pady=(5, 20))

        self.label_sonst_info = ctk.CTkLabel(self, text="Other Info")
        self.label_sonst_info.pack(pady=(0, 0))

        self.entry_sonst_info = ctk.CTkEntry(self)
        self.entry_sonst_info.pack(pady=(5, 20))

        self.add_button = ctk.CTkButton(self, text="Add Food Item", command=self.add_food_item)
        self.add_button.pack(pady=20)

    def update_storage_names(self, group_name):
        storage_names = self.db.get_storage_names(group_name)
        self.dropdown_storage_name.set("")
        self.dropdown_storage_name.configure(values=storage_names)

    def add_food_item(self):
        group_name = self.group_name_var.get()
        storage_name = self.storage_name_var.get()
        location = self.entry_location.get()
        food = self.entry_food.get()
        food_type = self.entry_food_type.get()
        food_ingredients = self.entry_food_ingredients.get()
        food_amount = self.entry_food_amount.get()
        amount_type = self.entry_amount_type.get()
        expire_day = self.entry_expire_day.get()
        sonst_info = self.entry_sonst_info.get()

        if not all([group_name, storage_name, location, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info]):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        food_item = [group_name, storage_name, location, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info]

        if not self.db.group_name_exists(group_name):
            messagebox.showerror("Error", "Group name does not exist!")
            return

        self.db.add_food_item(group_name, storage_name, location, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info)
        messagebox.showinfo("Success", "Food Item added successfully!")
        self.clear_entries()

    def clear_entries(self):
        self.group_name_var.delete(0, tk.END)
        self.storage_name_var.delete(0, tk.END)
        self.entry_location.delete(0, tk.END)
        self.entry_food.delete(0, tk.END)
        self.entry_food_type.delete(0, tk.END)
        self.entry_food_ingredients.delete(0, tk.END)
        self.entry_food_amount.delete(0, tk.END)
        self.entry_amount_type.delete(0, tk.END)
        self.entry_expire_day.delete(0, tk.END)
        self.entry_sonst_info.delete(0, tk.END)
