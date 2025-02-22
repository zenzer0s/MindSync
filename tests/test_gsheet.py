from google.oauth2.service_account import Credentials
import gspread
import os
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import GOOGLE_CREDS_PATH, SPREADSHEET_NAME

def test_connection():
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds_path = GOOGLE_CREDS_PATH
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Credentials file not found at {creds_path}")
        
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Create or open the spreadsheet
        try:
            sheet = client.open(SPREADSHEET_NAME)
        except gspread.SpreadsheetNotFound:
            sheet = client.create(SPREADSHEET_NAME)
            # Share with your email
            sheet.share('praveenzalaki.arc@gmail.com', perm_type='user', role='writer')
        
        worksheet = sheet.sheet1
        
        # Set up headers if sheet is empty
        if worksheet.row_count == 0:
            headers = ['URL', 'Title', 'Description', 'Image', 'Timestamp']
            worksheet.append_row(headers)
        
        print("✅ Connection successful!")
        print(f"📋 Spreadsheet URL: {sheet.url}")
        return worksheet
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    test_connection()