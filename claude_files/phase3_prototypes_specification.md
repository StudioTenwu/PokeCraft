# Phase 3: Teaching Tools - Three Prototype Architectures

**Goal:** Child teaches agent capabilities through natural language → LLM generates tools → Agent uses tools in world

This document specifies three different architectural approaches that will be built in parallel for comparison.

---

## Prototype 1: Direct Code Execution (RestrictedPython)

**Architecture:** LLM generates Python code → Sandboxed interpreter → Agent executes in world

### Backend Components
- `backend/src/tool_generator.py` - LLM-based Python code generation
- `backend/src/tool_executor.py` - RestrictedPython sandbox execution
- `backend/src/world_state.py` - World state management and collision detection

### API Endpoints
```
POST /api/tools/create
GET /api/tools/agent/{agent_id}
POST /api/agents/deploy (SSE stream)
```

### Success Criteria
- Python code generation from natural language
- Safe execution (no `import`, `exec`, file I/O)
- Code transparency ("Explain Code" feature)
- Real-time execution streaming

---

## Prototype 2: Agent SDK Native Tools

**Architecture:** LLM defines tools as JSON schemas → Claude Agent SDK tool use → Execution callbacks

### Backend Components
- `backend/src/tool_definer.py` - JSON tool schema generation
- `backend/src/tool_registry.py` - Predefined safe callback functions

### API Endpoints
```
POST /api/tools/define
POST /api/agents/deploy-sdk (SSE stream)
```

### Success Criteria
- JSON tool schema generation
- Claude SDK tool use integration
- Safest execution (only predefined callbacks)
- Streaming shows agent reasoning

---

## Prototype 3: Hybrid Planning + Primitives

**Architecture:** LLM generates pseudocode plan → Compiler to primitives → Safe execution

### Backend Components
- `backend/src/plan_generator.py` - Pseudocode plan generation
- `backend/src/plan_compiler.py` - Plan validation and compilation
- `backend/src/execution_engine.py` - Primitive execution with limits

### API Endpoints
```
POST /api/plans/generate
POST /api/plans/execute (SSE stream)
```

### Success Criteria
- Pseudocode generation from task descriptions
- Plan compilation with safety validation
- Execution trace visualization
- Loop/timeout protection

---

## Comparison Matrix

| Feature | Prototype 1 | Prototype 2 | Prototype 3 |
|---------|-------------|-------------|-------------|
| **Flexibility** | High (full Python) | Medium (tool schemas) | Medium (pseudocode) |
| **Safety** | RestrictedPython | Predefined callbacks | Compiled primitives |
| **Explainability** | Show code | Show schema | Show plan + trace |
| **Complexity** | High | Low | Medium |

---

## Decision Criteria

After building all three, choose based on:
1. **Safety:** Fewest security risks
2. **Usability:** Best for children (8-12 years)
3. **Pedagogy:** Teaches programming concepts
4. **Maintainability:** Easiest to extend

---

## Implementation Strategy

Each prototype will be built by a separate subagent in parallel using TDD methodology.

**Branches:**
- `prototype-1-direct-code`
- `prototype-2-sdk-tools`
- `prototype-3-hybrid-plan`

**Timeline:** 3 days per prototype (total: 9 days parallel work)

**Final Step:** User testing with target age group to determine winner for MVP.
