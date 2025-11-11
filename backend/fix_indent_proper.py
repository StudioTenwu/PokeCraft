#!/usr/bin/env python3
"""Properly fix indentation after async with/for addition"""

with open('src/agent_deployer.py', 'r') as f:
    content = f.read()

# Find the line numbers for the async for loop
lines = content.split('\n')
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'async for message in client.query(prompt=prompt):' in line:
        start_line = i
        # Find the indentation level of the async for
        base_indent = len(line) - len(line.lstrip())

        # Find the end of the async for block (when indentation returns to same or less)
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == '':
                continue
            current_indent = len(lines[j]) - len(lines[j].lstrip())
            if current_indent <= base_indent:
                end_line = j
                break
        break

if start_line and end_line:
    # Add 4 spaces to all lines between start_line+1 and end_line
    for i in range(start_line + 1, end_line):
        if lines[i].strip():  # Only if line is not empty
            lines[i] = '    ' + lines[i]

    with open('src/agent_deployer.py', 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Fixed indentation from line {start_line+1} to {end_line}")
else:
    print("Could not find async for loop")
