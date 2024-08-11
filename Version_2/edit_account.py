import re
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB

class EditAccountApp(ctk.CTkFrame):

    def __init__(self, parent, username, sheet_id, credentials_file):
        super().__init__(parent)
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self.username = username
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.create_widgets()

    def create_widgets(self):
        # Beginnt mit dem Überprüfen des aktuellen Passworts
        self.show_compare_password()

    def show_compare_password(self):
        # Löscht den Bildschirm, bevor die Eingabeaufforderung angezeigt wird
        self.clear_screen()

        self.label_edit = ctk.CTkLabel(self, text="Geben Sie Ihr Passwort ein")
        self.label_edit.pack(pady=(20, 0))

        # Eingabefeld für das aktuelle Passwort
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Aktuelles Passwort", show='*')
        self.password_entry.pack(pady=5)

        self.login_submit_button = ctk.CTkButton(self, text="Absenden", command=self.compare_password)
        self.login_submit_button.pack(pady=20)

    def show_edit_screen(self):
        # Zeigt Optionen zum Ändern von Passwort oder E-Mail an
        self.clear_screen()

        self.label_edit = ctk.CTkLabel(self, text="Was möchtest du ändern?")
        self.label_edit.pack(pady=(20, 0))

        # Buttons zum Ändern von Passwort oder E-Mail
        self.edit_password_button = ctk.CTkButton(self, text="Passwort ändern", command=self.show_change_password)
        self.edit_password_button.pack(pady=20)

        self.edit_email_button = ctk.CTkButton(self, text="Email ändern", command=self.show_change_email)
        self.edit_email_button.pack(pady=20)

    def compare_password(self):
        # Vergleicht das eingegebene Passwort mit dem gespeicherten Passwort
        username = self.username
        password = self.password_entry.get()
        success = self.db.compare_userpassword(password, username)
        if success:
            # Zeigt den nächsten Bildschirm an, wenn das Passwort korrekt ist
            messagebox.showinfo("Erfolg", "Sie können jetzt Ihr Passwort oder Ihre E-Mail ändern!")
            self.show_edit_screen()
        else:
            # Zeigt eine Fehlermeldung an, wenn das Passwort falsch ist
            messagebox.showerror("Fehler", "Falsches Passwort!")

    def show_change_password(self):
        # Bildschirm für die Passwortänderung anzeigen
        self.clear_screen()

        self.label_edit = ctk.CTkLabel(self, text="Geben Sie Ihr neues Passwort ein")
        self.label_edit.pack(pady=(20, 0))

        # Eingabefelder für das neue Passwort und dessen Bestätigung
        self.new_password_entry = ctk.CTkEntry(self, placeholder_text="Neues Passwort", show='*')
        self.new_password_entry.pack(pady=5)

        self.confirm_password_entry = ctk.CTkEntry(self, placeholder_text="Passwort bestätigen", show='*')
        self.confirm_password_entry.pack(pady=5)

        self.change_password_button = ctk.CTkButton(self, text="Passwort ändern", command=self.change_password)
        self.change_password_button.pack(pady=20)

    def change_password(self):
        # Logik zum Ändern des Passworts
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if new_password != confirm_password:
            # Zeigt eine Fehlermeldung an, wenn die Passwörter nicht übereinstimmen
            messagebox.showerror("Fehler", "Passwörter stimmen nicht überein!")
            return

        success = self.db.update_user_password(self.username, new_password)
        if success:
            messagebox.showinfo("Erfolg", "Passwort erfolgreich geändert!")
            self.show_edit_screen()
        else:
            messagebox.showerror("Fehler", "Passwortänderung fehlgeschlagen!")

    def show_change_email(self):
        # Bildschirm für die E-Mail-Änderung anzeigen
        self.clear_screen()

        self.label_edit = ctk.CTkLabel(self, text="Geben Sie Ihre neue E-Mail-Adresse ein")
        self.label_edit.pack(pady=(20, 0))

        self.new_email_entry = ctk.CTkEntry(self, placeholder_text="Neue E-Mail")
        self.new_email_entry.pack(pady=5)

        self.confirm_email_entry = ctk.CTkEntry(self, placeholder_text="E-Mail bestätigen")
        self.confirm_email_entry.pack(pady=5)

        self.change_email_button = ctk.CTkButton(self, text="E-Mail ändern", command=self.change_email)
        self.change_email_button.pack(pady=20)

    def change_email(self):
        # Logik zum Ändern der E-Mail-Adresse
        new_email = self.new_email_entry.get()
        confirm_email = self.confirm_email_entry.get()

        if new_email != confirm_email:
            # Zeigt eine Fehlermeldung an, wenn die E-Mails nicht übereinstimmen
            messagebox.showerror("Fehler", "E-Mails stimmen nicht überein!")
            return

        if not self.is_valid_email(new_email):
            # Überprüft, ob das neue E-Mail-Format gültig ist
            messagebox.showerror("Fehler", "Ungültiges E-Mail-Format!")
            return

        success = self.db.update_user_email(self.username, new_email)
        if success:
            messagebox.showinfo("Erfolg", "E-Mail erfolgreich geändert!")
            self.show_edit_screen()
        else:
            messagebox.showerror("Fehler", "E-Mail-Änderung fehlgeschlagen!")

    def is_valid_email(self, email):
        # Überprüft, ob die E-Mail-Adresse einem gültigen Muster entspricht
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
