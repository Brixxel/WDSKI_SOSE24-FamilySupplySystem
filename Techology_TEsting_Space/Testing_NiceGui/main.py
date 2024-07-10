from nicegui import ui, app
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
credentials_file = "C:/Users/de136581/Documents/_Uni/SoSe_2024/Programierung_2/WDSKI_SOSE24-FamilySupplySystem/Version_1/credentials.json"

class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
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

db = GoogleSheetDB(sheet_id, credentials_file)

# App State
app_state = {
    'username': 'DerRegler',
}

# UI Components
def login_page():
    with ui.page():
        ui.label('Login').style('font-size: 32px')
        username = ui.input('Username')
        password = ui.input('Password', password=True)
        login_error = ui.label().style('color: red')

        def do_login():
            if db.validate_user(username.value, password.value):
                app_state['username'] = username.value
                ui.open('/start')
            else:
                login_error.set_text('Invalid username or password')

        ui.button('Login', on_click=do_login)
        ui.button('Go to Register', on_click=lambda: ui.open('/register'))

def register_page():
    with ui.page():
        ui.label('Register').style('font-size: 32px')
        new_username = ui.input('Username')
        email = ui.input('Email')
        new_password = ui.input('Password', password=True)
        confirm_password = ui.input('Confirm Password', password=True)
        register_error = ui.label().style('color: red')

        def do_register():
            if new_password.value == confirm_password.value:
                db.add_user(new_username.value, email.value, new_password.value)
                ui.open('/login')
            else:
                register_error.set_text('Passwords do not match')

        ui.button('Register', on_click=do_register)
        ui.button('Back to Login', on_click=lambda: ui.open('/login'))

def start_page():
    with ui.page():
        ui.label(f'Willkommen {app_state["username"]}').style('font-size: 32px')
        group_options = ui.label()

        def update_group_options():
            groups = db.get_family_groups()
            if any(app_state['username'] in group['members'].split(',') for group in groups):
                group_options.set_text("Sie sind Mitglied einer FamilyGroup")
            else:
                group_options.set_text("Erstellen oder treten Sie einer FamilyGroup bei")

        ui.button('Create Family Group', on_click=lambda: ui.open('/create_group'))
        ui.button('Join Family Group', on_click=lambda: ui.open('/join_group'))
        ui.on_page_update(update_group_options)

def create_group_page():
    with ui.page():
        ui.label('Create Family Group').style('font-size: 32px')
        group_name = ui.input('Group Name')
        group_password = ui.input('Group Password', password=True)
        create_group_error = ui.label().style('color: red')

        def create_group():
            if group_name.value and group_password.value:
                db.add_family_group(group_name.value, group_password.value, [app_state['username']])
                ui.open('/start')
            else:
                create_group_error.set_text('Please enter a group name and password')

        ui.button('Create', on_click=create_group)
        ui.button('Back to Start', on_click=lambda: ui.open('/start'))

def join_group_page():
    with ui.page():
        ui.label('Join Family Group').style('font-size: 32px')
        group_name = ui.input('Group Name')
        group_password = ui.input('Group Password', password=True)
        join_group_error = ui.label().style('color: red')

        def join_group():
            groups = db.get_family_groups()
            for group in groups:
                if group['group_name'] == group_name.value and group['group_password'] == group_password.value:
                    members = group['members'].split(',')
                    if app_state['username'] not in members:
                        members.append(app_state['username'])
                        db.group_sheet.update_cell(groups.index(group) + 2, 3, ','.join(members))
                        db.group_sheet.update_cell(groups.index(group) + 2, 4, len(members))
                    ui.open('/start')
                    return
            join_group_error.set_text('Group not found or incorrect password')

        ui.button('Join', on_click=join_group)
        ui.button('Back to Start', on_click=lambda: ui.open('/start'))
        
app.add_route('/', login_page)
app.add_route('/login', login_page)
app.add_route('/register', register_page)
app.add_route('/start', start_page)
app.add_route('/create_group', create_group_page)
app.add_route('/join_group', join_group_page)

# Run the App
ui.run(port=8080, host='0.0.0.0')
