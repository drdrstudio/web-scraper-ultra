"""
Google Sheets Manager for Web Scraper
Handles authentication and data writing to Google Sheets
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google_auth_oauthlib.flow import Flow
from datetime import datetime

class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.sheet = None
        self.default_sheet_id = os.environ.get('DEFAULT_GOOGLE_SHEET_ID', '')
        
    def authenticate_service_account(self, credentials_file='google_sheets_credentials.json'):
        """Authenticate using service account (for automated access)"""
        try:
            if not os.path.exists(credentials_file):
                print(f"Service account credentials file not found: {credentials_file}")
                return False
                
            scope = ['https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
            self.client = gspread.authorize(creds)
            print("✅ Authenticated with Google Sheets using service account")
            return True
        except Exception as e:
            print(f"❌ Service account authentication failed: {e}")
            return False
    
    def authenticate_oauth2(self):
        """Authenticate using OAuth2 (requires user interaction)"""
        try:
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                print("OAuth2 credentials not found in environment variables")
                return False
            
            # OAuth2 configuration
            oauth_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080"]
                }
            }
            
            scope = ['https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive']
            
            # Save temporary config for OAuth flow
            with open('oauth_temp.json', 'w') as f:
                json.dump(oauth_config, f)
            
            flow = Flow.from_client_secrets_file(
                'oauth_temp.json',
                scopes=scope,
                redirect_uri='http://localhost:8080'
            )
            
            # For now, we'll use service account. Full OAuth2 flow requires web callback
            print("OAuth2 authentication requires web callback setup")
            return False
            
        except Exception as e:
            print(f"❌ OAuth2 authentication failed: {e}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists('oauth_temp.json'):
                os.remove('oauth_temp.json')
    
    def open_sheet(self, sheet_id=None):
        """Open a Google Sheet by ID"""
        try:
            if not self.client:
                # Try service account first
                if not self.authenticate_service_account():
                    print("Authentication required")
                    return None
            
            sheet_id = sheet_id or self.default_sheet_id
            if not sheet_id:
                print("No sheet ID provided")
                return None
            
            self.sheet = self.client.open_by_key(sheet_id)
            print(f"✅ Opened Google Sheet: {self.sheet.title}")
            return self.sheet
        except Exception as e:
            print(f"❌ Failed to open sheet: {e}")
            return None
    
    def create_sheet(self, title="Web Scraper Data"):
        """Create a new Google Sheet"""
        try:
            if not self.client:
                if not self.authenticate_service_account():
                    return None
            
            self.sheet = self.client.create(title)
            print(f"✅ Created new Google Sheet: {title}")
            print(f"   Sheet ID: {self.sheet.id}")
            print(f"   URL: {self.sheet.url}")
            
            # Add headers
            worksheet = self.sheet.sheet1
            headers = ["Timestamp", "URL", "Method", "Proxy Used", "Data"]
            worksheet.append_row(headers)
            
            return self.sheet
        except Exception as e:
            print(f"❌ Failed to create sheet: {e}")
            return None
    
    def append_data(self, url, data, method="static", proxy_info="No proxy", sheet_id=None):
        """Append scraped data to Google Sheet"""
        try:
            # Open sheet if not already open
            if not self.sheet or (sheet_id and sheet_id != self.sheet.id):
                if not self.open_sheet(sheet_id):
                    return False
            
            # Get the first worksheet
            worksheet = self.sheet.sheet1
            
            # Prepare row data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Truncate data if too long for a cell
            max_cell_length = 50000  # Google Sheets cell limit
            if len(data) > max_cell_length:
                data = data[:max_cell_length] + "... [truncated]"
            
            row = [timestamp, url, method, proxy_info, data]
            
            # Append to sheet
            worksheet.append_row(row)
            print(f"✅ Data appended to Google Sheet: {self.sheet.title}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to append data: {e}")
            return False
    
    def share_sheet(self, email, role='writer'):
        """Share the sheet with a specific email"""
        try:
            if not self.sheet:
                print("No sheet open")
                return False
            
            self.sheet.share(email, perm_type='user', role=role)
            print(f"✅ Shared sheet with {email} as {role}")
            return True
        except Exception as e:
            print(f"❌ Failed to share sheet: {e}")
            return False

# Global instance
google_sheets_manager = GoogleSheetsManager()