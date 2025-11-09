#!/usr/bin/env python3
"""
Re-upload AICraft as markdown file
"""

import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate, upload_file

def main():
    # Authenticate
    print("Authenticating with Google Drive...")
    drive = authenticate()

    folder_id = '1oEkKh89CzhfZDeKbCIM-6kU797nk6OsQ'  # Brainstorm with YC Application 2025

    # First, delete the old AICraft.txt file
    print("\nSearching for old AICraft.txt file...")
    from pydrive2.files import GoogleDriveFileList
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and title = 'AICraft.txt' and trashed = false"}).GetList()

    for file in file_list:
        print(f"Deleting old file: {file['title']} (ID: {file['id']})")
        file.Delete()
        print("✅ Deleted old AICraft.txt")

    # Upload as markdown
    print("\nUploading AICraft.md...")
    file_path = '/Users/wz/Desktop/zPersonalProjects/AICraft/AICraft.txt'

    # Upload with .md extension and markdown MIME type
    result = upload_file(drive, file_path, title='AICraft.md', folder_id=folder_id)

    # Override MIME type to markdown
    file_obj = drive.CreateFile({'id': result['id']})
    file_obj['mimeType'] = 'text/markdown'
    file_obj.Upload()

    print(f"✅ Uploaded: {result['title']} (ID: {result['id']})")
    print(f"File link: {result['link']}")
    print(f"\nFolder link: https://drive.google.com/drive/folders/{folder_id}")

if __name__ == '__main__':
    main()
