"""
Google Sheets Service
Handles creation and management of Google Sheets using the Google Sheets API
"""

import os
from services.google_oauth_service import GoogleOAuthService
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsService:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using unified OAuth"""
        oauth = GoogleOAuthService(self.credentials_file, self.token_file)
        creds = oauth.get_credentials()
        self.service = build('sheets', 'v4', credentials=creds)
    
    def create_spreadsheet(self, title, data=None):
        """
        Create a new Google Spreadsheet
        
        Args:
            title (str): The title of the spreadsheet
            data (list): Optional 2D array of data to populate the sheet
                        Example: [["Name", "Email"], ["John", "john@example.com"]]
        
        Returns:
            dict: Contains spreadsheet_id, title, and url
        """
        try:
            # Create the spreadsheet
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl,properties/title'
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            spreadsheet_url = spreadsheet.get('spreadsheetUrl')
            spreadsheet_title = spreadsheet['properties']['title']
            
            # If data is provided, populate the sheet
            if data and len(data) > 0:
                self.add_data(spreadsheet_id, data)
            
            return {
                'id': spreadsheet_id,
                'url': spreadsheet_url,
                'title': spreadsheet_title
            }
            
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def add_data(self, spreadsheet_id, data, range_name='Sheet1'):
        """
        Add data to a spreadsheet
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet
            data (list): 2D array of data to add
            range_name (str): The A1 notation of the range to update (default: 'Sheet1')
        
        Returns:
            dict: Update response from the API
        """
        try:
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return result
            
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def get_spreadsheet(self, spreadsheet_id):
        """
        Get spreadsheet metadata
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet
        
        Returns:
            dict: Spreadsheet metadata
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            return spreadsheet
            
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def read_data(self, spreadsheet_id, range_name='Sheet1'):
        """
        Read data from a spreadsheet
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet
            range_name (str): The A1 notation of the range to read
        
        Returns:
            list: 2D array of values
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
            
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
