#!/usr/bin/env python3
"""
Upload AICraft.txt to Google Drive in a structured folder and share with Matt K
"""

import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate, create_folder, upload_file, search_files

def main():
    # Authenticate
    print("Authenticating with Google Drive...")
    drive = authenticate()

    # Create folder "Brainstorm with YC Application 2025"
    print("Creating folder 'Brainstorm with YC Application 2025'...")
    folder = create_folder(drive, 'Brainstorm with YC Application 2025')
    folder_id = folder['id']
    print(f"Created folder: {folder['title']} (ID: {folder_id})")
    print(f"Folder link: {folder['link']}")

    # Upload AICraft.txt to the folder
    print("\nUploading AICraft.txt...")
    file_path = '/Users/wz/Desktop/zPersonalProjects/AICraft/AICraft.txt'
    result = upload_file(drive, file_path, title='AICraft.txt', folder_id=folder_id)
    print(f"Uploaded: {result['title']} (ID: {result['id']})")
    print(f"File link: {result['link']}")

    # Share with Matt K
    print("\nSharing folder with Matt K...")

    # Try common YC email formats
    possible_emails = [
        "matt@ycombinator.com",
        "mattk@ycombinator.com",
        "matt.krisiloff@ycombinator.com",
        "krisiloff@ycombinator.com"
    ]

    # Get the folder file object
    folder_file = drive.CreateFile({'id': folder_id})

    # Try to share with first available email
    shared = False
    for email in possible_emails:
        try:
            print(f"Attempting to share with {email}...")
            permission = folder_file.InsertPermission({
                'type': 'user',
                'value': email,
                'role': 'writer',  # Edit access
                'emailMessage': 'Shared folder: Brainstorm with YC Application 2025'
            })
            print(f"✅ Successfully shared with {email}")
            shared = True
            break
        except Exception as e:
            print(f"   Could not share with {email}: {str(e)}")
            continue

    if not shared:
        print("\nCould not automatically share. You can share manually using:")
        print(f"Folder link: {folder['link']}")
        print("\nOr if you know Matt K's email, run this Python code:")
        print(f"""
folder_file = drive.CreateFile({{'id': '{folder_id}'}})
permission = folder_file.InsertPermission({{
    'type': 'user',
    'value': 'matt@email.com',  # Replace with actual email
    'role': 'writer'
}})
""")

    print("\n✅ Upload complete!")
    print(f"Folder: {folder['link']}")
    print(f"File: {result['link']}")

if __name__ == '__main__':
    main()
