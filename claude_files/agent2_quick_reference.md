# Agent 2: Custom Skills Builder - Quick Reference

## At a Glance

**Concept**: Visual workflow builder where users create reusable "skills" by combining tools

**Key Innovation**: Transform agent from tool executor → skill learner

**Tech Stack**: React + ReactFlow + FastAPI

---

## Core Components

### 1. SkillBuilder (Main Container)
```
┌─────────────┬──────────────────┬─────────────┐
│  Skill      │   Workflow       │   Config    │
│  Library    │   Canvas         │   Panel     │
│             │   (ReactFlow)    │             │
└─────────────┴──────────────────┴─────────────┘
                     ↓
            ┌────────────────┐
            │  Skill Tester  │
            │  (collapsible) │
            └────────────────┘
```

### 2. Node Types
- **ToolNode**: Execute a tool (web_search, file_write, etc.)
- **DecisionNode**: If/else branching
- **LoopNode**: Iterate over data
- **MergeNode**: Combine multiple inputs
- **TransformNode**: Modify/format data

### 3. Skill Definition
```json
{
  "metadata": { "name": "...", "description": "..." },
  "triggers": { "keywords": [...], "patterns": [...] },
  "input_parameters": [...],
  "output_format": {...},
  "workflow": {
    "nodes": [...],
    "edges": [...]
  }
}
```

---

## 5 Pre-Built Templates

| Template | Tools | Complexity | Use Case |
|----------|-------|------------|----------|
| 🔍 Web Research | web_search → file_write | ⭐ Beginner | "Research AI safety" |
| 📊 Data Analysis | file_read → calculator → image_gen | ⭐⭐ Intermediate | "Analyze sales data" |
| ✍️ Content Creator | web_search → file_write → file_edit | ⭐⭐ Intermediate | "Write blog post" |
| 💻 Code Helper | web_search → code_exec → file_write | ⭐⭐⭐ Advanced | "Find sorting algorithm" |
| 🗂️ File Organizer | file_read (loop) → file_write (conditional) | ⭐⭐⭐ Advanced | "Organize downloads" |

---

## Visual Workflow Example: Research & Summarize

```
┌──────────────┐
│ 🔍 START     │
│ web_search   │
│ query: ${q}  │
└──────┬───────┘
       │
       │ data flow
       ▼
┌──────────────┐
│ 🔄 Transform │
│ Extract      │
│ title+snippet│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 📝 END       │
│ file_write   │
│ path: ${out} │
└──────────────┘
```

**Execution Flow**:
1. User: "Research quantum computing"
2. Agent: "I recognize my 'Research & Summarize' skill!"
3. Execute: web_search → transform → file_write
4. Result: Summary saved to /tmp/research.md

---

## Agent Perspective View

```
┌─────────────────────────────────────┐
│  🤖 AGENT VIEW                      │
├─────────────────────────────────────┤
│       _____                         │
│      /     \                        │
│     |  ^_^  |                       │
│      \_____/                        │
│                                     │
│  Skills: 7 total                    │
│  ├─ Built-in: 2                     │
│  └─ Custom: 5  ← Growing!           │
│                                     │
│  Most Used:                         │
│  1. 🔍 Research & Summarize (42×)   │
│  2. 📊 Data Analysis (18×)          │
│  3. ✍️ Content Creator (7×)         │
│                                     │
│  Agent's Thinking:                  │
│  "I can now help with 7 different   │
│   types of tasks! Each skill makes  │
│   me more capable."                 │
└─────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- ✅ ReactFlow canvas
- ✅ ToolNode component
- ✅ Drag-and-drop palette
- ✅ Save/load workflow

**Deliverable**: Create 2-3 node workflow

### Phase 2: Execution (Week 3-4)
- ✅ Backend executor
- ✅ Parameter resolution
- ✅ Testing panel
- ✅ Visualization

**Deliverable**: Execute linear workflows

### Phase 3: Advanced Nodes (Week 5-6)
- ✅ Decision/Loop/Merge nodes
- ✅ Complex workflows
- ✅ Validation

**Deliverable**: Branching/looping workflows

### Phase 4: Agent Integration (Week 7-8)
- ✅ Trigger matching
- ✅ Skill library UI
- ✅ Auto-suggestion
- ✅ Agent perspective

**Deliverable**: Agent auto-applies skills

### Phase 5: Polish (Week 9-10)
- ✅ 10+ templates
- ✅ Import/export
- ✅ Documentation
- ✅ Optimization

**Deliverable**: Production-ready

---

## Key Features

### Visual Programming
- Drag tools onto canvas
- Connect with arrows (data flow)
- Configure node parameters
- Test with sample data

### Skill Management
- Save to library
- Reuse across conversations
- Track usage statistics
- Duplicate and modify

### Agent Learning
- Recognizes trigger keywords
- Suggests relevant skills
- Executes automatically
- Shows reasoning

### Testing & Debugging
- Step-by-step execution
- Data flow visualization
- Error handling
- Debug console

---

## Technical Highlights

### Frontend
```jsx
<SkillBuilder>
  <SkillLibrary />
  <WorkflowCanvas>  {/* ReactFlow */}
    <ToolNode />
    <DecisionNode />
    <LoopNode />
  </WorkflowCanvas>
  <SkillConfigPanel />
  <SkillTester />
</SkillBuilder>
```

### Backend
```python
class SkillExecutor:
    async def execute_skill(skill, input_data):
        # Topological sort for execution order
        order = topological_sort(workflow)

        # Execute nodes
        for node in order:
            result = await execute_node(node)
            yield progress_event(node, result)

        return final_result
```

### Data Flow
```
User Message
    ↓
Agent Analyzes → Matches Skill Trigger
    ↓
Load Skill Workflow
    ↓
Execute Nodes (topological order)
    ↓
Stream Progress Events
    ↓
Return Result to Agent
    ↓
Agent Responds to User
```

---

## Example: Complex Workflow with Conditionals

**Scenario**: Data Analysis with Threshold

```
Input: { data_file: "sales.csv", threshold: 1000 }

Workflow:
1. file_read(data_file)
   ↓
2. calculator("SUM(column_B)")
   ↓
3. DECISION: sum > threshold?
   │
   ├─ TRUE (high sales)
   │  ├─ image_gen("High sales chart")
   │  └─ file_write("high_sales_report.md")
   │
   └─ FALSE (low sales)
      ├─ file_write("low_sales_alert.txt")
      └─ Return: { alert: "Below threshold" }
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Skills per user | 5-10 in first week |
| Reuse rate | 15× average |
| Task automation | 80% of repetitive tasks |
| Efficiency gain | 3× for common workflows |
| Success rate | 95% execution success |

---

## Future Enhancements

1. **Skill Marketplace**: Share and import community skills
2. **AI-Assisted Creation**: "Describe what you want, I'll build it"
3. **Versioning**: Track changes, A/B test, rollback
4. **Advanced Nodes**: API calls, databases, webhooks, scheduling
5. **Collaboration**: Multi-user editing, comments, reviews

---

## Quick Start (for Developers)

### 1. Install Dependencies
```bash
# Frontend
cd agent-evolution/frontend
npm install reactflow react-dnd react-dnd-html5-backend

# Backend
cd agent-evolution/backend
pip install fastapi anthropic
```

### 2. Create Basic Skill
```javascript
const skill = {
  id: "my_first_skill",
  metadata: { name: "My First Skill" },
  workflow: {
    nodes: [
      { id: "n1", type: "tool", data: { tool_name: "web_search" } },
      { id: "n2", type: "tool", data: { tool_name: "file_write" } }
    ],
    edges: [
      { source: "n1", target: "n2" }
    ]
  }
};
```

### 3. Execute Skill
```python
executor = SkillExecutor(tool_executor)
async for event in executor.execute_skill(skill, {"query": "test"}):
    print(event)
```

---

## Files to Create

### Frontend Components
- `/frontend/src/components/SkillBuilder.jsx`
- `/frontend/src/components/WorkflowCanvas.jsx`
- `/frontend/src/components/SkillLibrary.jsx`
- `/frontend/src/components/SkillConfigPanel.jsx`
- `/frontend/src/components/SkillTester.jsx`
- `/frontend/src/components/AgentPerspectivePanel.jsx`
- `/frontend/src/components/nodes/ToolNode.jsx`
- `/frontend/src/components/nodes/DecisionNode.jsx`
- `/frontend/src/components/nodes/LoopNode.jsx`

### Backend
- `/backend/skill_executor.py`
- `/backend/skill_matcher.py`
- `/backend/skill_storage.py`

### API Endpoints
- `POST /api/skills` - Create skill
- `GET /api/skills` - List skills
- `GET /api/skills/{id}` - Get skill
- `PUT /api/skills/{id}` - Update skill
- `DELETE /api/skills/{id}` - Delete skill
- `POST /api/skills/test` - Test skill (SSE stream)
- `POST /api/skills/match` - Match message to skills

---

## Summary

**What It Is**: Visual workflow builder for creating reusable agent skills

**How It Works**: Drag tools → Connect nodes → Configure → Test → Save

**Why It Matters**: Transforms agent from one-time executor to capability learner

**User Experience**: "I taught my agent 5 new skills today!"

**Agent Experience**: "I learned 5 new ways to help - I'm becoming more capable!"

**Technical Achievement**: Visual programming meets LLM tool use

---

## Resources

- Full Design Doc: `agent2_custom_skills_builder_design.md`
- Skill Templates: `agent2_skill_templates.json`
- ReactFlow Docs: https://reactflow.dev/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

**Location**: `/Users/wz/Desktop/zPersonalProjects/AICraft/agent-evolution/`

**Status**: Design Complete ✅ | Implementation Ready 🚀
