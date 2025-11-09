#!/usr/bin/env python3
"""Move current implementation to prototypes/prototype1"""
import shutil
import os
from pathlib import Path

base = Path("/Users/wz/Desktop/zPersonalProjects/AICraft")
proto1 = base / "prototypes" / "prototype1"

# Create prototype1 directory
proto1.mkdir(parents=True, exist_ok=True)

# Items to move
items_to_move = ["backend", "frontend", "test_webapp.py"]

print("Moving items to prototypes/prototype1/")
for item in items_to_move:
    src = base / item
    dst = proto1 / item

    if src.exists():
        if dst.exists():
            print(f"  Removing existing {item}")
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

        print(f"  Moving {item}")
        shutil.move(str(src), str(dst))
    else:
        print(f"  ⚠️  {item} not found")

print("✅ Move complete!")
