import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import customtkinter as ctk
from tkinter import ttk
from google_sheet_db import GoogleSheetDB
import tkinter as tk
import datetime

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

        self.filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.show_filter_window)
        self.filter_button.grid(row =1,  column = 1, columnspan=2, padx=20, pady=20)
        
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
            EditItemDialog(self, values, self.update_item, self.db, self.group_name_var.get())

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

 ### Methoden zum Filtern der Einträge ###

    def apply_filter(self):
        # Ausgewählte Storages und Food Types sammeln
        selected_group = self.group_name_var.get()
        selected_storages = [storage for storage, var in self.selected_storages if var.get()]
        selected_food_types = [food_type for food_type, var in self.selected_food_types if var.get()]

        if not selected_storages:
            messagebox.showerror("Error", "Please select at least one storage.")
            return

        if not selected_food_types:
            messagebox.showerror("Error", "Please select at least one food type.")
            return

        # Filtern der Lebensmittel basierend auf den ausgewählten Kriterien
        filtered_items = self.db.get_filtered_food_items(selected_group, selected_storages, selected_food_types)

        # Update der Treeview-Tabelle mit den gefilterten Items
        self.update_ui_with_filtered_items(filtered_items)

        messagebox.showinfo("Success", "Filter applied successfully!")


    def update_ui_with_filtered_items(self, items):
        # Leere die Tabelle
        self.tree.delete(*self.tree.get_children())

        if not items:
            # Optional: Eine Nachricht in die Tabelle einfügen, wenn keine Daten vorhanden sind
            self.tree.insert("", "end", values=("No items to display",) * len(self.tree["columns"]))
            return

        # Daten in die Tabelle einfügen
        for item in items:
            self.tree.insert("", "end", values=item[1:])  # Ignoriere die ID-Spalte beim Einfügen

        self.adjust_column_widths()  # Optional: Passe die Spaltenbreiten an


    def disable_filter(self):
        # Rücksetzung des Filters, um alle Einträge anzuzeigen
        all_items = self.db.get_all_data(self.group_name_var.get())
        
        # Update der Treeview-Tabelle mit allen Items
        self.update_ui_with_filtered_items(all_items)

        messagebox.showinfo("Success", "Filter disabled!")


    def show_filter_window(self):
        # Erstelle ein neues Fenster
        filter_window = ctk.CTkToplevel(self)
        filter_window.title("Filter Items")
        
        # Erstelle die Liste der Storages
        storage_label = ctk.CTkLabel(filter_window, text="Select Storages:")
        storage_label.pack(padx=10, pady=(10, 0))

        self.selected_storages = []
        storages = self.db.get_all_storages_from_family(self.group_name_var.get())

        def toggle_all_storages():
            select_all = all_var_storages.get()
            for var in self.storage_vars:
                var.set(select_all)

        all_var_storages = tk.BooleanVar(value=True)
        all_check_storages = ctk.CTkCheckBox(filter_window, text="All Storages", variable=all_var_storages, command=toggle_all_storages)
        all_check_storages.pack(anchor='w', padx=10, pady=2)

        self.storage_vars = [tk.BooleanVar(value=True) for _ in storages]

        for i, storage in enumerate(storages):
            var = tk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(filter_window, text=storage, variable=self.storage_vars[i])
            chk.pack(anchor='w', padx=10, pady=2)
            self.selected_storages.append((storage, self.storage_vars[i]))

        # Erstelle die Liste der Food-Types
        food_type_label = ctk.CTkLabel(filter_window, text="Select Food Types:")
        food_type_label.pack(padx=10, pady=(10, 0))

        Food_Types = ["Rohkost", "Gekochtes", "Gegrilltes", "Gebratenes", "Gebäck", "Eingemachtes", 
                    "Zutat", "Fermentiertes", "Süßes", "Snack", "Getränk", "Suppe", "Salat", 
                    "Kalte Speise", "Warme Speise"]

        def toggle_all_food_types():
            select_all = all_var_food_types.get()
            for var in self.food_type_vars:
                var.set(select_all)

        all_var_food_types = tk.BooleanVar(value=True)
        all_check_food_types = ctk.CTkCheckBox(filter_window, text="All Food Types", variable=all_var_food_types, command=toggle_all_food_types)
        all_check_food_types.pack(anchor='w', padx=10, pady=2)

        self.food_type_vars = [tk.BooleanVar(value=True) for _ in Food_Types]

        self.selected_food_types = []
        for i, food_type in enumerate(Food_Types):
            var = tk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(filter_window, text=food_type, variable=self.food_type_vars[i])
            chk.pack(anchor='w', padx=10, pady=2)
            self.selected_food_types.append((food_type, self.food_type_vars[i]))

        # Filter-Button
        apply_filter_button = ctk.CTkButton(filter_window, text="Apply Filter", command=self.apply_filter)
        apply_filter_button.pack(pady=(10, 5))

        # Filter deaktivieren
        disable_filter_button = ctk.CTkButton(filter_window, text="Disable Filter", command=self.disable_filter)
        disable_filter_button.pack(pady=5)


### Zum Bearbeiten der Einträge ###
class EditItemDialog(ctk.CTkToplevel):
    def __init__(self, parent, values, callback, db, group_name):
        super().__init__(parent)
        self.values = values
        self.callback = callback
        self.db = db
        self.group_name = group_name
        self.create_widgets()

    def create_widgets(self):
        self.title("Bearbeiten")

        labels = ["Storage Name", "Food", "Food Type", "Food Ingredients", "Food Amount", "Amount Type", "Expire Day", "Sonst Info"]
        
        # Dropdown für Storage
        storage_label = ctk.CTkLabel(self, text=labels[0])
        storage_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
        
        self.storage_var = tk.StringVar(value=self.values[0])
        storage_dropdown = ctk.CTkOptionMenu(self, variable=self.storage_var, values=self.db.get_all_storages_from_family(self.group_name))
        storage_dropdown.grid(row=0, column=1, padx=20, pady=10, sticky='ew')

        # Entry für Food
        food_label = ctk.CTkLabel(self, text=labels[1])
        food_label.grid(row=1, column=0, padx=20, pady=10, sticky='w')
        
        self.food_entry = ctk.CTkEntry(self)
        self.food_entry.insert(0, self.values[1])
        self.food_entry.grid(row=1, column=1, padx=20, pady=10, sticky='ew')

        # Dropdown für Food Type
        food_type_label = ctk.CTkLabel(self, text=labels[2])
        food_type_label.grid(row=2, column=0, padx=20, pady=10, sticky='w')
        
        self.food_type_var = tk.StringVar(value=self.values[2])
        food_type_dropdown = ctk.CTkOptionMenu(self, variable=self.food_type_var, values=[
            "Rohkost", "Gekochtes", "Gegrilltes", "Gebratenes", "Gebäck", "Eingemachtes", 
            "Zutat", "Fermentiertes", "Süßes", "Snack", "Getränk", "Suppe", "Salat", 
            "Kalte Speise", "Warme Speise"
        ])
        food_type_dropdown.grid(row=2, column=1, padx=20, pady=10, sticky='ew')

        # Entry für Ingredients
        ingredients_label = ctk.CTkLabel(self, text=labels[3])
        ingredients_label.grid(row=3, column=0, padx=20, pady=10, sticky='w')
        
        self.ingredients_entry = ctk.CTkEntry(self)
        self.ingredients_entry.insert(0, self.values[3])
        self.ingredients_entry.grid(row=3, column=1, padx=20, pady=10, sticky='ew')

        # Entry für Amount
        amount_label = ctk.CTkLabel(self, text=labels[4])
        amount_label.grid(row=4, column=0, padx=20, pady=10, sticky='w')
        
        self.amount_entry = ctk.CTkEntry(self)
        self.amount_entry.insert(0, self.values[4])
        self.amount_entry.grid(row=4, column=1, padx=20, pady=10, sticky='ew')

        # Dropdown für Unit
        unit_label = ctk.CTkLabel(self, text=labels[5])
        unit_label.grid(row=5, column=0, padx=20, pady=10, sticky='w')
        
        self.unit_var = tk.StringVar(value=self.values[5])
        unit_dropdown = ctk.CTkOptionMenu(self, variable=self.unit_var, values=["kg", "g", "L", "ml"])
        unit_dropdown.grid(row=5, column=1, padx=20, pady=10, sticky='ew')

        # Entry für Expiry Date
        expiry_label = ctk.CTkLabel(self, text=labels[6])
        expiry_label.grid(row=6, column=0, padx=20, pady=10, sticky='w')
        
        self.expiry_entry = ctk.CTkEntry(self)
        self.expiry_entry.insert(0, self.values[6])
        self.expiry_entry.grid(row=6, column=1, padx=20, pady=10, sticky='ew')

        # Entry für Notes
        notes_label = ctk.CTkLabel(self, text=labels[7])
        notes_label.grid(row=7, column=0, padx=20, pady=10, sticky='w')
        
        self.notes_entry = ctk.CTkEntry(self)
        self.notes_entry.insert(0, self.values[7])
        self.notes_entry.grid(row=7, column=1, padx=20, pady=10, sticky='ew')

        # Save Button
        save_button = ctk.CTkButton(self, text="Speichern", command=self.save)
        save_button.grid(row=8, column=0, columnspan=2, padx=20, pady=20)

        # Layout-Anpassungen
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def save(self):
        # Validierung der Eingaben
        if not self.validate_inputs():
            return
        
        # Neue Werte sammeln
        new_values = [
            self.values[0],  # ID beibehalten
            self.storage_var.get(),
            self.food_entry.get(),
            self.food_type_var.get(),
            self.ingredients_entry.get(),
            self.amount_entry.get(),
            self.unit_var.get(),
            self.expiry_entry.get(),
            self.notes_entry.get()
        ]
        
        # Callback aufrufen, um die Daten zu speichern
        self.callback(self.values, new_values)
        self.destroy()

    def validate_inputs(self):
        # Validierung des Expiry Date Formats
        try:
            datetime.datetime.strptime(self.expiry_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Expiry date must be in the format YYYY-MM-DD.")
            return False

        # Weitere Validierungen können hier hinzugefügt werden
        if not self.food_entry.get():
            messagebox.showerror("Error", "Food name cannot be empty.")
            return False

        # Alle Eingaben sind gültig
        return True
