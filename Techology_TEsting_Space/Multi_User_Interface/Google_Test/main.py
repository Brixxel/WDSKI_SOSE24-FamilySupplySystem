import gspread
from oauth2client.service_account import ServiceAccountCredentials
import bcrypt
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

class GoogleSheetDB:
    def __init__(self, sheet_url, credentials_file):
        self.scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url(sheet_url).sheet1  # Using the URL to open the sheet

    def insert_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.sheet.append_row([username, hashed_password.decode('utf-8')])

    def get_user(self, username):
        users = self.sheet.get_all_records()
        for user in users:
            if user['username'] == username:
                return user
        return None

    def update_user(self, username, new_password):
        users = self.sheet.get_all_records()
        for i, user in enumerate(users):
            if user['username'] == username:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                self.sheet.update_cell(i + 2, 2, hashed_password.decode('utf-8'))  # Assuming password is in the 2nd column
                return True
        return False

    def delete_user(self, username):
        users = self.sheet.get_all_records()
        for i, user in enumerate(users):
            if user['username'] == username:
                self.sheet.delete_row(i + 2)
                return True
        return False

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class LoginApp(App):
    def build(self):
        return ScreenManagement()

    def login(self, username, password):
        db = GoogleSheetDB('https://docs.google.com/spreadsheets/d/1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0/edit?usp=drive_link', 'credentials.json')
        user = db.get_user(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            print("Login successful")
        else:
            print("Invalid username or password")

    def register(self, username, password):
        db = GoogleSheetDB('https://docs.google.com/spreadsheets/d/1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0/edit?usp=drive_link', 'credentials.json')
        if db.get_user(username):
            print("User already exists")
        else:
            db.insert_user(username, password)
            print("User registered successfully")

if __name__ == "__main__":
    LoginApp().run()
