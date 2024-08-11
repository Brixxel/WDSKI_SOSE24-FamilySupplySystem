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
        self.label_group_name = ctk.CTkLabel(self, text="Gruppennamen eingeben")
        self.label_group_name.pack(pady=(20, 0))

        self.entry_group_name = ctk.CTkEntry(self)
        self.entry_group_name.pack(pady=(5, 20))

        # Label und Eingabefeld für das Passwort
        self.label_password = ctk.CTkLabel(self, text="Passwort")
        self.label_password.pack(pady=(0, 0))

        self.entry_password = ctk.CTkEntry(self, show='*')
        self.entry_password.pack(pady=(5, 20))

        # Button zum Beitreten der Familiengruppe
        self.create_button = ctk.CTkButton(self, text="Familiengruppe beitreten", command=self.join_family_group)
        self.create_button.pack(pady=20)

    def join_family_group(self):
    # Hole die Eingaben
        group_name = self.entry_group_name.get()
        password = self.entry_password.get()
        hashed_password = self.db.hash_password(password)
        username = self.username

        # Überprüfe, ob der Gruppenname existiert
        if not self.db.group_name_exists(group_name):
            messagebox.showerror("Fehler", "Gruppe existiert nicht!")
            return

        # Überprüfe, ob die Passwörter übereinstimmen
        if not self.db.compare_group_password(group_name, hashed_password):
            messagebox.showerror("Fehler", "Falsches Passwort!")
            return

        # Füge die Gruppe zum Account hinzu
        success = self.db.add_group_to_person_and_person_to_group(username, group_name) and self.db.compare_group_password(group_name, hashed_password)
        if success:
            messagebox.showinfo("Erfolg", "Erfolgreich der Familiengruppe beigetreten!")
            self.clear_entries()
        else:
            messagebox.showerror("Fehler", "Du bist bereits in der Gruppe!")

    def clear_entries(self):
        self.entry_group_name.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
