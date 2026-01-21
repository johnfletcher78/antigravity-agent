"""
Contact Management Service
Manages contacts stored in Google Sheets
"""

from services.google_sheets_service import GoogleSheetsService

class ContactService:
    def __init__(self):
        self.sheets = GoogleSheetsService()
        self.spreadsheet_id = self._get_or_create_contact_sheet()
    
    def _get_or_create_contact_sheet(self):
        """Get existing contact sheet or create new one"""
        try:
            with open('contact_sheet_id.txt', 'r') as f:
                sheet_id = f.read().strip()
                # Verify it exists
                try:
                    self.sheets.read_data(sheet_id, "A1:A1")
                    return sheet_id
                except:
                    # Sheet doesn't exist, create new one
                    pass
        except FileNotFoundError:
            pass
        
        # Create new contact sheet
        result = self.sheets.create_spreadsheet("NAT Contacts")
        sheet_id = result['id']  # Extract ID from the returned dict
        
        # Add headers with new column names
        headers = [["Full Name", "Email", "Cell Phone", "Contact Description"]]
        self.sheets.add_data(sheet_id, headers, "A1")
        
        # Save sheet ID
        with open('contact_sheet_id.txt', 'w') as f:
            f.write(sheet_id)
        
        return sheet_id
    
    def search_contact(self, name: str) -> dict:
        """
        Search for a contact by name
        
        Args:
            name: Contact name (partial match supported)
        
        Returns:
            dict with contact info or None
        """
        try:
            # Get all contacts
            data = self.sheets.read_data(self.spreadsheet_id, "A2:F1000")
            
            if not data:
                return {
                    "success": False,
                    "error": "No contacts found"
                }
            
            # Search for matching name (case-insensitive)
            name_lower = name.lower()
            matches = []
            
            for row in data:
                if len(row) > 0 and name_lower in row[0].lower():
                    contact = {
                        "name": row[0] if len(row) > 0 else "",
                        "email": row[1] if len(row) > 1 else "",
                        "phone": row[2] if len(row) > 2 else "",
                        "description": row[3] if len(row) > 3 else ""
                    }
                    matches.append(contact)
            
            if not matches:
                return {
                    "success": False,
                    "error": f"No contact found for '{name}'"
                }
            
            # Return first match (or all matches if multiple)
            return {
                "success": True,
                "contact": matches[0],
                "all_matches": matches if len(matches) > 1 else None,
                "count": len(matches)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_contact(self, name: str, email: str, phone: str = "", description: str = "") -> dict:
        """
        Add a new contact
        
        Args:
            name: Full name
            email: Email address
            phone: Cell phone number
            description: Contact description
        
        Returns:
            dict with success status
        """
        try:
            # Find next empty row
            data = self.sheets.read_data(self.spreadsheet_id, "A:A")
            next_row = len(data) + 1 if data else 2
            
            # Add contact
            contact_data = [[name, email, phone, description]]
            self.sheets.add_data(self.spreadsheet_id, contact_data, f"A{next_row}")
            
            return {
                "success": True,
                "message": f"Added contact: {name} ({email})",
                "spreadsheet_id": self.spreadsheet_id
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_all_contacts(self) -> dict:
        """Get all contacts"""
        try:
            data = self.sheets.read_data(self.spreadsheet_id, "A2:F1000")
            
            if not data:
                return {
                    "success": True,
                    "contacts": [],
                    "count": 0
                }
            
            contacts = []
            for row in data:
                if len(row) > 0 and row[0]:  # Has name
                    contact = {
                        "name": row[0] if len(row) > 0 else "",
                        "email": row[1] if len(row) > 1 else "",
                        "phone": row[2] if len(row) > 2 else "",
                        "description": row[3] if len(row) > 3 else ""
                    }
                    contacts.append(contact)
            
            return {
                "success": True,
                "contacts": contacts,
                "count": len(contacts),
                "spreadsheet_id": self.spreadsheet_id
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_contact(self, name: str, email: str = None, phone: str = None, description: str = None) -> dict:
        """
        Update an existing contact
        
        Args:
            name: Contact name to search for
            email: New email (optional)
            phone: New phone (optional)
            description: New description (optional)
        
        Returns:
            dict with success status
        """
        try:
            # Find the contact
            data = self.sheets.read_data(self.spreadsheet_id, "A2:D1000")
            
            if not data:
                return {"success": False, "error": "No contacts found"}
            
            name_lower = name.lower()
            row_index = None
            
            for i, row in enumerate(data):
                if len(row) > 0 and name_lower in row[0].lower():
                    row_index = i + 2  # +2 because data starts at row 2
                    break
            
            if row_index is None:
                return {"success": False, "error": f"Contact '{name}' not found"}
            
            # Get current values
            current_row = data[row_index - 2]
            updated_row = [
                current_row[0] if len(current_row) > 0 else "",  # Name stays same
                email if email is not None else (current_row[1] if len(current_row) > 1 else ""),
                phone if phone is not None else (current_row[2] if len(current_row) > 2 else ""),
                description if description is not None else (current_row[3] if len(current_row) > 3 else "")
            ]
            
            # Update the row
            self.sheets.add_data(self.spreadsheet_id, [updated_row], f"A{row_index}")
            
            return {
                "success": True,
                "message": f"Updated contact: {current_row[0]}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_contact(self, name: str) -> dict:
        """
        Delete a contact
        
        Args:
            name: Contact name to delete
        
        Returns:
            dict with success status
        """
        try:
            # Find the contact
            data = self.sheets.read_data(self.spreadsheet_id, "A2:D1000")
            
            if not data:
                return {"success": False, "error": "No contacts found"}
            
            name_lower = name.lower()
            row_index = None
            contact_name = None
            
            for i, row in enumerate(data):
                if len(row) > 0 and name_lower in row[0].lower():
                    row_index = i + 2
                    contact_name = row[0]
                    break
            
            if row_index is None:
                return {"success": False, "error": f"Contact '{name}' not found"}
            
            # Clear the row (we can't actually delete rows via API easily, so we clear it)
            empty_row = [["", "", "", ""]]
            self.sheets.add_data(self.spreadsheet_id, empty_row, f"A{row_index}")
            
            return {
                "success": True,
                "message": f"Deleted contact: {contact_name}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
