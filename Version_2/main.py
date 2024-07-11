import tkinter as tk
import customtkinter as ctk
from family_group_creator import FamilyGroupApp
from food_item_creator import FoodItemApp
from google_sheet_db import GoogleSheetDB

# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
credentials_file = 'C:/Users/gmgru/OneDrive/Dokumente/GitHub/WDSKI_SOSE24-FamilySupplySystem/Techology_TEsting_Space/Multi_User_Interface/Google_Test/credentials.json'


class Menu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.group_name = "dieReglers"  # Placeholder, replace with actual group name after login
        self.title("Family Supply System")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Menu
        self.menu_frame = ctk.CTkFrame(self, width=200, height=600)
        self.menu_frame.grid(row=0, column=0, sticky="nswe")
        
        self.menu_label = ctk.CTkLabel(self.menu_frame, text="Menu", font=("Arial", 16))
        self.menu_label.pack(pady=20)
        
        self.add_item_button = ctk.CTkButton(self.menu_frame, text="Add Food Item", command=self.show_add_food_item)
        self.add_item_button.pack(pady=10)
        
        self.view_items_button = ctk.CTkButton(self.menu_frame, text="View Food Items", command=self.show_view_food_items)
        self.view_items_button.pack(pady=10)
        
        self.add_family_group_button = ctk.CTkButton(self.menu_frame, text="Add Family Group", command=self.show_add_family_group)
        self.add_family_group_button.pack(pady=10)

        self.view_groups_button = ctk.CTkButton(self.menu_frame, text="View Family Groups", command=self.show_family_groups)
        self.view_groups_button.pack(pady=10)
        
        # Main Frame
        self.main_frame = ctk.CTkFrame(self, width=600, height=600)
        self.main_frame.grid(row=0, column=1, sticky="nswe")

    def show_add_food_item(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.main_frame)
        scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initialize the FoodItemApp in the scrollable frame
        food_item_app = FoodItemApp(scrollable_frame, sheet_id, credentials_file)
        food_item_app.pack(fill="both", expand=True)

    def show_view_food_items(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="View Food Items - Coming Soon", font=("Arial", 20))
        label.pack(pady=200)

    def show_add_family_group(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        family_group_app = FamilyGroupApp(self.main_frame, sheet_id, credentials_file)
        family_group_app.pack(fill="both", expand=True)

    def show_family_groups(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="View Family Groups - Coming Soon", font=("Arial", 20))
        label.pack(pady=200)

if __name__ == '__main__':
    app = Menu()
    app.mainloop()
