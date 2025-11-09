#!/usr/bin/env python3
"""
Search Google Drive for YC application documents
"""

import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate, search_files, get_metadata

def main():
    # Authenticate
    print("Authenticating with Google Drive...")
    drive = authenticate()

    # Search for YC application related documents
    print("\nSearching for YC application documents...")
    queries = [
        "title contains 'YC'",
        "title contains 'Y Combinator'",
        "title contains 'application'",
        "fullText contains 'YC application'",
        "fullText contains 'Y Combinator'"
    ]

    all_results = {}
    for query in queries:
        print(f"\nQuery: {query}")
        results = search_files(drive, f"{query} and trashed = false", max_results=10)
        for file in results:
            if file['id'] not in all_results:
                all_results[file['id']] = file
                print(f"  - {file['title']} (ID: {file['id']})")
                print(f"    Modified: {file.get('modifiedDate', 'N/A')}")
                print(f"    Link: https://drive.google.com/file/d/{file['id']}/view")

                # Get sharing/permission info
                try:
                    metadata = get_metadata(drive, file['id'])
                    file_obj = drive.CreateFile({'id': file['id']})
                    file_obj.FetchMetadata(fields='permissions')

                    if 'permissions' in file_obj:
                        print("    Shared with:")
                        for perm in file_obj['permissions']:
                            perm_type = perm.get('type', 'unknown')
                            email = perm.get('emailAddress', perm.get('name', 'N/A'))
                            role = perm.get('role', 'N/A')
                            print(f"      - {email} ({role}, {perm_type})")
                except Exception as e:
                    print(f"    Could not fetch permissions: {e}")

if __name__ == '__main__':
    main()
