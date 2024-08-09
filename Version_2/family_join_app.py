import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB


class FamilyJoinApp(ctk.CTkFrame):
    def __init__(self, parent, username, sheet_id, credentials_file):
        super().__init__(parent)
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.username = username
        self.create_widgets()
        

    def create_widgets(self):
        
        # Label und Eingabefeld für den Gruppennamen
        self.label_group_name = ctk.CTkLabel(self, text="Enter Group Name")
        self.label_group_name.pack(pady=(20, 0))

        self.entry_group_name = ctk.CTkEntry(self)
        self.entry_group_name.pack(pady=(5, 20))

        # Label und Eingabefeld für das Passwort
        self.label_password = ctk.CTkLabel(self, text="Password")
        self.label_password.pack(pady=(0, 0))


        self.entry_password = ctk.CTkEntry(self, show='*')
        self.entry_password.pack(pady=(5, 20))

        # Button zum Erstellen der Familiengruppe
        self.create_button = ctk.CTkButton(self, text="Join Family Group", command=self.join_family_group)
        self.create_button.pack(pady=20)

    def join_family_group(self):
    # Hole die Eingaben
        group_name = self.entry_group_name.get()
        password = self.entry_password.get()
        username = self.username

        # Überprüfe, ob die Passwörter übereinstimmen
        if not self.db.compare_group_password(group_name, password):
            messagebox.showerror("Error", "Not the right Password!")
            return

        # Überprüfe, ob der Gruppenname existiert
        if not self.db.group_name_exists(group_name):
            messagebox.showerror("Error", "Group doesn't exist!")
            return

        # Füge die Gruppe zum Account hinzu
        success = self.db.add_group_to_person(username, group_name, password)
        if success:
            messagebox.showinfo("Success", "Family Group joined successfully!")
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Failed to join family group!")

    def clear_entries(self):
        self.entry_group_name.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
