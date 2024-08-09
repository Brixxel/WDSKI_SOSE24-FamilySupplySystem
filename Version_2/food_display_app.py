import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import customtkinter as ctk
from tkinter import ttk
from google_sheet_db import GoogleSheetDB
import tkinter as tk

# from google_sheet_db import GoogleSheetDB

# class FoodDisplayApp(ctk.CTkFrame):
#     def __init__(self, parent, sheet_id, credentials_file, account):
#         super().__init__(parent)
#         self.sheet_id = sheet_id
#         self.credentials_file = credentials_file
#         self.account = account
#         self.db = GoogleSheetDB(sheet_id, credentials_file)
        
#         self.create_widgets()
#         self.load_food_items()

#     def create_widgets(self):
#         self.filter_frame = ctk.CTkFrame(self)
#         self.filter_frame.pack(side="top", fill="x", padx=10, pady=5)

#         self.sort_button = ctk.CTkButton(self.filter_frame, text="Sort by Date", command=self.sort_by_date)
#         self.sort_button.pack(side="left", padx=5, pady=5)

#         self.filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.apply_filter)
#         self.filter_button.pack(side="left", padx=5, pady=5)

#         self.food_list_frame = ctk.CTkFrame(self)
#         self.food_list_frame.pack(side="top", fill="both", expand=True)

#     def load_food_items(self):
#         group_name = self.account["groups"][0]  # Placeholder, select the correct group if necessary
#         storage_names = self.db.get_all_storages_from_family(group_name)
        
#         food_data = []
#         for storage in storage_names:
#             food_items = self.db.get_storage_items(group_name, storage)
#             food_data.extend(food_items)
        
#         self.display_food_items(food_data)

#     def display_food_items(self, food_data):
#         for widget in self.food_list_frame.winfo_children():
#             widget.destroy()

#         for food in food_data:
#             food_label = ctk.CTkLabel(self.food_list_frame, text=str(food))
#             food_label.pack(fill="x", padx=10, pady=5)

#     def sort_by_date(self):
#         group_name = self.account["groups"][0]
#         storage_names = self.db.get_all_storages_from_family(group_name)
        
#         food_data = []
#         for storage in storage_names:
#             food_items = self.db.get_storage_items(group_name, storage)
#             food_data.extend(food_items)

#         # Sort food_data by expire_day
#         food_data.sort(key=lambda x: x['expire_day'])
#         self.display_food_items(food_data)

#     def apply_filter(self):
#         # Implement filtering functionality here, e.g., by food type or other criteria
#         pass



class FoodDisplayApp(ctk.CTkFrame):
    def __init__(self, parent, sheet_id, credentials_file, account):
        super().__init__(parent)
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self.account = account
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        
        self.group_names = self.account["groups"]
        
        self.create_widgets()

    def create_widgets(self):
        
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        # Filter und Options:
        self.group_name_var = tk.StringVar(value=self.group_names[0] if self.group_names else "")
        self.dropdown_group_name = ctk.CTkOptionMenu(self.filter_frame, variable=self.group_name_var, values=self.group_names, command=self.fill_table)
        self.dropdown_group_name.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky='ew')
        


        self.sort_button = ctk.CTkButton(self.filter_frame, text="Sort by Date", command=self.sort_by_date)
        self.sort_button.grid(row =1,  column = 0, padx=5, pady=5)

        self.filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.apply_filter)
        self.filter_button.grid(row =1,  column = 1, padx=5, pady=5)
        
        # Frame für Treeview und Scrollbars erstellen
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview erstellen
        columns = ("Storage_Name", "food", "food_type", "food_ingredients", "food_amount", "amount_type", "expire_day", "sonst_info")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')

        # Spaltenüberschriften festlegen
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
            
        # Scrollbars hinzufügen
        self.vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.hsb.grid(row=1, column=0, sticky='ew')

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.fill_table()

        # Bearbeiten- und Löschen-Buttons
        edit_button = ctk.CTkButton(self, text="Bearbeiten", command=self.edit_item)
        edit_button.pack(side="left", padx=10, pady=10)

        delete_button = ctk.CTkButton(self, text="Löschen", command=self.delete_item)
        delete_button.pack(side="left", padx=10, pady=10)

    def fill_table(self, *args):
        # Optional: `args` verwenden, um den Wert aus dem Dropdown-Menü zu berücksichtigen
        selected_group = self.group_name_var.get()
        data = self.db.get_all_data(selected_group)
        
        # Tabelle leeren
        self.tree.delete(*self.tree.get_children())

        # Daten in die Tabelle einfügen
        for row in data:
            self.tree.insert("", "end", values=row[1:])  # Ignoriere die ID-Spalte beim Einfügen
        
        self.adjust_column_widths()  # Spaltenbreiten anpassen
            
    def adjust_column_widths(self):
        for col in self.tree["columns"]:
            max_width = max(len(str(self.tree.heading(col, "text"))),  # Header text
                            *(len(str(self.tree.item(child, "values")[i])) for i, child in enumerate(self.tree.get_children())))
            self.tree.column(col, width=max_width * 10)  # Adjust width

    def edit_item(self):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            EditItemDialog(self, values, self.update_item)

    def update_item(self, original_values, new_values):
        group_name = self.group_name_var.get()
        entry_id = original_values[0]  # Angenommen, die ID ist in original_values[0]

        self.db.update_food_item(entry_id, group_name, new_values)
        self.fill_table()

    def delete_item(self):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.db.delete_entry(values[0], self.group_name_var.get())  # Angenommen, die ID ist in values[0]
            self.tree.delete(selected_item)
            
    def sort_by_date(self):
        selected_group = self.group_name_var.get()
        data = self.db.get_all_data(selected_group)
        
        # Sortiere die Daten nach dem Ablaufdatum ("expire_day").
        # Wir gehen davon aus, dass das Datum im Format 'YYYY-MM-DD' vorliegt. 
        sorted_data = sorted(data, key=lambda x: x[7])  # Index 7 entspricht 'expire_day' in der Datenstruktur
        
        # Aktualisiere die Tabelle mit den sortierten Daten
        self.tree.delete(*self.tree.get_children())  # Löscht den aktuellen Inhalt der Tabelle
        for row in sorted_data:
            self.tree.insert("", "end", values=row[1:])  # Füge die sortierten Daten ein (ignoriere die ID-Spalte)
    
    def apply_filter(self):
        pass



class EditItemDialog(ctk.CTkToplevel):
    def __init__(self, parent, values, callback):
        super().__init__(parent)
        self.values = values
        self.callback = callback
        self.create_widgets()

    def create_widgets(self):
        self.title("Bearbeiten")

        labels = ["Storage Name", "Food", "Food Type", "Food Ingredients", "Food Amount", "Amount Type", "Expire Day", "Sonst Info"]
        self.entries = []

        for i, (label, value) in enumerate(zip(labels, self.values[1:]), start=1):
            lbl = ctk.CTkLabel(self, text=label)
            lbl.grid(row=i, column=0, padx=20, pady=10, sticky='w')

            entry = ctk.CTkEntry(self)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky='ew')
            entry.insert(0, value)
            self.entries.append(entry)

        save_button = ctk.CTkButton(self, text="Speichern", command=self.save)
        save_button.grid(row=len(labels)+1, column=0, columnspan=2, padx=20, pady=20)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def save(self):
        new_values = [entry.get() for entry in self.entries]
        self.callback(self.values, new_values)
        self.destroy()