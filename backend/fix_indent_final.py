#!/usr/bin/env python3
"""Fix indentation - indent lines 174-313 by 4 spaces"""

with open('src/agent_deployer.py', 'r') as f:
    lines = f.readlines()

# Indent lines 174-313 (0-indexed: 173-312)
for i in range(173, 313):
    if i < len(lines) and lines[i].strip():  # Only if line exists and is not empty
        lines[i] = '    ' + lines[i]

with open('src/agent_deployer.py', 'w') as f:
    f.writelines(lines)

print("✓ Fixed indentation for lines 174-313")
