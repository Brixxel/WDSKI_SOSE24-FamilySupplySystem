import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import uuid

# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
credentials_file = "/Users/tom/Documents/GitHub/WDSKI_SOSE24-FamilySupplySystem/credentials.json"

class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        
    def get_family_group_storages(self, group_name):
        sheet = self.client.open_by_key(sheet_id).worksheet(f"Storage_{group_name}")
        return sheet

    def add_food_item(self, group_name, storage_name, location, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info):
        sheet = self.get_family_group_storages(group_name)
        item_id = str(uuid.uuid4())
        sheet.append_row([item_id, storage_name, location, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info])

class AddFoodItemApp(App):
    def build(self):
        self.db = GoogleSheetDB(sheet_id, credentials_file)
        self.group_name = "dieReglers"  # Placeholder, replace with actual group name after login
        
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.grid = GridLayout(cols=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # Input fields
        self.inputs = {}
        fields = ['Storage_Name', 'location', 'food', 'food_type', 'food_ingredients', 'food_amount', 'amount_type', 'expire_day', 'sonst_info']
        dropdown_fields = ['Storage_Name', 'location']
        
        for field in fields:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
            label = Label(text=field, size_hint_x=0.3)
            if field in dropdown_fields:
                spinner = Spinner(text=f"Select {field}", values=('Option 1', 'Option 2', 'Option 3'), size_hint_x=0.7)
                self.inputs[field] = spinner
                box.add_widget(label)
                box.add_widget(spinner)
            else:
                input_field = TextInput(size_hint_x=0.7, multiline=False, height=40)
                self.inputs[field] = input_field
                box.add_widget(label)
                box.add_widget(input_field)
            self.grid.add_widget(box)
        
        self.scroll_view.add_widget(self.grid)
        self.layout.add_widget(self.scroll_view)

        # Submit button
        submit_btn = Button(text='Add Food Item', size_hint=(1, 0.1), background_color=(0.1, 0.6, 1, 1))
        submit_btn.bind(on_release=self.add_food_item)
        self.layout.add_widget(submit_btn)
        
        return self.layout

    def add_food_item(self, instance):
        values = {field: widget.text for field, widget in self.inputs.items()}
        self.db.add_food_item(self.group_name, values['Storage_Name'], values['location'], values['food'], values['food_type'], values['food_ingredients'], values['food_amount'], values['amount_type'], values['expire_day'], values['sonst_info'])
        print("Food item added successfully")

if __name__ == '__main__':
    AddFoodItemApp().run()
