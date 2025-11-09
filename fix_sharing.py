#!/usr/bin/env python3
"""
Fix sharing - remove incorrect person and add Matthew Kotzbauer
"""

import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate

def main():
    # Authenticate
    print("Authenticating with Google Drive...")
    drive = authenticate()

    folder_id = '1oEkKh89CzhfZDeKbCIM-6kU797nk6OsQ'  # Brainstorm with YC Application 2025

    # Get the folder
    folder = drive.CreateFile({'id': folder_id})
    folder.FetchMetadata(fields='permissions')

    print("\nCurrent permissions:")
    if 'permissions' in folder:
        for perm in folder['permissions']:
            email = perm.get('emailAddress', perm.get('name', 'N/A'))
            role = perm.get('role', 'N/A')
            perm_id = perm.get('id')
            print(f"  - {email} ({role}) [ID: {perm_id}]")

            # Remove the incorrect matt@ycombinator.com permission
            if email == 'matt@ycombinator.com':
                print(f"\n  Removing incorrect permission for {email}...")
                try:
                    folder.DeletePermission(perm_id)
                    print(f"  ✅ Removed {email}")
                except Exception as e:
                    print(f"  ❌ Could not remove {email}: {e}")

    # Add Matthew Kotzbauer
    print("\nAdding Matthew Kotzbauer...")
    matt_emails = [
        'matthewkotzbauer@college.harvard.edu',
        'mkotzbauer52@gmail.com'
    ]

    for email in matt_emails:
        try:
            print(f"  Sharing with {email}...")
            permission = folder.InsertPermission({
                'type': 'user',
                'value': email,
                'role': 'writer',
                'emailMessage': 'Shared folder: Brainstorm with YC Application 2025'
            })
            print(f"  ✅ Successfully shared with {email}")
        except Exception as e:
            print(f"  ⚠️  Could not share with {email}: {e}")

    print("\n✅ Sharing fixed!")
    print(f"Folder link: https://drive.google.com/drive/folders/{folder_id}")

if __name__ == '__main__':
    main()
