"""
Gmail Service
Handles sending and managing emails via Gmail API
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from services.google_oauth_service import GoogleOAuthService
from googleapiclient.discovery import build

class GmailService:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._get_gmail_service()
    
    def _get_gmail_service(self):
        """Initialize Gmail API service using unified OAuth"""
        oauth = GoogleOAuthService(self.credentials_file, self.token_file)
        creds = oauth.get_credentials()
        return build('gmail', 'v1', credentials=creds)
    
    def send_email(self, to: str, subject: str, body: str, from_email: str = "me") -> dict:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_email: Sender (default: "me" for authenticated user)
        
        Returns:
            dict with success status and message ID
        """
        try:
            message = MIMEText(body, 'html' if '<' in body else 'plain')
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId=from_email,
                body={'raw': raw_message}
            ).execute()
            
            return {
                "success": True,
                "message_id": send_message['id'],
                "to": to,
                "subject": subject
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def draft_email(self, to: str, subject: str, body: str) -> dict:
        """
        Create a draft email (for review before sending)
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
        
        Returns:
            dict with success status and draft ID
        """
        try:
            message = MIMEText(body, 'html' if '<' in body else 'plain')
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            return {
                "success": True,
                "draft_id": draft['id'],
                "to": to,
                "subject": subject,
                "message": "Draft created - review in Gmail before sending"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_email_with_attachment(self, to: str, subject: str, body: str, 
                                   attachment_path: str, attachment_name: str = None) -> dict:
        """
        Send an email with an attachment
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachment_path: Path to file to attach
            attachment_name: Name for attachment (optional, uses filename if not provided)
        
        Returns:
            dict with success status and message ID
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            # Add body
            message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
            
            # Add attachment
            if os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                
                filename = attachment_name or os.path.basename(attachment_path)
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                message.attach(part)
            else:
                return {
                    "success": False,
                    "error": f"Attachment file not found: {attachment_path}"
                }
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "success": True,
                "message_id": send_message['id'],
                "to": to,
                "subject": subject,
                "attachment": filename
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_email(self) -> str:
        """Get the authenticated user's email address"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress', 'unknown')
        except Exception as e:
            return 'unknown'

    def get_unread_emails(self, max_results: int = 10) -> dict:
        """
        Get unread emails from inbox
        
        Args:
            max_results: Maximum number of emails to return
        
        Returns:
            dict with list of unread emails
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return {
                    "success": True,
                    "count": 0,
                    "emails": []
                }
            
            emails = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Get email body
                body = ""
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = part['body'].get('data', '')
                            if body:
                                import base64
                                body = base64.urlsafe_b64decode(body).decode('utf-8')
                            break
                
                emails.append({
                    "id": msg['id'],
                    "from": from_email,
                    "subject": subject,
                    "date": date,
                    "snippet": message.get('snippet', ''),
                    "body_preview": body[:200] if body else message.get('snippet', '')
                })
            
            return {
                "success": True,
                "count": len(emails),
                "emails": emails
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_emails(self, query: str, max_results: int = 10) -> dict:
        """
        Search emails by query
        
        Args:
            query: Gmail search query (e.g., "from:example@email.com", "subject:meeting")
            max_results: Maximum number of results
        
        Returns:
            dict with search results
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return {
                    "success": True,
                    "count": 0,
                    "emails": []
                }
            
            emails = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                emails.append({
                    "id": msg['id'],
                    "from": from_email,
                    "subject": subject,
                    "date": date,
                    "snippet": message.get('snippet', '')
                })
            
            return {
                "success": True,
                "count": len(emails),
                "query": query,
                "emails": emails
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def mark_as_read(self, message_id: str) -> dict:
        """
        Mark an email as read
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            dict with success status
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return {
                "success": True,
                "message": f"Marked email {message_id} as read"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
