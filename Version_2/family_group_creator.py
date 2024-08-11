import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB

class FamilyGroupApp(ctk.CTkFrame):
    def __init__(self, parent, username, sheet_id, credentials_file):
        super().__init__(parent)
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.create_widgets()
        self.username = username

    def create_widgets(self):
        # Label und Eingabefeld für den Gruppennamen
        self.label_group_name = ctk.CTkLabel(self, text="Gruppenname")
        self.label_group_name.pack(pady=(20, 0))

        self.entry_group_name = ctk.CTkEntry(self)
        self.entry_group_name.pack(pady=(5, 20))

        # Label und Eingabefeld für das Passwort
        self.label_password = ctk.CTkLabel(self, text="Passwort")
        self.label_password.pack(pady=(0, 0))

        self.entry_password = ctk.CTkEntry(self, show='*')
        self.entry_password.pack(pady=(5, 20))

        # Label und Eingabefeld zur Bestätigung des Passworts
        self.label_confirm_password = ctk.CTkLabel(self, text="Passwort bestätigen")
        self.label_confirm_password.pack(pady=(0, 0))

        self.entry_confirm_password = ctk.CTkEntry(self, show='*')
        self.entry_confirm_password.pack(pady=(5, 20))

        # Label und Eingabefeld für die Namen der Speicherorte
        self.label_storages = ctk.CTkLabel(self, text="Speicherorte (durch Kommas getrennt)")
        self.label_storages.pack(pady=(0, 0))

        self.entry_storages = ctk.CTkEntry(self)
        self.entry_storages.pack(pady=(5, 20))

        # Button zum Erstellen der Familiengruppe
        self.create_button = ctk.CTkButton(self, text="Familiengruppe erstellen", command=self.create_family_group)
        self.create_button.pack(pady=20)

    def create_family_group(self):
        # Hole die Eingaben
        group_name = self.entry_group_name.get()
        password = self.entry_password.get()
        hashed_password = self.db.hash_password(password)
        confirm_password = self.entry_confirm_password.get()
        members = [self.username]
        storages = [storage.strip() for storage in self.entry_storages.get().split(',')]

        # Überprüfe, ob die Passwörter übereinstimmen
        if str(password) != str(confirm_password):
            messagebox.showerror("Fehler", "Passwörter stimmen nicht überein!")
            return

        # Überprüfe, ob der Gruppenname bereits existiert
        if self.db.group_name_exists(group_name):
            messagebox.showerror("Fehler", "Gruppenname existiert bereits!")
            return

        # Füge die Gruppeninformationen zur Datenbank hinzu
        self.db.add_family_group(group_name, password, hashed_password, members, storages)
        messagebox.showinfo("Erfolg", "Familiengruppe erfolgreich erstellt!")
        self.clear_entries()

    def clear_entries(self):
        self.entry_group_name.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_confirm_password.delete(0, tk.END)
        self.entry_storages.delete(0, tk.END)
