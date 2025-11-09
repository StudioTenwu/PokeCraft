"""Tool definitions and execution functions for agent stages."""

import json
from pathlib import Path
from typing import Any, Dict


# Tool Schemas for Claude Agent SDK
TOOL_SCHEMAS = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web for information. Returns search results with titles, URLs, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up"
                }
            },
            "required": ["query"]
        }
    },
    "calculator": {
        "name": "calculator",
        "description": "Perform mathematical calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    },
    "image_gen": {
        "name": "image_gen",
        "description": "Generate images from text descriptions",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Image description"
                },
                "size": {
                    "type": "string",
                    "enum": ["256x256", "512x512", "1024x1024"]
                }
            },
            "required": ["prompt"]
        }
    },
    "code_exec": {
        "name": "code_exec",
        "description": "Execute Python code safely",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                }
            },
            "required": ["code"]
        }
    },
    "file_write": {
        "name": "file_write",
        "description": "Write content to a file. Creates a new file or overwrites existing file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to write to (relative or absolute)"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    "file_read": {
        "name": "file_read",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read from"
                }
            },
            "required": ["path"]
        }
    },
    "file_edit": {
        "name": "file_edit",
        "description": "Edit a file by applying changes to specific sections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to edit"
                },
                "changes": {
                    "type": "string",
                    "description": "Description of changes to make (e.g., 'Replace line 10 with X', 'Add Y after line 5')"
                }
            },
            "required": ["path", "changes"]
        }
    }
}


# Tool Execution Functions
def execute_web_search(query: str) -> Dict[str, Any]:
    """Mock implementation of web search.

    In production, this would call a real search API.
    """
    return {
        "success": True,
        "results": [
            {
                "title": f"Search result for: {query}",
                "url": f"https://example.com/search?q={query}",
                "snippet": f"This is a mock search result for the query: {query}. "
                          "In a real implementation, this would return actual search results."
            },
            {
                "title": f"Another result for: {query}",
                "url": f"https://example.com/result2?q={query}",
                "snippet": "This demonstrates multiple search results being returned."
            }
        ],
        "query": query,
        "result_count": 2
    }


def execute_file_write(path: str, content: str) -> Dict[str, Any]:
    """Write content to a file."""
    try:
        file_path = Path(path)

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        file_path.write_text(content)

        return {
            "success": True,
            "path": str(file_path.absolute()),
            "bytes_written": len(content),
            "message": f"Successfully wrote {len(content)} bytes to {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to write to {path}: {str(e)}"
        }


def execute_file_read(path: str) -> Dict[str, Any]:
    """Read the contents of a file."""
    try:
        file_path = Path(path)

        if not file_path.exists():
            return {
                "success": False,
                "error": "File not found",
                "message": f"File does not exist: {path}"
            }

        content = file_path.read_text()

        return {
            "success": True,
            "path": str(file_path.absolute()),
            "content": content,
            "size_bytes": len(content),
            "line_count": len(content.splitlines())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to read {path}: {str(e)}"
        }


def execute_file_edit(path: str, changes: str) -> Dict[str, Any]:
    """Edit a file by applying described changes.

    This is a simplified implementation. In production, you might use
    a more sophisticated diff/patch system.
    """
    try:
        file_path = Path(path)

        if not file_path.exists():
            return {
                "success": False,
                "error": "File not found",
                "message": f"Cannot edit non-existent file: {path}"
            }

        # For this mock implementation, we'll just append the changes as a comment
        original_content = file_path.read_text()

        # Simple edit: append changes description
        edited_content = original_content + f"\n\n# Edit applied: {changes}\n"

        file_path.write_text(edited_content)

        return {
            "success": True,
            "path": str(file_path.absolute()),
            "changes_applied": changes,
            "message": f"Successfully edited {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to edit {path}: {str(e)}"
        }


# Tool execution dispatcher
TOOL_EXECUTORS = {
    "web_search": execute_web_search,
    "file_write": execute_file_write,
    "file_read": execute_file_read,
    "file_edit": execute_file_edit,
}


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name with given input.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Dictionary of input parameters

    Returns:
        Dictionary containing the tool execution result
    """
    if tool_name not in TOOL_EXECUTORS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
            "message": f"Tool '{tool_name}' is not available"
        }

    try:
        executor = TOOL_EXECUTORS[tool_name]
        result = executor(**tool_input)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error executing {tool_name}: {str(e)}"
        }


# Export TOOL_DEFINITIONS for API
TOOL_DEFINITIONS = list(TOOL_SCHEMAS.values())


def get_tools_for_stage(stage: int) -> list:
    """Get the list of tool schemas for a given stage.

    Args:
        stage: Stage number (1-4)

    Returns:
        List of tool schemas appropriate for the stage
    """
    if stage == 1:
        # Stage 1: No tools
        return []
    elif stage == 2:
        # Stage 2: Tools defined but explain only (agent sees schemas but doesn't execute)
        # We still return the schemas so agent can explain them
        return list(TOOL_SCHEMAS.values())
    elif stage == 3:
        # Stage 3: Execute single tools
        return list(TOOL_SCHEMAS.values())
    elif stage == 4:
        # Stage 4: Multi-tool chaining
        return list(TOOL_SCHEMAS.values())
    else:
        return []
