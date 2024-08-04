import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from family_group_creator import FamilyGroupApp
from food_item_creator import FoodItemApp
from google_sheet_db import GoogleSheetDB
from account_manager import AccountManager
from food_display_app import FoodDisplayApp


# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
# credentials_file = "/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/Version_2/credentials.json"
# credentials_file = "credentials.json"

script_dir = os.path.dirname(__file__)
credentials_file = os.path.join(script_dir, "credentials.json")
print(f"Credentials file path: {credentials_file}")


class Menu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.group_name = "dieReglers"  # Placeholder, replace with actual group name after login
        
        #TODO Need a function to log_in and fill the dict:
        #TODO Also: if not logged in, block all functions
        ### Account Details (loged_in)
        self.Account = {
            "logged_in" : True,
            "name" : "DerRegler",
            "groups" : ["dieReglers", "DieWebers"]
        }
        
    
        self.title("Family Supply System")
        self.geometry("800x600")
        self.create_widgets()



    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Menu
        self.menu_frame = ctk.CTkFrame(self, width=200, height=600)
        self.menu_frame.grid(row=0, column=0, rowspan=4, sticky="nswe")
        self.menu_frame.grid_rowconfigure(9, weight=1)
        
        self.menu_label = ctk.CTkLabel(self.menu_frame, text="Menu", font=("Arial", 16))
        self.menu_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.add_item_button = ctk.CTkButton(self.menu_frame, text="Add Food Item", command=self.show_add_food_item)
        self.add_item_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.view_items_button = ctk.CTkButton(self.menu_frame, text="View Food Items", command=self.show_view_food_items)
        self.view_items_button.grid(row=2, column=0, padx=20, pady=10)
        
        #TODO Sollte bald alles in einem unter-Menü ansteuerbar sein:
        
        self.manage_account_button = ctk.CTkButton(self.menu_frame, text="My Account", command= self.open_account_manager)
        self.manage_account_button.grid(row=3, column=0, padx=20, pady=10)
                
        
        ### Visual - Controle
        
        self.appearance_mode_label = ctk.CTkLabel(self.menu_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=10, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.menu_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=11, column=0, padx=20, pady=(10, 10))
        
        self.scaling_label = ctk.CTkLabel(self.menu_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=12, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.menu_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                            command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=13, column=0, padx=20, pady=(10, 20))

        
        # Main Frame
        self.main_frame = ctk.CTkFrame(self, width=600, height=600)
        self.main_frame.grid(row=0, column=1, sticky="nswe")

    def show_add_food_item(self):
        if self.Account["logged_in"]:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            food_item_app = FoodItemApp(self.main_frame, sheet_id, credentials_file, self.Account)
            food_item_app.pack(fill="both", expand=True)
        
        else:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            label = ctk.CTkLabel(self.main_frame, text="Please log in, or register", font=("Arial", 20))
            label.pack(pady=200)

    def show_view_food_items(self):
        if self.Account["logged_in"]:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            food_display_app = FoodDisplayApp(self.main_frame, sheet_id, credentials_file, self.Account)
            food_display_app.pack(fill="both", expand=True)
        else:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            label = ctk.CTkLabel(self.main_frame, text="Please log in, or register", font=("Arial", 20))
            label.pack(pady=200)
            
            
    ### ---- Account - Funktionen: ----
    
    def open_account_manager(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        account_manager = AccountManager(self.main_frame, sheet_id, credentials_file, self.Account)
        account_manager.pack(fill="both", expand=True)

        
    ### ---- Visualisierungs Funktionen ---- ###
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

if __name__ == '__main__':
    app = Menu()
    app.mainloop()
