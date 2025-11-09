"""Stage configurations for the agent evolution curriculum.

Based on the Anthropic ampcode article's 4-stage progression:
- Stage 1: No tools, basic conversation (max_turns=3)
- Stage 2: Tools defined but explain only (max_turns=3)
- Stage 3: Execute single tools (max_turns=5)
- Stage 4: Multi-tool chaining (max_turns=10)
"""

from typing import Dict, Any, List
from tools import get_tools_for_stage


STAGE_CONFIGS = {
    1: {
        "name": "Stage 1: Basic Reasoning",
        "description": "Agent can reason and respond but has no tools available.",
        "system_prompt": """You are a helpful AI assistant. You can think and reason about problems, but you don't have access to any external tools.

Your task is to help users by:
- Understanding their questions
- Providing thoughtful answers based on your knowledge
- Explaining your reasoning process
- Being honest when you don't know something

Since you have no tools, you can only use your reasoning abilities to help.""",
        "max_turns": 3,
        "tools_available": False,
        "tools_executable": False,
        "key_activity": {
            "title": "Basic Conversation",
            "prompt": "Tell me about yourself and what you can help me with."
        },
        "teaching_points": [
            "Basic agent conversation and reasoning",
            "Understanding prompts and instructions",
            "Limitations without tool access"
        ]
    },

    2: {
        "name": "Stage 2: Tool Awareness",
        "description": "Agent can see tool schemas and explain what they do, but cannot execute them.",
        "system_prompt": """You are a helpful AI assistant who can see and understand various tools, but you CANNOT execute them yet.

You have access to these tool schemas:
- web_search: Search the web for information
- file_write: Write content to files
- file_read: Read file contents
- file_edit: Edit existing files

IMPORTANT: You can EXPLAIN what these tools do and HOW you would use them to solve a problem, but you CANNOT actually call them.

When a user asks you to do something:
1. Explain which tool(s) you would use
2. Describe what parameters you would pass
3. Explain what the expected result would be
4. Make it clear that you're explaining, not executing

Example response:
"To solve this, I would use the web_search tool with the query parameter set to 'Python tutorials'. This would return search results with titles, URLs, and snippets about Python tutorials. However, I cannot actually execute this search - I can only explain the approach."
""",
        "max_turns": 3,
        "tools_available": True,
        "tools_executable": False,
        "key_activity": {
            "title": "Explain Tool Strategy",
            "prompt": "What's the latest news about artificial intelligence?"
        },
        "teaching_points": [
            "Understanding tool schemas and capabilities",
            "Planning tool usage without execution",
            "Explaining approaches and strategies"
        ]
    },

    3: {
        "name": "Stage 3: Single Tool Execution",
        "description": "Agent can execute individual tools to accomplish tasks.",
        "system_prompt": """You are a helpful AI assistant with access to tools that you can execute.

Available tools:
- web_search: Search the web for information
- file_write: Write content to files
- file_read: Read file contents
- file_edit: Edit existing files

You can now EXECUTE these tools to help users. When a user asks you to do something:
1. Think about which tool(s) to use
2. Execute the appropriate tool with the right parameters
3. Review the result
4. Provide a helpful response based on the tool output

For this stage, focus on using ONE tool at a time to solve problems. Be thoughtful about which tool to use and what parameters to provide.

Remember to:
- Explain what you're doing before using a tool
- Share the results with the user
- Provide context and interpretation of the results
""",
        "max_turns": 5,
        "tools_available": True,
        "tools_executable": True,
        "key_activity": {
            "title": "Web Search",
            "prompt": "Search for the latest Python web frameworks and tell me which ones are most popular."
        },
        "teaching_points": [
            "Executing individual tools",
            "Interpreting tool results",
            "Single-step problem solving"
        ]
    },

    4: {
        "name": "Stage 4: Multi-Tool Orchestration",
        "description": "Agent can chain multiple tools together to solve complex tasks.",
        "system_prompt": """You are an advanced AI assistant with full access to tools and the ability to chain them together.

Available tools:
- web_search: Search the web for information
- file_write: Write content to files
- file_read: Read file contents
- file_edit: Edit existing files

You can now use MULTIPLE tools in sequence to solve complex problems. For example:
1. Search for information with web_search
2. Process and organize the information
3. Write the results to a file with file_write
4. Read back the file to verify with file_read

When solving problems:
- Break down complex tasks into steps
- Use the right tool for each step
- Build on previous tool outputs
- Verify your work when appropriate
- Provide clear explanations of your process

You have up to 10 turns to complete complex tasks, so you can iterate and refine your approach.

Think step-by-step and use tools strategically to accomplish the user's goals.
""",
        "max_turns": 10,
        "tools_available": True,
        "tools_executable": True,
        "key_activity": {
            "title": "Research & Document",
            "prompt": "Research the top 3 programming languages in 2024, then create a summary document with their key features."
        },
        "teaching_points": [
            "Chaining multiple tools together",
            "Complex multi-step problem solving",
            "Strategic tool orchestration",
            "Iterative refinement and verification"
        ]
    }
}


def get_stage_config(stage: int) -> Dict[str, Any]:
    """Get configuration for a specific stage.

    Args:
        stage: Stage number (1-4)

    Returns:
        Dictionary containing stage configuration

    Raises:
        ValueError: If stage number is invalid
    """
    if stage not in STAGE_CONFIGS:
        raise ValueError(f"Invalid stage number: {stage}. Must be 1-4.")

    config = STAGE_CONFIGS[stage].copy()

    # Add tool schemas if tools are available
    if config["tools_available"]:
        config["tools"] = get_tools_for_stage(stage)
    else:
        config["tools"] = []

    return config


def get_all_stages_info() -> List[Dict[str, Any]]:
    """Get summary information for all stages.

    Returns:
        List of dictionaries with stage metadata (excluding full prompts)
    """
    stages_info = []

    for stage_num in sorted(STAGE_CONFIGS.keys()):
        config = STAGE_CONFIGS[stage_num]
        stages_info.append({
            "id": stage_num,
            "name": config["name"],
            "description": config["description"],
            "max_turns": config["max_turns"],
            "tools_available": config["tools_available"],
            "tools_executable": config["tools_executable"],
            "key_activity": config["key_activity"],
            "capabilities": config["teaching_points"],
            "teaching_points": config["teaching_points"]
        })

    return stages_info


def validate_stage(stage: int) -> bool:
    """Check if a stage number is valid.

    Args:
        stage: Stage number to validate

    Returns:
        True if valid, False otherwise
    """
    return stage in STAGE_CONFIGS
