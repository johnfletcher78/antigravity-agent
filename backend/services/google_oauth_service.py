"""
Unified Google OAuth Service
Handles OAuth authentication for all Google services with consolidated scopes
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleOAuthService:
    """
    Centralized OAuth service for all Google APIs
    Manages a single token with all required scopes
    """
    
    # All scopes needed across all Google services
    SCOPES = [
        # Google Docs
        'https://www.googleapis.com/auth/documents',
        # Google Sheets
        'https://www.googleapis.com/auth/spreadsheets',
        # Google Drive
        'https://www.googleapis.com/auth/drive.file',
        # Gmail
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
        # Google Analytics
        'https://www.googleapis.com/auth/analytics.readonly'
    ]
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize OAuth service
        
        Args:
            credentials_file: Path to OAuth client credentials
            token_file: Path to store/load access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
    
    def get_credentials(self) -> Credentials:
        """
        Get valid credentials, refreshing or re-authenticating as needed
        
        Returns:
            Valid Google OAuth credentials
        """
        # Load existing token if available
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If credentials are invalid or don't exist, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh expired token
                self.creds.refresh(Request())
            else:
                # Run OAuth flow
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please download OAuth credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())
        
        return self.creds
