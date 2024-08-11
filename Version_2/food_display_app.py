import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from google_sheet_db import GoogleSheetDB
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import datetime

class FoodDisplayApp(ctk.CTkFrame):
    def __init__(self, parent, sheet_id, credentials_file, account):
        super().__init__(parent)
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self.account = account
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        
        self.group_names = self.account["groups"]
        
        self.create_widgets()


# Tabellarische Darstellung der Kühlschrank Inhalte, sowie ergänzende Steuerungs und Manipulations-Buttons
    def create_widgets(self):
        
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        # Filter und Optionen:
        self.group_name_var = tk.StringVar(value=self.group_names[0] if self.group_names else "")
        self.dropdown_group_name = ctk.CTkOptionMenu(self.filter_frame, variable=self.group_name_var, values=self.group_names, command=self.fill_table)
        self.dropdown_group_name.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky='ew')
        
        self.sort_button = ctk.CTkButton(self.filter_frame, text="Nach Datum sortieren", command=self.sort_by_date)
        self.sort_button.grid(row=1, column=0, padx=5, pady=5)

        self.filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.show_filter_window)
        self.filter_button.grid(row=1, column=1, columnspan=2, padx=20, pady=20)
        
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

     ### ---------------------- Steuerungs-Funktionen -------------------------- ###

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
        # Ausgewählte Speicherorte und Lebensmitteltypen sammeln
        selected_group = self.group_name_var.get()
        selected_storages = [storage for storage, var in self.selected_storages if var.get()]
        selected_food_types = [food_type for food_type, var in self.selected_food_types if var.get()]

        if not selected_storages:
            messagebox.showerror("Fehler", "Bitte wähle mindestens einen Speicherort aus.")
            return

        if not selected_food_types:
            messagebox.showerror("Fehler", "Bitte wähle mindestens einen Lebensmitteltyp aus.")
            return

        # Filtern der Lebensmittel basierend auf den ausgewählten Kriterien
        filtered_items = self.db.get_filtered_food_items(selected_group, selected_storages, selected_food_types)

        # Aktualisierung der Treeview-Tabelle mit den gefilterten Items
        self.update_ui_with_filtered_items(filtered_items)

        messagebox.showinfo("Erfolg", "Filter erfolgreich angewendet!")


    def update_ui_with_filtered_items(self, items):
        # Leere die Tabelle
        self.tree.delete(*self.tree.get_children())

        if not items:
            # Optional: Eine Nachricht in die Tabelle einfügen, wenn keine Daten vorhanden sind
            self.tree.insert("", "end", values=("Keine Artikel zum Anzeigen",) * len(self.tree["columns"]))
            return

        # Daten in die Tabelle einfügen
        for item in items:
            self.tree.insert("", "end", values=item[1:])  # Ignoriere die ID-Spalte beim Einfügen

        self.adjust_column_widths()  # Optional: Passe die Spaltenbreiten an


    def disable_filter(self):
        # Rücksetzung des Filters, um alle Einträge anzuzeigen
        all_items = self.db.get_all_data(self.group_name_var.get())
        
        # Aktualisierung der Treeview-Tabelle mit allen Items
        self.update_ui_with_filtered_items(all_items)

        messagebox.showinfo("Erfolg", "Filter deaktiviert!")


    def show_filter_window(self):
        # Erstelle ein neues Fenster
        filter_window = ctk.CTkToplevel(self)
        filter_window.title("Filter Items")
        
        # Erstelle die Liste der Speicherorte
        storage_label = ctk.CTkLabel(filter_window, text="Speicherorte auswählen:")
        storage_label.pack(padx=10, pady=(10, 0))

        self.selected_storages = []
        storages = self.db.get_all_storages_from_family(self.group_name_var.get())

        def toggle_all_storages():
            select_all = all_var_storages.get()
            for var in self.storage_vars:
                var.set(select_all)

        all_var_storages = tk.BooleanVar(value=True)
        all_check_storages = ctk.CTkCheckBox(filter_window, text="Alle Speicherorte", variable=all_var_storages, command=toggle_all_storages)
        all_check_storages.pack(anchor='w', padx=10, pady=2)

        self.storage_vars = [tk.BooleanVar(value=True) for _ in storages]

        for i, storage in enumerate(storages):
            var = tk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(filter_window, text=storage, variable=self.storage_vars[i])
            chk.pack(anchor='w', padx=10, pady=2)
            self.selected_storages.append((storage, self.storage_vars[i]))

        # Erstelle die Liste der Lebensmitteltypen
        food_type_label = ctk.CTkLabel(filter_window, text="Lebensmitteltypen auswählen:")
        food_type_label.pack(padx=10, pady=(10, 0))

        Food_Types = ["Rohkost", "Gekochtes", "Gegrilltes", "Gebratenes", "Gebäck", "Eingemachtes", 
                      "Zutat", "Fermentiertes", "Süßes", "Snack", "Getränk", "Suppe", "Salat", 
                      "Kalte Speise", "Warme Speise"]

        def toggle_all_food_types():
            select_all = all_var_food_types.get()
            for var in self.food_type_vars:
                var.set(select_all)

        all_var_food_types = tk.BooleanVar(value=True)
        all_check_food_types = ctk.CTkCheckBox(filter_window, text="Alle Lebensmitteltypen", variable=all_var_food_types, command=toggle_all_food_types)
        all_check_food_types.pack(anchor='w', padx=10, pady=2)

        self.food_type_vars = [tk.BooleanVar(value=True) for _ in Food_Types]

        self.selected_food_types = []
        for i, food_type in enumerate(Food_Types):
            var = tk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(filter_window, text=food_type, variable=self.food_type_vars[i])
            chk.pack(anchor='w', padx=10, pady=2)
            self.selected_food_types.append((food_type, self.food_type_vars[i]))

        # Filter-Button
        apply_filter_button = ctk.CTkButton(filter_window, text="Filter anwenden", command=self.apply_filter)
        apply_filter_button.pack(pady=(10, 5))

        # Filter deaktivieren
        disable_filter_button = ctk.CTkButton(filter_window, text="Filter deaktivieren", command=self.disable_filter)
        disable_filter_button.pack(pady=5)

### ---- Dialog zum Bearbeiten der Einträge ---- ###

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

        labels = ["Speicherort", "Lebensmittel", "Lebensmitteltyp", "Zutaten", "Menge", "Mengeneinheit", "Ablaufdatum", "Sonstige Informationen"]
        
        # Dropdown für Speicherort
        storage_label = ctk.CTkLabel(self, text=labels[0])
        storage_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
        
        self.storage_var = tk.StringVar(value=self.values[0])
        storage_dropdown = ctk.CTkOptionMenu(self, variable=self.storage_var, values=self.db.get_all_storages_from_family(self.group_name))
        storage_dropdown.grid(row=0, column=1, padx=20, pady=10, sticky='ew')

        # Eingabefeld für Lebensmittel
        food_label = ctk.CTkLabel(self, text=labels[1])
        food_label.grid(row=1, column=0, padx=20, pady=10, sticky='w')
        
        self.food_entry = ctk.CTkEntry(self)
        self.food_entry.insert(0, self.values[1])
        self.food_entry.grid(row=1, column=1, padx=20, pady=10, sticky='ew')

        # Dropdown für Lebensmitteltyp
        food_type_label = ctk.CTkLabel(self, text=labels[2])
        food_type_label.grid(row=2, column=0, padx=20, pady=10, sticky='w')
        
        self.food_type_var = tk.StringVar(value=self.values[2])
        food_type_dropdown = ctk.CTkOptionMenu(self, variable=self.food_type_var, values=[
            "Rohkost", "Gekochtes", "Gegrilltes", "Gebratenes", "Gebäck", "Eingemachtes", 
            "Zutat", "Fermentiertes", "Süßes", "Snack", "Getränk", "Suppe", "Salat", 
            "Kalte Speise", "Warme Speise"
        ])
        food_type_dropdown.grid(row=2, column=1, padx=20, pady=10, sticky='ew')

        # Eingabefeld für Zutaten
        ingredients_label = ctk.CTkLabel(self, text=labels[3])
        ingredients_label.grid(row=3, column=0, padx=20, pady=10, sticky='w')
        
        self.ingredients_entry = ctk.CTkEntry(self)
        self.ingredients_entry.insert(0, self.values[3])
        self.ingredients_entry.grid(row=3, column=1, padx=20, pady=10, sticky='ew')

        # Eingabefeld für Menge
        amount_label = ctk.CTkLabel(self, text=labels[4])
        amount_label.grid(row=4, column=0, padx=20, pady=10, sticky='w')
        
        self.amount_entry = ctk.CTkEntry(self)
        self.amount_entry.insert(0, self.values[4])
        self.amount_entry.grid(row=4, column=1, padx=20, pady=10, sticky='ew')

        # Dropdown für Mengeneinheit
        unit_label = ctk.CTkLabel(self, text=labels[5])
        unit_label.grid(row=5, column=0, padx=20, pady=10, sticky='w')
        
        self.unit_var = tk.StringVar(value=self.values[5])
        unit_dropdown = ctk.CTkOptionMenu(self, variable=self.unit_var, values=["kg", "g", "L", "ml"])
        unit_dropdown.grid(row=5, column=1, padx=20, pady=10, sticky='ew')

        # Eingabefeld für Ablaufdatum
        expiry_label = ctk.CTkLabel(self, text=labels[6])
        expiry_label.grid(row=6, column=0, padx=20, pady=10, sticky='w')
        
        self.expiry_entry = DateEntry(self, date_pattern="yyyy-mm-dd")
        self.expiry_entry.set_date(self.values[6])
        self.expiry_entry.grid(row=6, column=1, padx=20, pady=10, sticky='ew')

        # Eingabefeld für sonstige Informationen
        notes_label = ctk.CTkLabel(self, text=labels[7])
        notes_label.grid(row=7, column=0, padx=20, pady=10, sticky='w')
        
        self.notes_entry = ctk.CTkEntry(self)
        self.notes_entry.insert(0, self.values[7])
        self.notes_entry.grid(row=7, column=1, padx=20, pady=10, sticky='ew')

        # Speichern-Button
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
            # ID beibehalten
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
        # Validierung des Ablaufdatumsformats
        try:
            datetime.datetime.strptime(self.expiry_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Fehler", "Das Ablaufdatum muss im Format JJJJ-MM-TT vorliegen.")
            return False

        # Weitere Validierungen können hier hinzugefügt werden
        if not self.food_entry.get():
            messagebox.showerror("Fehler", "Der Name des Lebensmittels darf nicht leer sein.")
            return False

        # Alle Eingaben sind gültig
        return True

