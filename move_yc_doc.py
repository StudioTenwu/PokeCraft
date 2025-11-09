#!/usr/bin/env python3
"""
Move YCApplication2025 document into the Brainstorm with YC Application 2025 folder
"""

import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate

def main():
    # Authenticate
    print("Authenticating with Google Drive...")
    drive = authenticate()

    # IDs
    doc_id = '1XskfMFw9OPSI2pLUmTytGoNpixeiDjWVNzgztBG9vBo'  # YCApplication2025
    folder_id = '1oEkKh89CzhfZDeKbCIM-6kU797nk6OsQ'  # Brainstorm with YC Application 2025

    # Get the document
    print("\nFetching YCApplication2025 document...")
    doc = drive.CreateFile({'id': doc_id})
    doc.FetchMetadata(fields='title,parents')

    print(f"Document: {doc['title']}")
    print(f"Current parents: {doc.get('parents', [])}")

    # Get current parent IDs
    old_parents = [{'id': parent['id']} for parent in doc.get('parents', [])]

    # Move the document to the new folder
    print(f"\nMoving document to folder {folder_id}...")

    # Remove from old parents and add to new parent
    doc['parents'] = [{'id': folder_id}]
    doc.Upload()

    print(f"✅ Successfully moved YCApplication2025 to 'Brainstorm with YC Application 2025' folder")
    print(f"\nDocument link: https://drive.google.com/file/d/{doc_id}/view")
    print(f"Folder link: https://drive.google.com/drive/folders/{folder_id}")

if __name__ == '__main__':
    main()
