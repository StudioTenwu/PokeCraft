# Phase 3: Teaching Tools Implementation

## Context
You are implementing Phase 3 of AICraft - the "Teaching Tools" feature where children can teach their AI agents new capabilities through natural language.

**Previous Phases Completed:**
- ✅ Phase 1: Agent Birth (agent creation, avatar generation with mflux)
- ✅ Phase 2: World Creation (2D grid world generation)

## Your Task: Implement Simplified Tool Generation System

Build the tool teaching system using the **Direct Claude Generation** approach from designer.md:

### Architecture Overview

**Flow:**
1. Child describes tool: "I want my agent to move forward 3 steps"
2. Claude generates tool function with `@tool` decorator
3. Tool dynamically registered to MCP server
4. Agent uses custom tools via Claude Agent SDK

### Implementation Requirements

#### 1. Backend Components (`backend/src/`)

**`tool_generator.py`** - Tool code generation service
```python
class ToolGenerator:
    async def generate_tool(self, description: str, agent_id: str) -> ToolCode:
        """
        Uses Claude Agent SDK to generate @tool-decorated function.
        
        Returns:
        - tool_name: str
        - code: str (complete @tool function)
        - explanation: str (kid-friendly explanation)
        """
```

Requirements:
- Use Claude Agent SDK (NOT direct Anthropic API)
- Generate valid Python with `@tool` decorator
- Validate syntax with `ast.parse()`
- Forbidden imports: `os`, `subprocess`, `sys`, `importlib`
- Return XML-wrapped JSON output

**`tools.py`** - Auto-generated tool storage
- Initially empty file with docstring
- Claude appends new @tool functions here
- Format:
```python
@tool("move_forward", "Move agent forward", {"steps": int})
async def move_forward(args: dict[str, Any]) -> dict[str, Any]:
    # Implementation
    return {"content": [{"type": "text", "text": "..."}]}
```

**`tool_registry.py`** - Dynamic tool discovery
```python
def get_available_tools(agent_id: str) -> list[Callable]:
    """Import and return all @tool functions for agent"""

def create_user_tool_server() -> McpSdkServerConfig:
    """Create MCP server with discovered tools"""
```

**`agent_deployer.py`** - Agent execution
```python
async def deploy_agent(agent_id: str, world_id: str, goal: str):
    """
    Deploy agent with custom tools using Claude Agent SDK.
    
    Stream via SSE:
    - Agent reasoning
    - Tool calls
    - World state updates
    - Completion status
    """
```

#### 2. Database Schema

**`models/db_models.py`** - Add ToolDB model
```python
class ToolDB(Base):
    __tablename__ = "tools"
    id: Column(String, primary_key=True)
    agent_id: Column(String, ForeignKey("agents.id"))
    name: Column(String, unique=True, nullable=False)
    description: Column(Text)
    code: Column(Text, nullable=False)
    category: Column(String)  # Movement, Perception, Interaction
    created_at: Column(DateTime, default=datetime.utcnow)
```

#### 3. API Endpoints

**`main.py`** - Add routes
```python
@app.post("/api/tools/create")
async def create_tool(request: ToolCreateRequest):
    """Generate new tool from description"""
    # Input: { agent_id, description }
    # Output: { tool_name, code, explanation }

@app.get("/api/tools/agent/{agent_id}")
async def get_agent_tools(agent_id: str):
    """List all tools for agent"""
    # Output: [{ name, description, parameters, code }]

@app.post("/api/agents/deploy")
async def deploy_agent(request: DeployRequest):
    """Deploy agent in world with SSE streaming"""
    # Input: { agent_id, world_id, goal }
    # Output: SSE stream

@app.delete("/api/tools/{tool_name}")
async def delete_tool(tool_name: str):
    """Delete tool"""
```

#### 4. Frontend Components (`frontend/src/components/`)

**`ToolCreator.jsx`**
- Text input for tool description
- "Create Tool" button
- Display generated code (read-only, monospace)
- "Explain Tool" button → show kid-friendly explanation
- Loading state during generation

**`ToolLibrary.jsx`**
- List all tools for current agent
- Show: name, description, parameters
- Color-coded by category (Movement: blue, Perception: green, etc.)
- Delete tool button
- "View Code" toggle

**`AgentRunner.jsx`**
- Input: goal description
- "Deploy Agent" button
- SSE stream display:
  - Agent reasoning text
  - Tool calls with parameters
  - Tool results
  - World state updates (grid changes)
- Pause/Resume/Stop controls
- Real-time world visualization updates

### Testing Requirements (TDD - MANDATORY)

Follow Red-Green-Refactor-Commit cycle for EVERY component:

**Backend Tests:**
```python
# tests/unit/test_tool_generator.py
- test_generate_simple_movement_tool
- test_generate_tool_with_parameters
- test_validate_safe_code
- test_reject_dangerous_imports
- test_syntax_validation

# tests/unit/test_tool_registry.py
- test_discover_tools_from_file
- test_create_mcp_server_with_tools
- test_empty_tools_file

# tests/integration/test_agent_deployment.py
- test_deploy_agent_with_custom_tool
- test_stream_tool_execution
- test_world_state_updates
```

**Frontend Tests:**
```javascript
// components/ToolCreator.test.jsx
- renders input and button
- submits description on button click
- displays generated code
- handles loading and error states

// components/ToolLibrary.test.jsx
- displays list of tools
- color codes by category
- handles delete tool

// components/AgentRunner.test.jsx
- connects to SSE stream
- displays reasoning and tool calls
- updates world visualization
```

### Code Quality Standards (MANDATORY)

**Python:**
- ✅ Full type hints on ALL functions
- ✅ Use Pydantic models for validation
- ✅ Use `logging` (NO print statements)
- ✅ SQLAlchemy ORM (NO raw SQL)
- ✅ Claude Agent SDK (NO direct Anthropic API)
- ✅ XML-wrapped JSON for LLM outputs

**Testing:**
- ✅ Write tests BEFORE implementation
- ✅ Minimum 80% code coverage
- ✅ All tests passing before commit
- ✅ Use pytest-asyncio for async tests

**Commits:**
- ✅ Commit after each Red-Green-Refactor cycle
- ✅ Format: `Add: <feature description>`
- ✅ Include "Tests: N passing" in message

### Safety Validation

Tool code validation checklist:
- ✅ Syntax validation: `ast.parse(code)`
- ✅ Forbidden imports check: `os`, `subprocess`, `sys`, `eval`, `exec`
- ✅ Must have `@tool` decorator
- ✅ Function name matches tool name
- ✅ Returns dict with "content" key

### Success Criteria

When complete, you should be able to:
1. Create tool: "Make my agent move forward 3 steps"
2. See generated Python code with `@tool` decorator
3. View tool in ToolLibrary
4. Deploy agent with goal: "Find the treasure"
5. Watch SSE stream of agent using custom tools
6. See world visualization update in real-time

### File Locations

All code in:
- Backend: `backend/src/`
- Tests: `backend/tests/`
- Frontend: `frontend/src/components/`

### Important Notes

1. **Use Claude Agent SDK**: Import from `claude_agent_sdk`, NOT `anthropic`
2. **Follow TDD strictly**: Red → Green → Refactor → Commit
3. **Type hints mandatory**: Every function needs complete type annotations
4. **Test coverage**: Aim for 80%+ coverage
5. **Logging**: Use `logger.info()`, `logger.error()`, etc.

### Getting Started

1. Start with `ToolGenerator` class and its tests
2. Build `tool_registry.py` for dynamic discovery
3. Add `ToolDB` model and migration
4. Implement API endpoints with SSE streaming
5. Build frontend components
6. Integration test: full flow from description → deployment

Remember: Write tests FIRST, then implement. Commit after each complete cycle.

Good luck! Report back when you have questions or need clarification.