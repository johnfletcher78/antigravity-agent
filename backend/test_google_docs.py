#!/usr/bin/env python3
"""
Test script for Google Docs integration
"""
import sys
sys.path.append('/Users/bullfletcher/Desktop/Antigravity Marketing Agent/backend')

from services.google_docs_service import GoogleDocsService

def test_google_docs():
    print("🔧 Testing Google Docs Integration...")
    print("=" * 50)
    
    try:
        # Initialize the service (this will trigger OAuth flow)
        print("\n1. Initializing Google Docs service...")
        docs = GoogleDocsService()
        print("✅ Service initialized successfully!")
        
        # Create a test document
        print("\n2. Creating a test document...")
        result = docs.create_document(
            title="NAT Test Document - " + str(int(time.time())),
            content="Hello from NAT! This is a test document created programmatically.\n\nThis confirms that NAT can now create and manage Google Docs!"
        )
        
        print(f"✅ Document created successfully!")
        print(f"   📄 Title: {result['title']}")
        print(f"   🔗 URL: {result['url']}")
        print(f"   🆔 ID: {result['id']}")
        
        # List recent documents
        print("\n3. Listing recent documents...")
        documents = docs.list_documents(max_results=5)
        print(f"✅ Found {len(documents)} recent documents:")
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc['name']}")
            print(f"      URL: {doc['url']}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Google Docs integration is working!")
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure credentials.json is in the backend/ directory")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    import time
    test_google_docs()
