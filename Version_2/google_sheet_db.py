import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import hashlib

class GoogleSheetDB:
    def __init__(self, sheet_id, credentials_file):
        # Initialisiere die Verbindung zur Google Sheets-Datenbank
        self.sheet_id = sheet_id
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)
        
        # Verbinde mit den entsprechenden Tabellen
        self.group_sheet = self.client.open_by_key(self.sheet_id).worksheet("FamilyGroups")
        self.user_sheet = self.client.open_by_key(self.sheet_id).worksheet("Users")
        self.recipes_sheet = self.client.open_by_key(self.sheet_id).worksheet("Recipes")

    ### Gruppenverwaltung ###

    def get_all_group_names(self):
        # Gibt eine Liste aller Gruppennamen zurück
        records = self.group_sheet.get_all_records()
        return [record['GroupName'] for record in records]

    def get_all_storages_from_family(self, fam_name):
        # Gibt alle Speichernamen für eine bestimmte Familie zurück
        records = self.group_sheet.get_all_records()
        storages = [record['Storage_Names'] for record in records if record['GroupName'] == fam_name]
        if storages:
            return [item.strip() for item in storages[0].split(',')]
        return []

    def get_storage_names(self, group_name):
        # Gibt eine Liste aller Speichernamen für eine bestimmte Gruppe zurück
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return list(set(record['Storage_Name'] for record in records if record['Storage_Name']))

    def get_food_items_from_storage(self, group_name, storage_name):
        # Gibt eine Liste von Lebensmitteln aus einem bestimmten Speicher zurück
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return [{'name': record['food'], 'food_type': record['food_type']} for record in records if record['Storage_Name'] == storage_name and record['food_type'] == 'Rohkost']

    def group_name_exists(self, group_name):
        # Überprüft, ob ein Gruppenname bereits existiert
        records = self.group_sheet.get_all_records()
        return any(record['GroupName'] == group_name for record in records)

    def add_family_group(self, group_name, group_password, hashed_password, members=[], storages=[]):
        # Fügt eine neue Familie hinzu und erstellt ein neues Arbeitsblatt für die Gruppe
        self.group_sheet.append_row([group_name, group_password, hashed_password, ','.join(members), ','.join(storages)])
        
        # Erstelle ein neues Arbeitsblatt mit Kopfzeilen
        new_sheet = self.client.open_by_key(self.sheet_id).add_worksheet(title=f"Storage_{group_name}", rows="1000", cols="10")
        headers = ['id', 'Storage_Name', 'food', 'food_type', 'food_ingredients', 'food_amount', 'amount_type', 'expire_day', 'sonst_info']
        new_sheet.append_row(headers)

    ### Passwort- und Benutzerverwaltung ###

    def hash_password(self, password):
        # Hasht ein Passwort mit SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, email, password):
        # Registriert einen neuen Benutzer, wenn der Benutzername oder die E-Mail nicht bereits existieren
        records = self.user_sheet.get_all_records()
        if any(record['username'] == username or record['email'] == email for record in records):
            return False
        hashed_password = self.hash_password(password)
        self.user_sheet.append_row([username, email, hashed_password])
        return True

    def login_user(self, username, password):
        # Authentifiziert einen Benutzer
        records = self.user_sheet.get_all_records()
        hashed_password = self.hash_password(password)
        for record in records:
            if record['username'] == username and record['hashed_password'] == hashed_password:
                return True, record
        return False, None

    def get_user_details(self, username):
        # Gibt die Details eines Benutzers zurück
        records = self.user_sheet.get_all_records()
        for record in records:
            if record['username'] == username:
                return record
        return None

    ### Funktionen für Gruppenbeitritt ###

    def compare_group_password(self, group_name, hashed_password):
        # Vergleicht das Passwort einer Gruppe
        records = self.group_sheet.get_all_records()
        for record in records:
            if record['GroupName'] == group_name and record['hashed_password'] == hashed_password:
                return True
        return False

    def add_group_to_person_and_person_to_group(self, username, group_name):
        # Fügt einen Benutzer einer Gruppe hinzu und umgekehrt
        user_updated = False
        group_updated = False
        
        # Benutzer zur Gruppe hinzufügen
        records = self.user_sheet.get_all_records()
        for idx, record in enumerate(records):
            if record['username'] == username:
                current_groups = record.get('Groups', '')
                if current_groups:
                    existing_groups = current_groups.split(',')
                    if group_name not in existing_groups:
                        new_groups = f"{current_groups},{group_name}"
                        col_index = list(record.keys()).index('Groups') + 1
                        self.user_sheet.update_cell(idx + 2, col_index, new_groups)
                        user_updated = True
                else:
                    new_groups = group_name
                    col_index = list(record.keys()).index('Groups') + 1
                    self.user_sheet.update_cell(idx + 2, col_index, new_groups)
                    user_updated = True

        # Gruppe aktualisieren, wenn Benutzer aktualisiert wurde
        if user_updated:
            group_records = self.group_sheet.get_all_records()
            for idx, group_record in enumerate(group_records):
                if group_record['GroupName'] == group_name:
                    current_members = group_record.get('members', '')
                    if current_members:
                        existing_members = current_members.split(',')
                        if username not in existing_members:
                            new_members = f"{current_members},{username}"
                            col_index = list(group_record.keys()).index('members') + 1
                            self.group_sheet.update_cell(idx + 2, col_index, new_members)
                            group_updated = True
                    else:
                        new_members = username
                        col_index = list(group_record.keys()).index('members') + 1
                        self.group_sheet.update_cell(idx + 2, col_index, new_members)
                        group_updated = True

        return user_updated and group_updated

    ### Funktionen zum Bearbeiten von Benutzerinformationen ###

    def compare_userpassword(self, password, username):
        # Vergleicht das Benutzerpasswort
        records = self.user_sheet.get_all_records()
        hashed_password = self.hash_password(password)
        for record in records:
            if record['username'] == username and record['hashed_password'] == hashed_password:
                return True
        return False

    def update_user_password(self, username, new_password):
        # Aktualisiert das Passwort eines Benutzers
        records = self.user_sheet.get_all_records()
        hashed_password = self.hash_password(new_password)
        for index, record in enumerate(records):
            if record['username'] == username:
                self.user_sheet.update_cell(index + 2, 3, new_password)  # Update plain password
                self.user_sheet.update_cell(index + 2, 4, hashed_password)  # Update hashed password
                return True
        return False

    def update_user_email(self, username, new_email):
        # Aktualisiert die E-Mail-Adresse eines Benutzers
        records = self.user_sheet.get_all_records()
        for index, record in enumerate(records):
            if record['username'] == username:
                self.user_sheet.update_cell(index + 2, 2, new_email)  # Update email
                return True
        return False

    ### Funktionen für den Umgang mit den Essensdaten ###

    def add_food_item(self, group_name, storage_name, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info):
        # Fügt einen neuen Lebensmittel-Eintrag hinzu
        item_id = str(uuid.uuid4())
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        sheet.append_row([item_id, storage_name, food, food_type, food_ingredients, food_amount, amount_type, expire_day, sonst_info])

    def update_food_item(self, entry_id, group_name, new_values):
        # Aktualisiert einen bestehenden Lebensmittel-Eintrag
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        cell = sheet.find(entry_id)
        
        if cell:
            row_number = cell.row
            for col_index, value in enumerate(new_values, start=2):
                sheet.update_cell(row_number, col_index, value)

    def get_storage_items(self, group_name, storage_name):
        # Gibt alle Lebensmittel aus einem bestimmten Speicher zurück
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return [record for record in records if record['Storage_Name'] == storage_name]

    def get_all_data(self, group_name):
        # Gibt alle Gruppendaten zurück
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        return [(record['id'], record['Storage_Name'], record['food'], record['food_type'],
                 record['food_ingredients'], record['food_amount'], record['amount_type'],
                 record['expire_day'], record['sonst_info']) for record in records]
    
    def get_filtered_food_items(self, group_name, selected_storages, selected_food_types):
        # Alle Lebensmittel für die Gruppe abrufen
        all_items = self.get_all_data(group_name)

        # Filtern nach Storage
        if selected_storages:
            all_items = [item for item in all_items if item[1] in selected_storages]

        # Filtern nach Food-Type
        if selected_food_types:
            all_items = [item for item in all_items if item[3] in selected_food_types]

        return all_items

    def delete_entry(self, entry_id, group_name):
        # Eintrag löschen
        sheet_name = f"Storage_{group_name}"
        sheet = self.client.open_by_key(self.sheet_id).worksheet(sheet_name)
        cell = sheet.find(entry_id)
        if cell:
            sheet.delete_rows(cell.row)

    def save_recipe(self, recipe_name, ingredients, url, image_url, group_name):
        # Rezept speichern
        recipe_id = str(uuid.uuid4())
        ingredients_str = ', '.join(ingredients) if isinstance(ingredients, list) else ingredients
        self.recipes_sheet.append_row([recipe_id, recipe_name, ingredients_str, url, image_url, group_name])

    def get_saved_recipes(self, group_name):
        # gespeichertes Rezept zurückgeben
        records = self.recipes_sheet.get_all_records()
        return [record for record in records if record['group_name'] == group_name]
