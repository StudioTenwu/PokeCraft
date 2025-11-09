#!/bin/bash
# Verification script for AICraft rename

echo "=== Verifying AICraft Rename ==="
echo ""

# Check directory exists
if [ -d "/Users/wz/Desktop/zPersonalProjects/AICraft" ]; then
    echo "✅ AICraft directory exists"
else
    echo "❌ AICraft directory NOT found"
    exit 1
fi

# Check for any remaining RLCraft references
echo ""
echo "Searching for remaining 'RLCraft' references..."
cd /Users/wz/Desktop/zPersonalProjects/AICraft
matches=$(grep -r "RLCraft" --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude="*.log" --exclude="verify_rename.sh" . 2>/dev/null | wc -l)

if [ "$matches" -eq 0 ]; then
    echo "✅ No 'RLCraft' references found"
else
    echo "⚠️  Found $matches 'RLCraft' references:"
    grep -r "RLCraft" --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude="*.log" --exclude="verify_rename.sh" . 2>/dev/null | head -10
fi

# Check if backend is running
echo ""
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "⚠️  Backend not responding on port 8000"
fi

# Check if frontend is running
echo ""
if curl -s http://localhost:5175/ > /dev/null 2>&1; then
    echo "✅ Frontend is running on port 5175"
else
    echo "⚠️  Frontend not responding on port 5175"
fi

echo ""
echo "=== Rename Verification Complete ==="
