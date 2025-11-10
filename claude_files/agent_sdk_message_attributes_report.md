# Agent SDK Message Attributes Report

## Overview

This report documents the different message types and their attributes returned by the `claude_agent_sdk.query()` async generator. Understanding these message types is crucial for proper handling of responses from the Agent SDK.

## Message Types

The Agent SDK returns **three main message types** during a query:

1. **SystemMessage** - Initial session/system information
2. **AssistantMessage** - Claude's responses (can occur multiple times)
3. **ResultMessage** - Final result with metadata

Additional message types may appear:
- **UserMessage** - Used for tool results in multi-turn conversations

---

## 1. SystemMessage

### Purpose
Contains initialization data about the Claude session, including available tools, settings, and environment.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `subtype` | `str` | Message subtype (e.g., `"init"`) |
| `data` | `dict` | Contains comprehensive session information |

### `data` Dictionary Keys

```python
{
    'type': 'system',
    'subtype': 'init',
    'cwd': '/current/working/directory',
    'session_id': 'uuid-string',
    'tools': ['Task', 'Bash', 'Glob', ...],  # Available tools
    'mcp_servers': [],  # MCP server configurations
    'model': 'claude-sonnet-4-5-20250929',
    'permissionMode': 'default',
    'slash_commands': ['compact', 'context', ...],
    'apiKeySource': 'none',
    'claude_code_version': '2.0.36',
    'output_style': 'default',
    'agents': ['general-purpose', 'Explore', ...],
    'skills': [],
    'plugins': [],
    'uuid': 'session-uuid'
}
```

### Usage
- Typically the **first message** received
- Useful for understanding the session context
- Usually can be **ignored** for simple queries

---

## 2. AssistantMessage

### Purpose
Contains Claude's response content, which may include text, tool uses, or thinking blocks.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | `list` | List of content blocks (TextBlock, ToolUseBlock, etc.) |
| `model` | `str` | Model identifier used for this response |
| `parent_tool_use_id` | `str \| None` | ID of parent tool if this is a nested response |

### Content Block Types

The `content` list can contain:

1. **TextBlock** - Text responses
   ```python
   TextBlock(text="Hello! I'm Claude...")
   ```

2. **ToolUseBlock** - When Claude uses tools
   ```python
   ToolUseBlock(id='toolu_...', name='Write', input={...})
   ```

3. **ThinkingBlock** - Claude's reasoning (if enabled)

4. **ToolResultBlock** - Results from tool executions

### Usage
- Can occur **multiple times** in a single query (for multi-turn interactions)
- Check if `content` contains TextBlock for text responses
- Access text via: `content[0].text` (if first item is TextBlock)

### Example
```python
async for message in query(prompt="Say hello"):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"Claude says: {block.text}")
```

---

## 3. ResultMessage ⭐ (Most Important)

### Purpose
The **final message** containing the complete result and execution metadata. This is typically what you want to use.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `result` | `str \| None` | **The final text response** (most important!) |
| `subtype` | `str` | Result type (e.g., `"success"`) |
| `duration_ms` | `int` | Total duration in milliseconds |
| `duration_api_ms` | `int` | API call duration in milliseconds |
| `is_error` | `bool` | Whether an error occurred |
| `num_turns` | `int` | Number of conversation turns |
| `session_id` | `str` | Session UUID |
| `total_cost_usd` | `float \| None` | Estimated cost in USD |
| `usage` | `dict \| None` | Token usage statistics |

### `usage` Dictionary Structure

```python
{
    'input_tokens': 3,
    'cache_creation_input_tokens': 326,
    'cache_read_input_tokens': 12442,
    'output_tokens': 29,
    'server_tool_use': {
        'web_search_requests': 0,
        'web_fetch_requests': 0
    },
    'service_tier': 'standard',
    'cache_creation': {
        'ephemeral_1h_input_tokens': 0,
        'ephemeral_5m_input_tokens': 326
    }
}
```

### Usage ⭐
This is the **most important message type** for most use cases:

```python
response_text = ""

async for message in query(prompt=prompt):
    if hasattr(message, "result") and message.result:
        response_text = message.result
        # Continue to consume generator fully

print(response_text)  # Final result
```

---

## 4. UserMessage

### Purpose
Contains tool results and user inputs in multi-turn conversations.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | `list` | List of ToolResultBlock or user input blocks |

### Usage
- Appears when Claude uses tools
- Contains the results of tool executions
- Usually can be **ignored** unless you're debugging tool usage

---

## Message Flow Examples

### Simple Query
```
1. SystemMessage (init info)
2. AssistantMessage (response content)
3. ResultMessage (final result) ⭐
```

### Complex Query with Tools
```
1. SystemMessage (init info)
2. AssistantMessage (thinking/text)
3. AssistantMessage (tool use)
4. UserMessage (tool result)
5. AssistantMessage (final response)
6. ResultMessage (final result) ⭐
```

---

## Best Practices

### ✅ Recommended Pattern (Current Code)

```python
async for message in query(prompt=prompt):
    if hasattr(message, "result") and message.result:
        response_text = message.result
        # Don't break - let generator finish naturally

# Use response_text after loop completes
```

**Why this works:**
- Uses `ResultMessage.result` which contains the final, complete response
- Fully consumes the async generator (prevents asyncio issues)
- Ignores intermediate messages automatically
- Simple and reliable

### ❌ Anti-Pattern: Breaking Early

```python
async for message in query(prompt=prompt):
    if hasattr(message, "result"):
        return message.result  # DON'T DO THIS
        # Breaking early can cause asyncio scope issues
```

### ⚠️ Alternative Pattern (More Complex)

If you need to capture streaming responses:

```python
text_chunks = []

async for message in query(prompt=prompt):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                text_chunks.append(block.text)

    if hasattr(message, "result"):
        final_result = message.result

# Use text_chunks for streaming, final_result for complete response
```

---

## Checking for Attributes

### Safe Attribute Checking

All message types are dataclasses. You can check attributes using:

1. **`hasattr()`** - Recommended
   ```python
   if hasattr(message, "result"):
       print(message.result)
   ```

2. **`isinstance()`** - Type-safe
   ```python
   from claude_agent_sdk.types import ResultMessage

   if isinstance(message, ResultMessage):
       print(message.result)
   ```

3. **`vars()` or `__dict__`** - Introspection
   ```python
   attrs = vars(message)
   print(attrs.keys())
   ```

---

## Common Attributes Quick Reference

| Attribute | SystemMessage | AssistantMessage | ResultMessage | UserMessage |
|-----------|---------------|------------------|---------------|-------------|
| `result` | ❌ | ❌ | ✅ | ❌ |
| `content` | ❌ | ✅ | ❌ | ✅ |
| `data` | ✅ | ❌ | ❌ | ❌ |
| `subtype` | ✅ | ❌ | ✅ | ❌ |
| `model` | ❌ | ✅ | ❌ | ❌ |
| `is_error` | ❌ | ❌ | ✅ | ❌ |
| `usage` | ❌ | ❌ | ✅ | ❌ |

---

## Summary

### Key Takeaways

1. **Three main message types**: SystemMessage, AssistantMessage, ResultMessage
2. **`ResultMessage.result`** contains the final response you usually want
3. **Always consume the generator fully** to avoid asyncio issues
4. Use `hasattr(message, "result")` to safely check for the final result
5. The current code pattern in `llm_client.py` is correct and follows best practices

### For Most Use Cases

```python
response = ""
async for message in query(prompt=prompt):
    if hasattr(message, "result") and message.result:
        response = message.result
return response
```

This pattern works for 90% of use cases and is what the current codebase correctly implements.

---

## Appendix: Full Message Type Signatures

```python
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]

@dataclass
class AssistantMessage:
    content: list[TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock]
    model: str
    parent_tool_use_id: str | None = None

@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None

@dataclass
class UserMessage:
    content: list[ToolResultBlock | ...]
```

---

**Generated**: 2025-11-10
**Experiment Script**: `backend/experiment_agent_sdk.py`
**Source Code**: `backend/src/llm_client.py:43-47`
