#!/usr/bin/env python3
"""
Automated book downloader using search CLI
Simulates interactive input for batch downloads
"""

import subprocess
import sys

# Books to download: (query, selection_number)
BOOKS = [
    ("Introduction to Game Design Prototyping Development Jeremy Gibson Bond", "6"),
    ("Unity Development Cookbook", "1"),
    ("Godot 4 Game Development Projects", "3"),
]

def download_book(query: str, selection: str) -> bool:
    """Download a book by providing simulated input"""
    print(f"\n{'='*60}")
    print(f"📚 Downloading: {query}")
    print(f"   Selection: #{selection}")
    print(f"{'='*60}\n")

    try:
        # Run search download with interactive flag, provide selection via stdin
        process = subprocess.Popen(
            ["search", "download", query, "--interactive"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send the selection number
        stdout, stderr = process.communicate(input=f"{selection}\n")

        print(stdout)
        if stderr:
            print(f"Errors: {stderr}", file=sys.stderr)

        if process.returncode == 0:
            print(f"✅ Successfully downloaded!\n")
            return True
        else:
            print(f"❌ Download failed with code {process.returncode}\n")
            return False

    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

def main():
    print("\n" + "="*60)
    print("🎮 Auto-downloading Game Development Books")
    print("="*60)
    print(f"\nDownloading {len(BOOKS)} books to ~/Desktop/AArchive/\n")

    results = []
    for query, selection in BOOKS:
        success = download_book(query, selection)
        results.append((query, success))

    # Summary
    print("\n" + "="*60)
    print("📊 Download Summary")
    print("="*60 + "\n")

    for query, success in results:
        status = "✅" if success else "❌"
        short_name = query.split()[0:3]
        print(f"{status} {' '.join(short_name)}...")

    success_count = sum(1 for _, s in results if s)
    print(f"\n{success_count}/{len(BOOKS)} books downloaded successfully")

    if success_count == len(BOOKS):
        print("\n🎉 All books downloaded! Check ~/Desktop/AArchive/")
    else:
        print("\n⚠️  Some downloads failed. You can run them manually:")
        for query, success in results:
            if not success:
                print(f'  search download "{query}" --interactive')

if __name__ == "__main__":
    main()
