from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set window background color to light blue
Window.clearcolor = (0.8, 0.9, 1, 1)

# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
credentials_file = "C:/Users/de136581/Documents/_Uni/SoSe_2024/Programierung_2/WDSKI_SOSE24-FamilySupplySystem/Version_1/credentials.json"

class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        self.group_sheet = self.client.open_by_key(sheet_id).worksheet("FamilyGroups")
        
    def group_name_exists(self, group_name):
        records = self.group_sheet.get_all_records()
        for record in records:
            if record['GroupName'] == group_name:
                return True
        return False

    def add_family_group(self, group_name, group_password, members=[], num_storages=0):
        self.group_sheet.append_row([group_name, group_password, ','.join(members), num_storages])
        
        # Create a new sheet with headers
        new_sheet = self.client.open_by_key(sheet_id).add_worksheet(title=f"Storage_{group_name}", rows="1000", cols="10")
        headers = ['id', 'Storage_Name', 'location', 'food', 'food_type', 'food_ingredients', 'food_amount', 'amount_type', 'expire_day', 'sonst_info']
        new_sheet.append_row(headers)

db = GoogleSheetDB(sheet_id, credentials_file)

class FamilyGroupApp(App):
    def build(self):
        self.title = 'Family Group Creator'
        
        self.sm = ScreenManager()
        
        self.create_group_screen = CreateGroupScreen(name='create_group')
        self.success_screen = SuccessScreen(name='success')
        
        self.sm.add_widget(self.create_group_screen)
        self.sm.add_widget(self.success_screen)
        
        return self.sm

class CreateGroupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scrollview = ScrollView(size_hint=(1, None), size=(400, 500))
        gridlayout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        gridlayout.bind(minimum_height=gridlayout.setter('height'))
        
        label_style = {'color': (0, 0, 0, 1), 'font_size': '20sp'}
        input_style = {'multiline': False, 'font_size': '20sp', 'height': 40, 'size_hint_y': None}
        
        gridlayout.add_widget(Label(text="Group Name", **label_style))
        self.group_name_input = TextInput(**input_style)
        gridlayout.add_widget(self.group_name_input)
        
        gridlayout.add_widget(Label(text="Password", **label_style))
        self.password_input = TextInput(password=True, **input_style)
        gridlayout.add_widget(self.password_input)
        
        gridlayout.add_widget(Label(text="Confirm Password", **label_style))
        self.confirm_password_input = TextInput(password=True, **input_style)
        gridlayout.add_widget(self.confirm_password_input)
        
        gridlayout.add_widget(Label(text="Members (comma separated)", **label_style))
        self.members_input = TextInput(**input_style)
        gridlayout.add_widget(self.members_input)
        
        gridlayout.add_widget(Label(text="Number of Storages", **label_style))
        self.num_storages_input = TextInput(**input_style)
        gridlayout.add_widget(self.num_storages_input)
        
        self.message_label = Label(text="", color=(1, 0, 0, 1), font_size='18sp')
        gridlayout.add_widget(self.message_label)
        
        create_button = Button(text="Create Family Group", size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        create_button.bind(on_press=self.create_family_group)
        gridlayout.add_widget(create_button)
        
        scrollview.add_widget(gridlayout)
        root.add_widget(scrollview)
        
        self.add_widget(root)
    
    def create_family_group(self, instance):
        group_name = self.group_name_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        members = self.members_input.text.split(',')
        num_storages = self.num_storages_input.text
        
        if password != confirm_password:
            self.message_label.text = "Passwords do not match!"
            return
        
        if not num_storages.isdigit():
            self.message_label.text = "Number of storages must be a number!"
            return
        
        if db.group_name_exists(group_name):
            self.message_label.text = "Group name already exists!"
            return
        
        num_storages = int(num_storages)
        
        db.add_family_group(group_name, password, members, num_storages)
        self.message_label.text = "Family Group created successfully!"
        self.manager.current = 'success'

class SuccessScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label_style = {'color': (0, 0, 0, 1), 'font_size': '20sp'}
        
        success_label = Label(text="Family Group created successfully!", **label_style)
        root.add_widget(success_label)
        
        back_button = Button(text="Back to Create Group", size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        back_button.bind(on_press=self.back_to_create_group)
        root.add_widget(back_button)
        
        self.add_widget(root)
    
    def back_to_create_group(self, instance):
        self.manager.current = 'create_group'

if __name__ == "__main__":
    FamilyGroupApp().run()
