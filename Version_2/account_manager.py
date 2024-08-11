import re
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB

from family_group_creator import FamilyGroupApp
from family_join_app import FamilyJoinApp
from edit_account import EditAccountApp

class AccountManager(ctk.CTkFrame):

    def __init__(self, parent, sheet_id, credentials_file, Account):
        super().__init__(parent)
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.Account = Account
        self.create_widgets()  # Initialisiert die Benutzeroberfläche basierend auf dem Login-Status

    def create_widgets(self):
        # Überprüft, ob der Benutzer eingeloggt ist und zeigt die entsprechende Ansicht an
        if not self.Account["logged_in"]:
            self.show_login_or_register()
        else:
            self.show_account_overview()

    def show_login_or_register(self):
        # Zeigt die Optionen zum Anmelden oder Registrieren an, wenn der Benutzer nicht eingeloggt ist
        self.clear_screen()
        self.login_button = ctk.CTkButton(self, text="Anmelden", command=self.show_login_screen)
        self.login_button.pack(pady=20)

        self.register_button = ctk.CTkButton(self, text="Registrieren", command=self.show_register_screen)
        self.register_button.pack(pady=20)

    def show_login_screen(self):
        # Zeigt das Anmeldeformular an
        self.clear_screen()
        self.login_label = ctk.CTkLabel(self, text="Anmeldung")
        self.login_label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Benutzername")
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Passwort", show='*')
        self.password_entry.pack(pady=5)

        self.login_submit_button = ctk.CTkButton(self, text="Absenden", command=self.login)
        self.login_submit_button.pack(pady=20)

    def show_register_screen(self):
        # Zeigt das Registrierungsformular an
        self.clear_screen()
        self.register_label = ctk.CTkLabel(self, text="Registrierung")
        self.register_label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Benutzername")
        self.username_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="E-Mail")
        self.email_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Passwort", show='*')
        self.password_entry.pack(pady=5)

        self.register_submit_button = ctk.CTkButton(self, text="Absenden", command=self.register)
        self.register_submit_button.pack(pady=20)

    def show_account_overview(self):
        # Zeigt eine Übersicht des Kontos mit Optionen für das Erstellen und Beitreten von Familiengruppen sowie das Bearbeiten des Kontos
        self.clear_screen()
        self.account_label = ctk.CTkLabel(self, text=f"Willkommen, {self.Account['name']}")
        self.account_label.pack(pady=10)

        self.logout_button = ctk.CTkButton(self, text="Abmelden", command=self.logout)
        self.logout_button.pack(pady=10)

        self.create_family_button = ctk.CTkButton(self, text="Familie erstellen", command=self.create_family)
        self.create_family_button.pack(pady=10)

        self.join_family_button = ctk.CTkButton(self, text="Familie beitreten", command=self.join_family)
        self.join_family_button.pack(pady=10)

        self.edit_account_button = ctk.CTkButton(self, text="Konto bearbeiten", command=self.edit_account)
        self.edit_account_button.pack(pady=10)

    def login(self):
        # Handhabt die Benutzeranmeldung und speichert die Login-Daten
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, user_record = self.db.login_user(username, password)
        if success:
            self.Account["logged_in"] = True
            self.Account["name"] = user_record["username"]
            self.Account["groups"] = user_record["Groups"].split(',')
            self.create_widgets()  # Aktualisiert die Ansicht nach erfolgreicher Anmeldung
        else:
            messagebox.showerror("Fehler", "Ungültiger Benutzername oder Passwort!")

    def register(self):
        # Handhabt die Benutzerregistrierung und überprüft die Eingabedaten
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not self.is_valid_email(email):
            messagebox.showerror("Fehler", "Ungültiges E-Mail-Format!")
            return

        success = self.db.register_user(username, email, password)
        if success:
            messagebox.showinfo("Erfolg", "Registrierung erfolgreich!")
            self.show_login_screen()  # Leitet den Benutzer nach erfolgreicher Registrierung zur Anmeldung
        else:
            messagebox.showerror("Fehler", "Benutzername oder E-Mail existiert bereits!")

    def is_valid_email(self, email):
        # Überprüft das Format der E-Mail-Adresse
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
    
    def logout(self):
        # Handhabt das Ausloggen des Benutzers
        self.Account["logged_in"] = False
        self.Account["name"] = None
        self.Account["groups"] = []
        self.create_widgets()  # Zeigt die Login/Registrierungsansicht nach dem Ausloggen an
        
    #### Familienfunktionen ####

    def show_family_groups(self):
        # Funktion für das zukünftige Anzeigen von Familiengruppen (noch nicht implementiert)
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="Familiengruppen anzeigen - Demnächst verfügbar", font=("Arial", 20))
        label.pack(pady=200)

    def create_family(self):
        # Leitet zur Ansicht zum Erstellen einer neuen Familie weiter
        self.clear_screen()
        username = self.Account["name"]  
        family_group_app = FamilyGroupApp(self, username, self.sheet_id, self.credentials_file)
        family_group_app.pack(fill="both", expand=True)

    def join_family(self):
        self.clear_screen()
        username = self.Account["name"]
        family_join_app = FamilyJoinApp(self, username, self.sheet_id, self.credentials_file, callback=self.add_group_to_account)
        family_join_app.pack(fill="both", expand=True)

    def add_group_to_account(self, group_name):
        if group_name not in self.Account["groups"]:
            self.Account["groups"].append(group_name)
            messagebox.showinfo("Erfolg", f"Sie sind der Gruppe '{group_name}' erfolgreich beigetreten!")
        else:
            messagebox.showinfo("Info", f"Sie sind bereits Mitglied der Gruppe '{group_name}'.")

    def edit_account(self):
        # Leitet zur Ansicht zum Bearbeiten des Benutzerkontos weiter
        self.clear_screen()
        username = self.Account["name"]
        family_group_app = EditAccountApp(self, username, self.sheet_id, self.credentials_file)
        family_group_app.pack(fill="both", expand=True)

    def clear_screen(self):
        # Entfernt alle Widgets vom aktuellen Bildschirm
        for widget in self.winfo_children():
            widget.destroy()
