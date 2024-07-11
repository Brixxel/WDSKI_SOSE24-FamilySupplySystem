import gspread
from tkinter import messagebox
from oauth2client.service_account import ServiceAccountCredentials
import uuid

# Google Sheet Setup
sheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'
credentials_file = 'C:/Users/gmgru/OneDrive/Dokumente/GitHub/WDSKI_SOSE24-FamilySupplySystem/Techology_TEsting_Space/Multi_User_Interface/Google_Test/credentials.json'


class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        self.group_sheet = self.client.open_by_key(sheet_id).worksheet("FamilyGroups")
        
    def get_all_group_names(self):
        records = self.group_sheet.get_all_records()
        return [record['GroupName'] for record in records]

    def get_storage_names(self, group_name):
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return list(set(record['Storage_Name'] for record in records if record['Storage_Name']))

    def group_name_exists(self, group_name):
        records = self.group_sheet.get_all_records()
        return any(record['GroupName'] == group_name for record in records)

    def add_family_group(self, group_name, group_password, members=[], num_storages=0):
        self.group_sheet.append_row([group_name, group_password, ','.join(members), num_storages])
        
        # Create a new sheet with headers
        new_sheet = self.client.open_by_key(sheet_id).add_worksheet(title=f"Storage_{group_name}", rows="1000", cols="10")
        headers = ['id', 'Storage_Name', 'location', 'food', 'food_type', 'food_ingredients', 'food_amount', 'amount_type', 'expire_day', 'sonst_info']
        new_sheet.append_row(headers)

    def add_food_item(self, group_name, storage_name, location, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info):
        item_id = str(uuid.uuid4())  # Generate a unique identifier
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)
        sheet.append_row([
            item_id, storage_name, location, food, 
            food_type, food_ingredients, food_amount, 
            amount_type, expire_day, sonst_info
        ])

