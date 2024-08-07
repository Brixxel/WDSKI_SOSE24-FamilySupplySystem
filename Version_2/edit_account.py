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
        self.show_compare_password()

    def show_compare_password(self):
        self.clear_screen()

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Aktuelles Password", show='*')
        self.password_entry.pack(pady=5)

        self.login_submit_button = ctk.CTkButton(self, text="Submit", command=self.compare_password)
        self.login_submit_button.pack(pady=20)

    def show_edit_screen(self):
        self.clear_screen()

        self.edit_password_button = ctk.CTkButton(self, text="Passwort ändern", command=self.show_change_password)
        self.edit_password_button.pack(pady=20)

        self.edit_email_button = ctk.CTkButton(self, text="Email ändern", command=self.show_change_email)
        self.edit_email_button.pack(pady=20)

    def compare_password(self):
        username = self.username
        password = self.password_entry.get()
        # success = self.db.compare_userpassword(password, username)
        # if success:
        messagebox.showinfo("Success", "You can now change your password or email!")
        self.show_edit_screen()
        # else:
        #     messagebox.showerror("Error", "Wrong password!")

    def show_change_password(self):
        self.clear_screen()

        self.new_password_entry = ctk.CTkEntry(self, placeholder_text="Neues Password", show='*')
        self.new_password_entry.pack(pady=5)

        self.confirm_password_entry = ctk.CTkEntry(self, placeholder_text="Password bestätigen", show='*')
        self.confirm_password_entry.pack(pady=5)

        self.change_password_button = ctk.CTkButton(self, text="Change Password", command=self.change_password)
        self.change_password_button.pack(pady=20)

    def change_password(self):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        success = self.db.update_user_password(self.username, new_password)
        if success:
            messagebox.showinfo("Success", "Password changed successfully!")
            self.show_edit_screen()
        else:
            messagebox.showerror("Error", "Failed to change password!")

    def show_change_email(self):
        self.clear_screen()

        self.new_email_entry = ctk.CTkEntry(self, placeholder_text="Neue Email")
        self.new_email_entry.pack(pady=5)

        self.confirm_email_entry = ctk.CTkEntry(self, placeholder_text="Email bestätigen")
        self.confirm_email_entry.pack(pady=5)

        self.change_email_button = ctk.CTkButton(self, text="Change Email", command=self.change_email)
        self.change_email_button.pack(pady=20)

    def change_email(self):
        new_email = self.new_email_entry.get()
        confirm_email = self.confirm_email_entry.get()

        if new_email != confirm_email:
            messagebox.showerror("Error", "Emails do not match!")
            return

        if not self.is_valid_email(new_email):
            messagebox.showerror("Error", "Invalid email format!")
            return

        success = self.db.update_user_email(self.username, new_email)
        if success:
            messagebox.showinfo("Success", "Email changed successfully!")
            self.show_edit_screen()
        else:
            messagebox.showerror("Error", "Failed to change email!")

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
