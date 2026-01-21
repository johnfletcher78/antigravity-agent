#!/usr/bin/env python3
"""
Test script for Google Sheets integration
"""
import sys
sys.path.append('/Users/bullfletcher/Desktop/Antigravity Marketing Agent/backend')

from services.google_sheets_service import GoogleSheetsService

def test_google_sheets():
    print("🔧 Testing Google Sheets Integration...")
    print("=" * 50)
    
    try:
        # Initialize the service
        print("\n1. Initializing Google Sheets service...")
        sheets = GoogleSheetsService()
        print("✅ Service initialized successfully!")
        
        # Create a test spreadsheet with data
        print("\n2. Creating a test spreadsheet with sample data...")
        test_data = [
            ["Name", "Email", "Role"],
            ["John Doe", "john@example.com", "Developer"],
            ["Jane Smith", "jane@example.com", "Designer"],
            ["Bob Johnson", "bob@example.com", "Manager"]
        ]
        
        result = sheets.create_spreadsheet(
            title="NAT Test Spreadsheet - Sample Data",
            data=test_data
        )
        
        print(f"✅ Spreadsheet created successfully!")
        print(f"   📊 Title: {result['title']}")
        print(f"   🔗 URL: {result['url']}")
        print(f"   🆔 ID: {result['id']}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Google Sheets integration is working!")
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure credentials.json is in the backend/ directory")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_google_sheets()
