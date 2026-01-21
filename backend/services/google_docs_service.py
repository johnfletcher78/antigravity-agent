import os
import json
from services.google_oauth_service import GoogleOAuthService
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleDocsService:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.docs_service = None
        self.drive_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs using unified OAuth"""
        oauth = GoogleOAuthService(self.credentials_file, self.token_file)
        creds = oauth.get_credentials()
        
        # Build the services
        self.docs_service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
    
    def create_document(self, title: str, content: str = "") -> dict:
        """
        Create a new Google Doc
        
        Args:
            title: Title of the document
            content: Initial content (plain text)
        
        Returns:
            dict with 'id' and 'url' of the created document
        """
        try:
            # Create the document
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()
            
            doc_id = document.get('documentId')
            
            # Add content if provided
            if content:
                self.append_text(doc_id, content)
            
            # Get shareable link
            file = self.drive_service.files().get(
                fileId=doc_id,
                fields='webViewLink'
            ).execute()
            
            return {
                'id': doc_id,
                'url': file.get('webViewLink'),
                'title': title
            }
        
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def append_text(self, document_id: str, text: str):
        """
        Append text to the end of a document
        
        Args:
            document_id: ID of the document
            text: Text to append
        """
        try:
            requests = [{
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': text
                }
            }]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
        
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def read_document(self, document_id: str) -> str:
        """
        Read the content of a document
        
        Args:
            document_id: ID of the document
        
        Returns:
            Plain text content of the document
        """
        try:
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            
            content = []
            for element in document.get('body').get('content'):
                if 'paragraph' in element:
                    for elem in element.get('paragraph').get('elements'):
                        if 'textRun' in elem:
                            content.append(elem.get('textRun').get('content'))
            
            return ''.join(content)
        
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def update_document(self, document_id: str, new_content: str):
        """
        Replace entire document content
        
        Args:
            document_id: ID of the document
            new_content: New content to replace with
        """
        try:
            # Get the document to find the end index
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            
            end_index = document.get('body').get('content')[-1].get('endIndex') - 1
            
            # Delete all content and insert new
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index,
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': new_content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
        
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def list_documents(self, max_results: int = 10) -> list:
        """
        List recent Google Docs
        
        Args:
            max_results: Maximum number of documents to return
        
        Returns:
            List of documents with id, name, and url
        """
        try:
            results = self.drive_service.files().list(
                pageSize=max_results,
                q="mimeType='application/vnd.google-apps.document'",
                fields="files(id, name, webViewLink, modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            return [
                {
                    'id': file['id'],
                    'name': file['name'],
                    'url': file['webViewLink'],
                    'modified': file['modifiedTime']
                }
                for file in files
            ]
        
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
