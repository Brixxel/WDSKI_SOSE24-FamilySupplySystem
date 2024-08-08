import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import hashlib

class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        self.sheet_id = sheet_id  # Speichern des sheet_id als Instanzvariable
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        self.group_sheet = self.client.open_by_key(self.sheet_id).worksheet("FamilyGroups")  # All Groups
        self.user_sheet = self.client.open_by_key(self.sheet_id).worksheet("Users")  # All Users

    def get_all_group_names(self):      
        records = self.group_sheet.get_all_records()
        return [record['GroupName'] for record in records]

    def get_all_storages_from_family(self, fam_name):
        records = self.group_sheet.get_all_records()
        storages = [record['Storage_Names'] for record in records if record['GroupName'] == fam_name]
        if storages:
            # Split the single string into parts and strip any leading/trailing whitespace from each part
            return [item.strip() for item in storages[0].split(',')]
        return []

    def get_storage_names(self, group_name):
        """Returns a list of unique storage names from the specified group."""
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return list(set(record['Storage_Name'] for record in records if record['Storage_Name']))

    def get_food_items_from_storage(self, group_name, storage_name):
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()

        # Filtern der Einträge nach 'Storage_Name' und 'food_type' "Rohkost"
        filtered_items = [
            {'name': record['food'], 'food_type': record['food_type']}
            for record in records
            if record['Storage_Name'] == storage_name and record['food_type'] == 'Rohkost'
        ]

        return filtered_items

    def group_name_exists(self, group_name):
        records = self.group_sheet.get_all_records()
        return any(record['GroupName'] == group_name for record in records)

    def add_family_group(self, group_name, group_password, members=[], storages=[]):
        self.group_sheet.append_row([group_name, group_password, ','.join(members), ','.join(storages)])
        
        # Erstelle ein neues Arbeitsblatt mit Kopfzeilen
        new_sheet = self.client.open_by_key(self.sheet_id).add_worksheet(title=f"Storage_{group_name}", rows="1000", cols="10")
        headers = ['id', 'Storage_Name', 'food', 'food_type', 'food_ingredients', 'food_amount', 'amount_type', 'expire_day', 'sonst_info']
        new_sheet.append_row(headers)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, email, password):
        records = self.user_sheet.get_all_records()
        if any(record['username'] == username or record['email'] == email for record in records):
            return False
        hashed_password = self.hash_password(password)
        self.user_sheet.append_row([username, email, hashed_password])
        return True

    def login_user(self, username, password):
        records = self.user_sheet.get_all_records()
        hashed_password = self.hash_password(password)
        for record in records:
            if record['username'] == username and record['hashed_password'] == hashed_password:
                return True, record
        return False, None

    def get_user_details(self, username):
        records = self.user_sheet.get_all_records()
        for record in records:
            if record['username'] == username:
                return record
        return None

    def add_food_item(self, group_name, storage_name, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info):
        item_id = str(uuid.uuid4())  # Generate a unique identifier
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        sheet.append_row([
            item_id, storage_name, food, 
            food_type, food_ingredients, food_amount, 
            amount_type, expire_day, sonst_info
        ])
    
    def get_storage_items(self, group_name, storage_name):
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return [record for record in records if record['Storage_Name'] == storage_name]

    def get_all_data(self, group_name):
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return [(record['id'], record['Storage_Name'], record['food'], record['food_type'],
                 record['food_ingredients'], record['food_amount'], record['amount_type'],
                 record['expire_day'], record['sonst_info']) for record in records]

    def delete_entry(self, entry_id, group_name):
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        cell = sheet.find(entry_id)
        if cell:
            sheet.delete_rows(cell.row)
