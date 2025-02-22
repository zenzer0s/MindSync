import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class GoogleSheetsDB:
    def __init__(self, credentials_path: str, spreadsheet_name: str):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = Credentials.from_service_account_file(
            credentials_path, scopes=self.scopes
        )
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open(spreadsheet_name).sheet1

        # Ensure headers are set
        headers = ['URL', 'Title', 'Description', 'Image', 'Timestamp']
        if not self.sheet.row_count:
            self.sheet.append_row(headers)
        else:
            existing_headers = self.sheet.row_values(1)
            if existing_headers != headers:
                self.sheet.delete_rows(1)
                self.sheet.insert_row(headers, 1)

    async def add_url(self, metadata: dict) -> bool:
        try:
            row = [
                metadata['url'],
                metadata['title'],
                metadata['description'],
                metadata['image'],
                datetime.now().isoformat()
            ]
            self.sheet.append_row(row)
            print(f"Added row: {row}")
            return True
        except Exception as e:
            print(f"Error adding URL: {e}")
            return False

    async def get_urls(self, limit: int = 10) -> list:
        try:
            rows = self.sheet.get_all_records()
            print(f"Retrieved rows: {rows}")
            return rows[-limit:] if limit > 0 else rows
        except Exception as e:
            print(f"Error getting URLs: {e}")
            return []