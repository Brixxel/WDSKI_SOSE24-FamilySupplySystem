import os
from tkinter import *
import customtkinter as ctk
from PIL import Image
from food_item_creator import FoodItemApp
from google_sheet_db import GoogleSheetDB
from account_manager import AccountManager
from food_display_app import FoodDisplayApp
from recipe_app import RecipeApp

ctk.set_default_color_theme("green")

# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
script_dir = os.path.dirname(__file__)
credentials_file = os.path.join(script_dir, "credentials.json")


class Menu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.group_name = "dieReglers"  # Platzhalter, nach dem Login mit tatsächlichem Gruppennamen ersetzen

        self.Account = {
            "logged_in": True,
            "name": "DerRegler",
            "groups": ["dieReglers", "DieWebers"]
        }

        # self.Account = {
        #     "logged_in" :  False,
        #     "name" : "",
        #     "groups" : []
        # }
        

        self.title("KitchenKeeper")
        self.geometry("800x600")
        self.set_icon_based_on_mode()
        self.create_widgets()

    ## linkes Menü erstellen 

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu_frame = ctk.CTkFrame(self, width=200, height=600)
        self.menu_frame.grid(row=0, column=0, rowspan=4, sticky="nswe")
        self.menu_frame.grid_rowconfigure(9, weight=1)

        # Bilder für hellen und dunklen Modus laden
        menu_icon = ctk.CTkImage(light_image=Image.open("Version_2\icons/menu_dark.png"), dark_image=Image.open("Version_2\icons/menu_light.png"))
        
        # Label mit Icon anstelle von Text
        self.menu_label = ctk.CTkLabel(self.menu_frame, image=menu_icon, text="")
        self.menu_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Bildpfade anpassen und Bilder laden
        add_item_img_path = r"Version_2\icons\plus.png"
        view_items_img_path = r"Version_2\icons\apple.png"
        recipe_img_path = r"Version_2\icons\book.png"

        add_item_img = PhotoImage(file=add_item_img_path)
        view_items_img = PhotoImage(file=view_items_img_path)
        recipe_img = PhotoImage(file=recipe_img_path)

        # Button für "Lebensmittel hinzufügen" mit Icon
        self.add_item_button = ctk.CTkButton(self.menu_frame, text="Lebensmittel hinzufügen", image=add_item_img, compound="left", command=self.show_add_food_item)
        self.add_item_button.grid(row=2, column=0, padx=20, pady=10)

        # Button für "Lebensmittel anzeigen" mit Icon
        self.view_items_button = ctk.CTkButton(self.menu_frame, text="Lebensmittel anzeigen", image=view_items_img, compound="left", command=self.show_view_food_items)
        self.view_items_button.grid(row=3, column=0, padx=20, pady=10)

        # Button für "Rezeptfinder" mit Icon
        self.recipe_button = ctk.CTkButton(self.menu_frame, text="Rezeptfinder", image=recipe_img, compound="left", command=self.show_recipe_finder)
        self.recipe_button.grid(row=4, column=0, padx=20, pady=10)


        ### Account-Steuerung
        
        # Bildpfad anpassen und Bild laden
        account_img_path = r"Version_2\icons\account.png"
        account_img = PhotoImage(file=account_img_path)

        # Button erstellen mit Icon
        self.manage_account_button = ctk.CTkButton(self.menu_frame, text="Mein Konto", image=account_img, compound="left", command=self.open_account_manager)
        self.manage_account_button.grid(row=1, column=0, padx=20, pady=10)
                
        
        ### Visual - Kontrolle
        
        self.appearance_mode_label = ctk.CTkLabel(self.menu_frame, text="Darstellungsmodus:", anchor="w")
        self.appearance_mode_label.grid(row=10, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.menu_frame, values=["System", "Light", "Dark"],
                                                             
                                                            command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=11, column=0, padx=20, pady=(10, 10))

        self.scaling_label = ctk.CTkLabel(self.menu_frame, text="UI-Skalierung:", anchor="w")
        self.scaling_label.grid(row=12, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.menu_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                    command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=13, column=0, padx=20, pady=(10, 20))

        self.main_frame = ctk.CTkFrame(self, width=600, height=600)
        self.main_frame.grid(row=0, column=1, sticky="nswe")
        
        # Main-Screen zu Beginn
        # Willkommensnachricht
        
        if self.Account["logged_in"]:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            # Hintergrundfarbe des Frames ändern
            #self.main_frame.configure(fg_color="lightgreen")
            welcome_label = ctk.CTkLabel(self.main_frame, text="WILLKOMMEN!", font=("Arial", 40, "bold"))
            welcome_label.pack(pady=(150, 10))
            name_label = ctk.CTkLabel(self.main_frame, text=self.Account["name"], font=("Arial", 30))
            name_label.pack(pady=10)
        else:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            label = ctk.CTkLabel(self.main_frame, text="Bitte einloggen oder registrieren", font=("Arial", 20))
            label.pack(pady=200)    
         
    # ------------ Display Funktionen (Aufruf der separat gecodeten Darstellungen) ------------- #       

    def show_add_food_item(self):
        if self.Account["logged_in"]:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            food_item_app = FoodItemApp(self.main_frame, sheet_id, credentials_file, self.Account)
            food_item_app.pack(fill="both", expand=True)
        else:
            self.show_login_prompt()

    def show_view_food_items(self):
        if self.Account["logged_in"]:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            food_display_app = FoodDisplayApp(self.main_frame, sheet_id, credentials_file, self.Account)
            food_display_app.pack(fill="both", expand=True)
        else:
            self.show_login_prompt()

    def show_recipe_finder(self):
        if self.Account["logged_in"]:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            recipe_app = RecipeApp(self.main_frame, self.Account)  # Übergebe den Account-Parameter
            recipe_app.pack(fill="both", expand=True)
        else:
            self.show_login_prompt()

            label = ctk.CTkLabel(self.main_frame, text="Bitte einloggen oder registrieren", font=("Arial", 20))
            label.pack(pady=200)

            
            
    ### ---- Account-Manager - Funktionen: ---- ###
    
    def open_account_manager(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        account_manager = AccountManager(self.main_frame, sheet_id, credentials_file, self.Account)
        account_manager.pack(fill="both", expand=True)

    def show_login_prompt(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="Bitte einloggen oder registrieren", font=("Arial", 20))
        label.pack(pady=200)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def set_icon_based_on_mode(self):
        
        current_mode = ctk.get_appearance_mode()

        if current_mode == "Dark":
            icon_path = r"Version_2\icons\kühlschrank_light.ico"
        if current_mode == "System":
            icon_path = r"Version_2\icons\kühlschrank_light.ico"
        elif current_mode == "Light":
            icon_path = r"Version_2\icons\kühlschrank_dark.ico"
        self.iconbitmap(icon_path)

### öffnen des Fensters ###

if __name__ == '__main__':
    app = Menu()
    icon_path = os.path.dirname(__file__)
    icon_path = os.path.join(script_dir, "kühlschrank.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print("Icon file not found!")

    app.mainloop()