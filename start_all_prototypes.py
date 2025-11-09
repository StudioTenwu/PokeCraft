#!/usr/bin/env python3
"""Start all three prototypes"""
import subprocess
import time
import os
from pathlib import Path

base = Path("/Users/wz/Desktop/zPersonalProjects/AICraft/prototypes")

print("🚀 Starting all AICraft prototypes...\n")

# Prototype 2 - Frontend only on port 3000
print("📦 Starting Prototype 2 (Director-Observer)...")
proto2 = base / "prototype2"
if proto2.exists():
    subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=proto2,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("   ✅ Prototype 2 starting on http://localhost:3000")
else:
    print("   ⚠️  Prototype 2 not found")

time.sleep(2)

# Prototype 3 - Backend on 8001, Frontend on 5173
print("\n🎮 Starting Prototype 3 (Four Primitives)...")
proto3 = base / "prototype3"
if proto3.exists():
    # Start backend
    subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--port", "8001"],
        cwd=proto3 / "backend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("   ✅ Backend starting on http://localhost:8001")

    time.sleep(2)

    # Start frontend
    subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=proto3 / "frontend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("   ✅ Frontend starting on http://localhost:5173")
else:
    print("   ⚠️  Prototype 3 not found")

time.sleep(2)

# Prototype 4 - Backend on 8002, Frontend on 5174
print("\n🏗️  Starting Prototype 4 (Exportable Scaffolds)...")
proto4 = base / "prototype4"
if proto4.exists():
    # Initialize if needed
    init_file = proto4 / "backend" / "initialize.py"
    if init_file.exists():
        print("   Initializing database...")
        subprocess.run(
            ["python3", "initialize.py"],
            cwd=proto4 / "backend",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # Start backend
    subprocess.Popen(
        ["python3", "-m", "src.app"],
        cwd=proto4 / "backend",
        env={**os.environ, "FLASK_RUN_PORT": "8002"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("   ✅ Backend starting on http://localhost:8002")

    time.sleep(2)

    # Start frontend (Vite will auto-select 5174 if 5173 is taken)
    subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "5174"],
        cwd=proto4 / "frontend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("   ✅ Frontend starting on http://localhost:5174")
else:
    print("   ⚠️  Prototype 4 not found")

print("\n" + "="*60)
print("🎉 All prototypes started!")
print("="*60)
print("\n📍 Access them at:")
print("   • Prototype 2: http://localhost:3000")
print("   • Prototype 3: http://localhost:5173")
print("   • Prototype 4: http://localhost:5174")
print("\n💡 Tip: Open each URL in a different browser tab")
print("⏱️  Give them 10-15 seconds to fully start up")
