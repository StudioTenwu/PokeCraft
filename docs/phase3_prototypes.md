# Phase 3: Teaching Tools - Three Prototype Architectures

**Status:** Design Complete - Ready for Implementation
**Date:** 2025-11-10

---

## Overview

Phase 3 implements the teaching tools system where children teach their AI agents new capabilities through natural language. Three different architectural approaches will be prototyped in parallel:

1. **Direct Code Execution** - LLM generates Python → RestrictedPython sandbox
2. **Agent SDK Native Tools** - LLM generates JSON schemas → Predefined callbacks
3. **Hybrid Planning** - LLM generates pseudocode → Compiler → Primitives

---

## Prototype 1: Direct Code Execution

**Branch:** `prototype-1-direct-code`

### Architecture
```
Child Description → Claude → Python Code → AST Validation → RestrictedPython → World State Update
```

### Implementation Files
- `backend/src/tool_generator.py` - Code generation with safety validation
- `backend/src/tool_executor.py` - Sandboxed execution engine
- `backend/src/world_state.py` - World state management
- `frontend/src/components/ToolCreator.jsx` - Tool creation UI
- `frontend/src/components/ToolLibrary.jsx` - Tool management
- `frontend/src/components/AgentRunner.jsx` - Execution visualization

### Database Schema
```sql
CREATE TABLE tools (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    category TEXT,  -- Movement, Perception, Interaction
    description TEXT,
    created_at DATETIME
)
```

### Safety Measures
- AST parsing to detect dangerous imports
- Whitelist of allowed builtins: `len`, `range`, `enumerate`, `int`, `str`
- Whitelist of world API methods
- 5-second timeout per tool execution
- Maximum recursion depth: 10
- No file I/O, no network access, no subprocess

---

## Prototype 2: Agent SDK Native Tools

**Branch:** `prototype-2-sdk-tools`

### Architecture
```
Child Description → Claude → JSON Tool Schema → Agent SDK → Callback Registry → Execution
```

### Implementation Files
- `backend/src/tool_definer.py` - Schema generation
- `backend/src/tool_registry.py` - Callback mapping
- `backend/src/agent_sdk_runner.py` - Agent SDK integration

### Example Tool Definition
```json
{
  "name": "move_forward",
  "description": "Move the agent forward by N steps in the current direction",
  "input_schema": {
    "type": "object",
    "properties": {
      "steps": {
        "type": "integer",
        "description": "Number of steps to move (1-10)",
        "minimum": 1,
        "maximum": 10
      }
    },
    "required": ["steps"]
  }
}
```

### Predefined Callbacks
```python
# All implementations hardcoded for safety
TOOL_REGISTRY = {
    "move_forward": move_forward_impl,
    "turn_left": turn_left_impl,
    "turn_right": turn_right_impl,
    "scan_area": scan_area_impl,
    "pick_up": pick_up_impl,
}
```

---

## Prototype 3: Hybrid Planning + Primitives

**Branch:** `prototype-3-hybrid-plan`

### Architecture
```
Task Description → Claude → Pseudocode Plan → Compiler → Primitive Sequence → Execution Engine
```

### Implementation Files
- `backend/src/plan_generator.py` - Pseudocode generation
- `backend/src/plan_compiler.py` - AST parsing and compilation
- `backend/src/execution_engine.py` - Step-by-step execution
- `frontend/src/components/PlanVisualizer.jsx` - Plan display
- `frontend/src/components/ExecutionDebugger.jsx` - Step-through debugger

### Example Pseudocode
```
PLAN find_treasure:
  SET treasure_found = FALSE
  WHILE treasure_found == FALSE AND steps < 100:
    IF SCAN_AHEAD == "treasure":
      MOVE_FORWARD
      PICKUP
      SET treasure_found = TRUE
    ELIF SCAN_LEFT == "treasure":
      TURN_LEFT
    ELIF SCAN_RIGHT == "treasure":
      TURN_RIGHT
    ELSE:
      MOVE_FORWARD
```

### Primitive Set
- `MOVE_FORWARD` - Move one cell forward
- `TURN_LEFT` - Rotate 90° left
- `TURN_RIGHT` - Rotate 90° right
- `SCAN_AHEAD` - Check cell in front
- `SCAN_LEFT` - Check cell to left
- `SCAN_RIGHT` - Check cell to right
- `PICKUP` - Pick up item at current position

---

## Comparison Matrix

| Aspect | Prototype 1 | Prototype 2 | Prototype 3 |
|--------|-------------|-------------|-------------|
| **Flexibility** | ⭐⭐⭐⭐⭐ Full Python | ⭐⭐⭐ Predefined schemas | ⭐⭐⭐⭐ Pseudocode DSL |
| **Safety** | ⭐⭐⭐ Sandbox + validation | ⭐⭐⭐⭐⭐ Only callbacks | ⭐⭐⭐⭐ Compiled primitives |
| **Explainability** | ⭐⭐⭐⭐ Show Python code | ⭐⭐⭐ Show JSON schema | ⭐⭐⭐⭐⭐ Plan + trace |
| **Child Editing** | ⭐⭐⭐⭐⭐ Full code edit | ⭐⭐ Parameter edit only | ⭐⭐⭐⭐ Pseudocode edit |
| **Performance** | ⭐⭐⭐⭐⭐ Direct execution | ⭐⭐⭐ SDK overhead | ⭐⭐⭐⭐ Compiled |
| **Implementation** | ⭐⭐ Complex sandbox | ⭐⭐⭐⭐⭐ Leverage SDK | ⭐⭐⭐ Need compiler |
| **Pedagogy** | ⭐⭐⭐⭐⭐ Real Python | ⭐⭐ Abstract schemas | ⭐⭐⭐⭐ Structured thinking |

---

## TDD Testing Strategy

Each prototype must implement:

### Unit Tests
- Tool/schema/plan generation from various descriptions
- Safety validation (reject malicious code/plans)
- Execution correctness (world state updates)
- Error handling (invalid inputs, timeouts)

### Integration Tests
- Full flow: description → generation → execution → result
- SSE streaming during agent deployment
- Frontend-backend communication

### End-to-End Tests
- Create agent → create world → teach tool → deploy → verify success
- Complex multi-tool scenarios
- Edge cases (empty world, obstacles, etc.)

---

## Implementation Plan

### Parallel Development (3 subagents)

1. **Subagent 1:** Prototype 1 (Direct Code)
   - Branch: `prototype-1-direct-code`
   - Timeline: 3 days
   - Dependencies: RestrictedPython, AST analysis

2. **Subagent 2:** Prototype 2 (SDK Tools)
   - Branch: `prototype-2-sdk-tools`
   - Timeline: 3 days
   - Dependencies: Claude Agent SDK integration

3. **Subagent 3:** Prototype 3 (Hybrid)
   - Branch: `prototype-3-hybrid-plan`
   - Timeline: 3 days
   - Dependencies: Custom pseudocode parser

### Evaluation Phase (After completion)

1. **Security Audit:** Test each with malicious inputs
2. **Usability Testing:** Test with target age group (8-12 years)
3. **Performance Benchmarking:** Execution speed comparison
4. **Code Review:** Maintainability assessment

### Decision Criteria

Choose MVP winner based on:
1. **Safety** (30%) - Fewest vulnerabilities
2. **Usability** (30%) - Children understand and enjoy
3. **Pedagogy** (20%) - Teaches programming concepts
4. **Maintainability** (20%) - Easy to extend with new tools

---

## Next Steps

1. Create feature branches for each prototype
2. Spawn three subagents with detailed specifications
3. Monitor parallel development
4. Merge completed prototypes for comparison
5. Conduct user testing
6. Select winner for MVP

---

**Ready for implementation.** Each prototype has complete specifications, TDD approach, and success criteria defined.
