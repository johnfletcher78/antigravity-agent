# Google Docs & Drive API Setup for NAT

**Last Updated:** January 20, 2026  
**Purpose:** Enable NAT to create and manage Google Docs

---

## 🎯 Overview

This guide will help you set up Google Docs and Drive API access so NAT can:
- Create Google Docs programmatically
- Read and write document content
- List and manage your documents
- Share documents automatically

---

## 📋 Prerequisites

- Google Account
- Access to Google Cloud Console
- NAT backend running locally

---

## 🚀 Setup Steps

### **Step 1: Enable Google APIs**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one:
   - Click "Select a project" at the top
   - Click "NEW PROJECT"
   - Name it "NAT Marketing Assistant"
   - Click "CREATE"

3. Enable required APIs:
   - Go to "APIs & Services" → "Library"
   - Search for and enable:
     - **Google Docs API**
     - **Google Drive API**

### **Step 2: Create OAuth 2.0 Credentials**

1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: **NAT Marketing Assistant**
   - User support email: Your email
   - Developer contact: Your email
   - Click "SAVE AND CONTINUE"
   - Scopes: Skip for now (click "SAVE AND CONTINUE")
   - Test users: Add your email
   - Click "SAVE AND CONTINUE"

4. Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: **NAT Desktop Client**
   - Click "CREATE"

5. Download credentials:
   - Click the download icon (⬇️) next to your new OAuth 2.0 Client ID
   - Save the file as `credentials.json`

### **Step 3: Install Credentials**

1. Move `credentials.json` to the backend directory:
   ```bash
   mv ~/Downloads/credentials.json "/Users/bullfletcher/Desktop/Antigravity Marketing Agent/backend/"
   ```

2. Verify the file is in place:
   ```bash
   ls "/Users/bullfletcher/Desktop/Antigravity Marketing Agent/backend/credentials.json"
   ```

### **Step 4: First-Time Authentication**

1. The first time NAT tries to use Google Docs, you'll need to authenticate:
   - A browser window will open automatically
   - Sign in with your Google account
   - Click "Allow" to grant permissions
   - The browser will show "The authentication flow has completed"

2. A `token.json` file will be created automatically
   - This stores your authentication for future use
   - **Never commit this file to Git** (it's in .gitignore)

---

## 🧪 Testing the Integration

### **Test 1: Create a Document**

```python
from services.google_docs_service import GoogleDocsService

# Initialize service
docs = GoogleDocsService()

# Create a test document
result = docs.create_document(
    title="NAT Test Document",
    content="Hello from NAT! This document was created programmatically."
)

print(f"Document created: {result['url']}")
```

### **Test 2: List Documents**

```python
# List recent documents
documents = docs.list_documents(max_results=5)

for doc in documents:
    print(f"{doc['name']}: {doc['url']}")
```

---

## 🔧 Integration with NAT

NAT can now use these commands:

### **Create a Document**
```
You: "NAT, create a Google Doc called 'Campaign Strategy'"
NAT: "I've created the document: [link]"
```

### **Add Content**
```
You: "Add a section about SEO best practices"
NAT: "Added! Here's the updated doc: [link]"
```

### **List Documents**
```
You: "Show me my recent Google Docs"
NAT: "Here are your 5 most recent documents: ..."
```

---

## 📁 File Structure

```
backend/
├── credentials.json       # OAuth client credentials (from Google Cloud)
├── token.json            # Auto-generated auth token (DO NOT COMMIT)
└── services/
    └── google_docs_service.py  # Google Docs integration
```

---

## 🔒 Security Notes

### **Files to NEVER Commit:**
- ✅ `credentials.json` - Already in .gitignore
- ✅ `token.json` - Already in .gitignore

### **Permissions Granted:**
- **Google Docs API**: Create, read, update documents
- **Google Drive API**: Manage files created by NAT

### **Scope Limitations:**
- NAT can only access files she creates
- Cannot access your existing Google Docs (unless you share them)
- Cannot delete files (safety feature)

---

## 🐛 Troubleshooting

### **Error: "credentials.json not found"**
**Solution:** Download credentials from Google Cloud Console and place in `backend/` directory

### **Error: "Access blocked: This app's request is invalid"**
**Solution:** 
1. Go to Google Cloud Console
2. OAuth consent screen
3. Add your email to "Test users"
4. Try again

### **Error: "Token has been expired or revoked"**
**Solution:**
1. Delete `token.json`
2. Run the authentication flow again
3. Grant permissions

### **Browser doesn't open for authentication**
**Solution:**
1. Check terminal for the authentication URL
2. Copy and paste it into your browser manually
3. Complete the authentication flow

---

## 🎯 Next Steps

Once set up, NAT can:

1. **Create campaign reports** as Google Docs
2. **Generate SEO audits** with findings
3. **Build content calendars** in Docs
4. **Share documents** automatically
5. **Update docs** based on your requests

---

## 📚 Additional Resources

- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)

---

## ✅ Verification Checklist

Before using NAT's Google Docs features:

- [ ] Google Cloud project created
- [ ] Google Docs API enabled
- [ ] Google Drive API enabled
- [ ] OAuth 2.0 credentials created
- [ ] `credentials.json` downloaded
- [ ] `credentials.json` placed in `backend/` directory
- [ ] First-time authentication completed
- [ ] `token.json` generated successfully
- [ ] Test document creation works

---

**Document Version:** 1.0  
**Last Updated:** January 20, 2026  
**Status:** Ready for Setup
