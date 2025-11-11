#!/usr/bin/env python3
"""Fix indentation in agent_deployer.py for async for loop inside async with"""

with open('src/agent_deployer.py', 'r') as f:
    lines = f.readlines()

# Find the line with "async for message in client.query(prompt=prompt):"
output_lines = []
inside_async_for = False
async_for_indent = 0

for i, line in enumerate(lines):
    if "async for message in client.query(prompt=prompt):" in line:
        inside_async_for = True
        async_for_indent = len(line) - len(line.lstrip())
        output_lines.append(line)
        continue

    if inside_async_for:
        # Check if we've exited the async for loop (dedented line)
        current_indent = len(line) - len(line.lstrip())

        # If line is not empty and has same or less indentation than async for, we're done
        if line.strip() and current_indent <= async_for_indent:
            inside_async_for = False
            output_lines.append(line)
            continue

        # Add 4 spaces of indentation to all lines inside async for
        if line.strip():  # Only if line is not empty
            output_lines.append("    " + line)
        else:
            output_lines.append(line)
    else:
        output_lines.append(line)

with open('src/agent_deployer.py', 'w') as f:
    f.writelines(output_lines)

print("✓ Fixed indentation in agent_deployer.py")
