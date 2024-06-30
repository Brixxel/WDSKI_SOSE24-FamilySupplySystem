import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        self.scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        self.user_sheet = self.client.open_by_key(sheet_id).worksheet("Users")
        self.group_sheet = self.client.open_by_key(sheet_id).worksheet("FamilyGroups")
    
    def add_user(self, username, email, password):
        self.user_sheet.append_row([username, email, password])
    
    def validate_user(self, username, password):
        users = self.user_sheet.get_all_records()
        for user in users:
            if user['username'] == username and user['password'] == password:
                return True
        return False
    
    def add_family_group(self, group_name, group_password, members=[]):
        self.group_sheet.append_row([group_name, group_password, ','.join(members), len(members)])

    def get_family_groups(self):
        return self.group_sheet.get_all_records()

class LoginScreen(Screen):
    def do_login(self, username, password):
        if db.validate_user(username, password):
            app.username = username
            self.manager.current = 'start'
        else:
            self.ids.login_error.text = "Invalid username or password"

class RegisterScreen(Screen):
    def do_register(self, username, email, password, confirm_password):
        if password == confirm_password:
            db.add_user(username, email, password)
            self.manager.current = 'login'
        else:
            self.ids.register_error.text = "Passwords do not match"

class StartScreen(Screen):
    def on_pre_enter(self):
        self.ids.welcome_label.text = f"Willkommen {app.username}"
        groups = db.get_family_groups()
        if any(app.username in group['members'].split(',') for group in groups):
            self.ids.group_options.text = "Sie sind Mitglied einer FamilyGroup"
        else:
            self.ids.group_options.text = "Erstellen oder treten Sie einer FamilyGroup bei"

    def create_group(self, group_name, group_password):
        db.add_family_group(group_name, group_password, [app.username])
        self.manager.current = 'start'

    def join_group(self, group_name, group_password):
        groups = db.get_family_groups()
        for group in groups:
            if group['group_name'] == group_name and group['group_password'] == group_password:
                members = group['members'].split(',')
                if app.username not in members:
                    members.append(app.username)
                    db.group_sheet.update_cell(groups.index(group) + 2, 3, ','.join(members))
                    db.group_sheet.update_cell(groups.index(group) + 2, 4, len(members))
                self.manager.current = 'start'
                return
        self.ids.group_error.text = "Group not found or incorrect password"

class MyScreenManager(ScreenManager):
    pass

class LoginApp(App):
    username = ""

    def build(self):
        return MyScreenManager()

if __name__ == '__main__':
    sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
    credentials_file = 'D:/Uni/Codes/Reposetories/WDSKI_SOSE24-FamilySupplySystem/Techology_TEsting_Space/Multi_User_Interface/Google_Test/credentials.json'
    db = GoogleSheetDB(sheet_id, credentials_file)
    app = LoginApp()
    app.run()
