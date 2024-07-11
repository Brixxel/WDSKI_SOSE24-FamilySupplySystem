import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from google_sheet_db import GoogleSheetDB

class FamilyGroupApp(ctk.CTkFrame):
    def __init__(self, parent, sheet_id, credentials_file):
        super().__init__(parent)
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.create_widgets()

    def create_widgets(self):
        self.label_group_name = ctk.CTkLabel(self, text="Group Name")
        self.label_group_name.pack(pady=(20, 0))

        self.entry_group_name = ctk.CTkEntry(self)
        self.entry_group_name.pack(pady=(5, 20))

        self.label_password = ctk.CTkLabel(self, text="Password")
        self.label_password.pack(pady=(0, 0))

        self.entry_password = ctk.CTkEntry(self, show='*')
        self.entry_password.pack(pady=(5, 20))

        self.label_confirm_password = ctk.CTkLabel(self, text="Confirm Password")
        self.label_confirm_password.pack(pady=(0, 0))

        self.entry_confirm_password = ctk.CTkEntry(self, show='*')
        self.entry_confirm_password.pack(pady=(5, 20))

        self.label_members = ctk.CTkLabel(self, text="Members (comma separated)")
        self.label_members.pack(pady=(0, 0))

        self.entry_members = ctk.CTkEntry(self)
        self.entry_members.pack(pady=(5, 20))

        self.label_num_storages = ctk.CTkLabel(self, text="Number of Storages")
        self.label_num_storages.pack(pady=(0, 0))

        self.entry_num_storages = ctk.CTkEntry(self)
        self.entry_num_storages.pack(pady=(5, 20))

        self.create_button = ctk.CTkButton(self, text="Create Family Group", command=self.create_family_group)
        self.create_button.pack(pady=20)

    def create_family_group(self):
        group_name = self.entry_group_name.get()
        password = self.entry_password.get()
        confirm_password = self.entry_confirm_password.get()
        members = self.entry_members.get().split(',')
        num_storages = self.entry_num_storages.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if not num_storages.isdigit():
            messagebox.showerror("Error", "Number of storages must be a number!")
            return

        if self.db.group_name_exists(group_name):
            messagebox.showerror("Error", "Group name already exists!")
            return

        num_storages = int(num_storages)
        self.db.add_family_group(group_name, password, members, num_storages)
        messagebox.showinfo("Success", "Family Group created successfully!")
        self.clear_entries()

    def clear_entries(self):
        self.entry_group_name.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_confirm_password.delete(0, tk.END)
        self.entry_members.delete(0, tk.END)
        self.entry_num_storages.delete(0, tk.END)
