import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Credentials laden
credentials_file = 'D:/Uni/Codes/Reposetories/WDSKI_SOSE24-FamilySupplySystem/Techology_TEsting_Space/Multi_User_Interface/Google_Test/credentials.json'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)

# Google Sheets Client autorisieren
client = gspread.authorize(creds)

# Beispiel: Daten in ein Google Spreadsheet schreiben
def write_to_sheet():
    spreadsheet_id = '1MtPC-Wh-qdQ-J06ExlSgaSaU4_U2FGuxXsbkIsJxKz0'  # Passe die Spreadsheet-ID an
    sheet = client.open_by_key(spreadsheet_id).sheet1

    data = ["Test", "Data", "123"]  # Beispiel-Daten zum Schreiben
    sheet.append_row(data)
    print("Daten wurden erfolgreich in das Spreadsheet geschrieben.")

if __name__ == "__main__":
    write_to_sheet()
