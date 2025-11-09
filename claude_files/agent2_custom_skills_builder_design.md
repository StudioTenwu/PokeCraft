# Agent 2: Custom Skills Builder - Complete Design Document

## Executive Summary

The Custom Skills Builder is an interactive visual system that empowers users to create reusable agent workflows by combining tools into custom "skills". Using a drag-and-drop node-based editor inspired by Scratch and Node-RED, users can compose complex multi-step behaviors from simple tool primitives, complete with conditional logic, loops, and data transformations.

**Core Innovation**: Transform the agent from a tool executor into a skill learner - users teach the agent new capabilities that become part of its permanent repertoire.

---

## 1. Design Philosophy

### 1.1 Core Concept: Skills = Reusable Tool Workflows

A "skill" is a saved pattern of tool usage that the agent can recognize and execute automatically:

```
Traditional Approach:
User: "Research AI papers and create a summary document"
Agent: *executes tools ad-hoc each time*

Skills Approach:
User: "Research AI papers and create a summary document"
Agent: "I recognize this as my 'Research & Summarize' skill! Let me use that workflow."
Agent: *executes pre-configured tool chain: web_search → file_write → file_edit*
```

### 1.2 First-Person Agent Experience

The agent gains "abilities" through skills, similar to how video game characters gain new moves:

```
┌─────────────────────────────────────┐
│  🤖 Agent's Skill Library           │
├─────────────────────────────────────┤
│  Built-in Skills: (2)               │
│  ✅ Basic conversation              │
│  ✅ Simple calculation              │
│                                     │
│  Custom Skills: (3) ← Growing!      │
│  ✨ Research & Summarize            │
│     Tools: web_search → file_write  │
│     When: User asks for research    │
│                                     │
│  ✨ Data Analysis Pipeline          │
│     Tools: file_read → calculator   │
│            → chart_create           │
│     When: User provides data file   │
│                                     │
│  ✨ Content Creator                 │
│     Tools: web_search → text_gen    │
│            → grammar_check          │
│     When: User needs written content│
│                                     │
│  Agent Thinking:                    │
│  "I now have 5 total skills! Each   │
│   new skill makes me more capable." │
└─────────────────────────────────────┘
```

### 1.3 Visual Programming Paradigm

Skills are created using a visual node-based editor:

- **Nodes**: Represent tools, decisions, loops, transforms
- **Edges**: Represent data flow between operations
- **Canvas**: Drag-and-drop workspace for composing workflows
- **Live Preview**: See data flowing through the graph during testing

---

## 2. System Architecture

### 2.1 Component Hierarchy

```
App.jsx
├── SkillBuilder (main container)
│   ├── SkillLibrary (left sidebar)
│   │   ├── SkillList
│   │   │   ├── SkillCard (built-in)
│   │   │   └── SkillCard (custom) x N
│   │   ├── NewSkillButton
│   │   └── ImportTemplateButton
│   │
│   ├── WorkflowCanvas (center - main editor)
│   │   ├── ReactFlow canvas
│   │   ├── ToolPalette (drag source)
│   │   ├── NodeTypes:
│   │   │   ├── ToolNode (execute tool)
│   │   │   ├── DecisionNode (if/else)
│   │   │   ├── LoopNode (repeat)
│   │   │   ├── MergeNode (combine data)
│   │   │   └── TransformNode (modify data)
│   │   ├── EdgeTypes:
│   │   │   ├── DataEdge (normal flow)
│   │   │   ├── ConditionalEdge (if branch)
│   │   │   └── LoopEdge (iteration)
│   │   └── MiniMap
│   │
│   ├── SkillConfigPanel (right sidebar)
│   │   ├── SkillMetadata
│   │   │   ├── Name input
│   │   │   ├── Description textarea
│   │   │   └── Trigger conditions
│   │   ├── InputParameters
│   │   │   └── ParameterEditor x N
│   │   ├── OutputFormat
│   │   │   └── FormatSelector
│   │   └── ExampleUseCases
│   │       └── ExampleCard x N
│   │
│   └── SkillTester (bottom panel - collapsible)
│       ├── TestInputForm
│       ├── ExecutionVisualizer
│       │   ├── StepList
│       │   │   └── StepCard (with status)
│       │   └── DataFlowAnimation
│       ├── ResultDisplay
│       └── DebugConsole
│
└── AgentPerspectivePanel (floating)
    ├── AgentAvatar
    ├── SkillCount
    ├── ThinkingProcess
    └── CapabilityTree
```

### 2.2 Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Skill Creation Flow                     │
└──────────────────────────────────────────────────────────────┘

1. User drags tools onto canvas
   ↓
2. User connects nodes with edges
   ↓
3. User configures node parameters
   ↓
4. User sets skill metadata (name, description, triggers)
   ↓
5. User tests skill with sample input
   ↓
6. System validates workflow:
   - All required inputs connected
   - No circular dependencies (except loops)
   - Type compatibility between nodes
   ↓
7. User saves skill
   ↓
8. Skill added to agent's library
   ↓
9. Agent can now recognize and use skill

┌──────────────────────────────────────────────────────────────┐
│                      Skill Execution Flow                     │
└──────────────────────────────────────────────────────────────┘

1. User sends message to agent
   ↓
2. Agent analyzes message and available skills
   ↓
3. Agent matches message to skill trigger
   ↓
4. Agent requests skill execution from SkillExecutor
   ↓
5. SkillExecutor loads workflow definition
   ↓
6. Executor processes nodes in topological order:
   ├─ Execute tool nodes
   ├─ Evaluate decision nodes
   ├─ Run loop nodes
   └─ Apply transform nodes
   ↓
7. Each step emits events (for visualization)
   ↓
8. Final result returned to agent
   ↓
9. Agent incorporates result into response
```

---

## 3. Skill Definition Schema

### 3.1 Skill JSON Structure

```json
{
  "id": "research_and_summarize_v1",
  "version": "1.0.0",
  "metadata": {
    "name": "Research & Summarize",
    "description": "Search web for information and create a structured summary document",
    "author": "user",
    "created_at": "2025-11-09T00:00:00Z",
    "updated_at": "2025-11-09T00:00:00Z",
    "tags": ["research", "writing", "automation"],
    "category": "content_creation"
  },

  "triggers": {
    "keywords": ["research", "summarize", "investigate"],
    "patterns": [
      "research * and create summary",
      "look up * and write about it"
    ],
    "confidence_threshold": 0.7
  },

  "input_parameters": [
    {
      "name": "query",
      "type": "string",
      "description": "The research topic or question",
      "required": true,
      "default": null
    },
    {
      "name": "max_sources",
      "type": "integer",
      "description": "Maximum number of sources to search",
      "required": false,
      "default": 5
    }
  ],

  "output_format": {
    "type": "object",
    "properties": {
      "summary_file": {
        "type": "string",
        "description": "Path to created summary file"
      },
      "sources_count": {
        "type": "integer",
        "description": "Number of sources consulted"
      },
      "key_findings": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  },

  "workflow": {
    "nodes": [
      {
        "id": "node_1",
        "type": "tool",
        "position": {"x": 100, "y": 100},
        "data": {
          "tool_name": "web_search",
          "parameters": {
            "query": "${input.query}"
          }
        }
      },
      {
        "id": "node_2",
        "type": "transform",
        "position": {"x": 300, "y": 100},
        "data": {
          "operation": "extract_fields",
          "config": {
            "fields": ["title", "snippet"],
            "source": "${node_1.results}"
          }
        }
      },
      {
        "id": "node_3",
        "type": "tool",
        "position": {"x": 500, "y": 100},
        "data": {
          "tool_name": "file_write",
          "parameters": {
            "path": "/tmp/research_summary.md",
            "content": "${node_2.formatted_text}"
          }
        }
      }
    ],

    "edges": [
      {
        "id": "edge_1",
        "source": "node_1",
        "target": "node_2",
        "type": "data",
        "data": {
          "source_handle": "output",
          "target_handle": "input"
        }
      },
      {
        "id": "edge_2",
        "source": "node_2",
        "target": "node_3",
        "type": "data",
        "data": {
          "source_handle": "output",
          "target_handle": "input"
        }
      }
    ],

    "entry_point": "node_1",
    "exit_points": ["node_3"]
  },

  "examples": [
    {
      "description": "Research AI safety",
      "input": {
        "query": "AI safety research 2025",
        "max_sources": 3
      },
      "expected_output": {
        "summary_file": "/tmp/research_summary.md",
        "sources_count": 3,
        "key_findings": [
          "Finding 1 from source A",
          "Finding 2 from source B"
        ]
      }
    }
  ],

  "statistics": {
    "times_used": 42,
    "success_rate": 0.95,
    "avg_execution_time_ms": 2500,
    "last_used": "2025-11-08T15:30:00Z"
  }
}
```

### 3.2 Node Types Specification

#### ToolNode
```json
{
  "type": "tool",
  "data": {
    "tool_name": "web_search",
    "parameters": {
      "query": "${input.query}"
    },
    "error_handling": {
      "retry_count": 3,
      "fallback_node": "node_fallback_1"
    }
  }
}
```

#### DecisionNode
```json
{
  "type": "decision",
  "data": {
    "condition": {
      "type": "expression",
      "expression": "${node_1.success} === true"
    },
    "branches": {
      "true": "node_2",
      "false": "node_3"
    }
  }
}
```

#### LoopNode
```json
{
  "type": "loop",
  "data": {
    "iteration_source": "${node_1.results}",
    "loop_variable": "item",
    "body_nodes": ["node_2", "node_3"],
    "max_iterations": 10,
    "collect_results": true
  }
}
```

#### MergeNode
```json
{
  "type": "merge",
  "data": {
    "inputs": ["${node_1.output}", "${node_2.output}"],
    "strategy": "concatenate", // or "merge_objects", "combine_arrays"
    "output_name": "merged_data"
  }
}
```

#### TransformNode
```json
{
  "type": "transform",
  "data": {
    "operation": "extract_fields",
    "config": {
      "fields": ["title", "url"],
      "source": "${node_1.results}",
      "format": "markdown"
    }
  }
}
```

---

## 4. User Interface Design

### 4.1 Main Workflow Canvas

```
┌────────────────────────────────────────────────────────────────────┐
│  SkillBuilder: "Research & Summarize"                    [Test] [Save] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  TOOL PALETTE (draggable)                                          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 🔍 web_search  📝 file_write  📖 file_read  🔢 calculator│    │
│  │ 🎨 image_gen   ⚙️ code_exec  🔀 if/else  🔁 loop        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  CANVAS (node editor)                                              │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │    ┌──────────────┐                                     │    │
│  │    │ 🔍 START     │                                     │    │
│  │    │ web_search   │                                     │    │
│  │    │ query: ${q}  │                                     │    │
│  │    └──────┬───────┘                                     │    │
│  │           │                                              │    │
│  │           ▼                                              │    │
│  │    ┌──────────────┐                                     │    │
│  │    │ 🔄 Transform │                                     │    │
│  │    │ Extract      │                                     │    │
│  │    │ title,snippet│                                     │    │
│  │    └──────┬───────┘                                     │    │
│  │           │                                              │    │
│  │           ▼                                              │    │
│  │    ┌──────────────┐                                     │    │
│  │    │ 📝 END       │                                     │    │
│  │    │ file_write   │                                     │    │
│  │    │ path: ${out} │                                     │    │
│  │    └──────────────┘                                     │    │
│  │                                                          │    │
│  │                                                          │    │
│  │  [Mini Map]                                             │    │
│  │  ┌─────┐                                                │    │
│  │  │ ● │ │  ← You are here                               │    │
│  │  │  ●  │                                                │    │
│  │  │   ● │                                                │    │
│  │  └─────┘                                                │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Node Design (ToolNode Example)

```
┌─────────────────────────────────┐
│ 🔍 web_search          [⚙️] [×] │  ← Header (icon, name, settings, delete)
├─────────────────────────────────┤
│ ◉ input                         │  ← Input handle
│   query: "${input.query}"       │  ← Parameters
│   max_results: 5                │
├─────────────────────────────────┤
│ Status: ⚪ Not executed          │  ← Execution status
│ Result: —                       │  ← Last result preview
├─────────────────────────────────┤
│                            ◉    │  ← Output handle
│                          output │
└─────────────────────────────────┘
```

Status indicators:
- ⚪ Not executed
- 🔵 Running
- ✅ Success
- ❌ Error
- ⏸️ Waiting

### 4.3 Skill Configuration Panel

```
┌────────────────────────────────────┐
│  SKILL CONFIGURATION               │
├────────────────────────────────────┤
│                                    │
│  Basic Info                        │
│  ┌──────────────────────────────┐ │
│  │ Name: Research & Summarize   │ │
│  │                              │ │
│  │ Description:                 │ │
│  │ Search web for information   │ │
│  │ and create a structured      │ │
│  │ summary document             │ │
│  └──────────────────────────────┘ │
│                                    │
│  Triggers                          │
│  ┌──────────────────────────────┐ │
│  │ Keywords:                    │ │
│  │ [research] [summarize] [+]   │ │
│  │                              │ │
│  │ Patterns:                    │ │
│  │ • "research * and summarize" │ │
│  │ • "investigate *"       [+]  │ │
│  └──────────────────────────────┘ │
│                                    │
│  Input Parameters                  │
│  ┌──────────────────────────────┐ │
│  │ 1. query (string, required)  │ │
│  │    The research topic        │ │
│  │                              │ │
│  │ 2. max_sources (int)         │ │
│  │    Default: 5           [Edit]│ │
│  │                         [+]  │ │
│  └──────────────────────────────┘ │
│                                    │
│  Output Format                     │
│  ┌──────────────────────────────┐ │
│  │ ○ Text                       │ │
│  │ ● Object (structured)        │ │
│  │ ○ File path                  │ │
│  │ ○ Custom...                  │ │
│  └──────────────────────────────┘ │
│                                    │
│  Example Use Cases                 │
│  ┌──────────────────────────────┐ │
│  │ "Research AI safety"         │ │
│  │ Expected: 3 sources, summary │ │
│  │                         [+]  │ │
│  └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

### 4.4 Skill Testing Panel

```
┌──────────────────────────────────────────────────────────────────┐
│  SKILL TESTER                                    [Collapse] [×]  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Test Input                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ query: "AI safety research 2025"                           │ │
│  │ max_sources: 3                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                 [Run Test]       │
│                                                                  │
│  Execution Timeline                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ✅ 1. web_search                            [120ms]        │ │
│  │    → Found 3 results                                       │ │
│  │                                                            │ │
│  │ ✅ 2. transform (extract_fields)            [15ms]         │ │
│  │    → Extracted 6 fields                                    │ │
│  │                                                            │ │
│  │ 🔵 3. file_write                            [running...]   │ │
│  │    → Writing to /tmp/research_summary.md                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Data Flow Visualization                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  query: "AI safety research 2025"                          │ │
│  │     ↓                                                      │ │
│  │  web_search → {results: [...]}  ← 3 items                 │ │
│  │     ↓                                                      │ │
│  │  transform → {formatted_text: "..."}  ← 500 chars         │ │
│  │     ↓                                                      │ │
│  │  file_write → {success: true, path: "/tmp/..."}           │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Final Result                                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ {                                                          │ │
│  │   "summary_file": "/tmp/research_summary.md",              │ │
│  │   "sources_count": 3,                                      │ │
│  │   "key_findings": [                                        │ │
│  │     "AI safety focuses on alignment",                      │ │
│  │     "Current research emphasizes..."                       │ │
│  │   ]                                                        │ │
│  │ }                                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Debug Console                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ [INFO] Starting execution...                               │ │
│  │ [DEBUG] node_1: web_search with query "AI safety..."      │ │
│  │ [INFO] node_1 completed in 120ms                          │ │
│  │ [DEBUG] node_2: transform with 3 items                    │ │
│  │ [INFO] node_2 completed in 15ms                           │ │
│  │ [DEBUG] node_3: file_write to /tmp/research_summary.md    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4.5 Skill Library Panel

```
┌────────────────────────────────────┐
│  SKILL LIBRARY         [+] [Import]│
├────────────────────────────────────┤
│  Search: [_______________] 🔍      │
│                                    │
│  Built-in Skills (2)               │
│  ┌──────────────────────────────┐ │
│  │ 💬 Basic Conversation        │ │
│  │ Always active                │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 🔢 Simple Calculation        │ │
│  │ Always active                │ │
│  └──────────────────────────────┘ │
│                                    │
│  Custom Skills (5)                 │
│  ┌──────────────────────────────┐ │
│  │ 🔍 Research & Summarize ★    │ │
│  │ Used 42 times | 95% success  │ │
│  │ [Edit] [Delete] [Duplicate]  │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 📊 Data Analysis Pipeline    │ │
│  │ Used 18 times | 88% success  │ │
│  │ [Edit] [Delete] [Duplicate]  │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ ✍️ Content Creator           │ │
│  │ Used 7 times | 100% success  │ │
│  │ [Edit] [Delete] [Duplicate]  │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 🗂️ File Organizer            │ │
│  │ Used 3 times | 67% success   │ │
│  │ [Edit] [Delete] [Duplicate]  │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 📧 Email Responder           │ │
│  │ Never used                   │ │
│  │ [Edit] [Delete] [Duplicate]  │ │
│  └──────────────────────────────┘ │
│                                    │
│  Templates (10)                    │
│  ┌──────────────────────────────┐ │
│  │ 📖 Web Research              │ │
│  │ [Preview] [Use Template]     │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ 📈 Code Helper               │ │
│  │ [Preview] [Use Template]     │ │
│  └──────────────────────────────┘ │
│  ...                               │
│                                    │
└────────────────────────────────────┘
```

### 4.6 Agent Perspective Panel (Floating)

```
┌─────────────────────────────────────┐
│  🤖 AGENT VIEW                [−] [×]│
├─────────────────────────────────────┤
│                                     │
│       _____                         │
│      /     \                        │
│     |  ^_^  |  ← Agent Avatar       │
│      \_____/                        │
│        | |                          │
│       /   \                         │
│                                     │
│  Current Capabilities               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                     │
│  Skills: 7 total                    │
│  ├─ Built-in: 2                     │
│  └─ Custom: 5                       │
│                                     │
│  Most Used:                         │
│  1. 🔍 Research & Summarize (42×)   │
│  2. 📊 Data Analysis (18×)          │
│  3. ✍️ Content Creator (7×)         │
│                                     │
│  Recent Additions:                  │
│  ✨ Email Responder (just now!)     │
│                                     │
│  Agent's Thinking:                  │
│  ┌───────────────────────────────┐ │
│  │ "I can now help with 7        │ │
│  │  different types of tasks!    │ │
│  │  When users ask me to         │ │
│  │  research something, I        │ │
│  │  automatically know to use    │ │
│  │  my Research & Summarize      │ │
│  │  skill. Each skill makes      │ │
│  │  me more useful!"             │ │
│  └───────────────────────────────┘ │
│                                     │
│  Capability Tree                    │
│  ┌───────────────────────────────┐ │
│  │ Information Gathering         │ │
│  │ ├─ Web search                 │ │
│  │ ├─ File reading               │ │
│  │ └─ 🔍 Research & Summarize    │ │
│  │                               │ │
│  │ Content Creation              │ │
│  │ ├─ Text generation            │ │
│  │ ├─ File writing               │ │
│  │ └─ ✍️ Content Creator         │ │
│  │                               │ │
│  │ Data Processing               │ │
│  │ ├─ Calculations               │ │
│  │ ├─ File editing               │ │
│  │ └─ 📊 Data Analysis Pipeline  │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Pre-Built Skill Templates

### Template 1: Web Research

**Name**: Web Research
**Description**: Search the web for a topic and compile findings
**Tools Used**: web_search → file_write

**Workflow**:
```
1. web_search(query: ${query})
   ↓
2. file_write(path: "/tmp/research.md", content: ${results})
```

**Use Case**: "Research quantum computing and save findings"

---

### Template 2: Data Analysis Pipeline

**Name**: Data Analysis Pipeline
**Description**: Read a data file, perform calculations, and create visualization
**Tools Used**: file_read → calculator → image_gen

**Workflow**:
```
1. file_read(path: ${data_file})
   ↓
2. calculator(expression: ${analysis_formula})
   ↓
3. image_gen(prompt: "Chart showing ${results}")
```

**Use Case**: "Analyze sales data and create chart"

---

### Template 3: Content Creator

**Name**: Content Creator
**Description**: Research a topic and generate polished content
**Tools Used**: web_search → file_write → file_edit

**Workflow**:
```
1. web_search(query: ${topic})
   ↓
2. file_write(path: "/tmp/draft.md", content: ${search_results})
   ↓
3. file_edit(path: "/tmp/draft.md", changes: "Format as blog post")
```

**Use Case**: "Create a blog post about AI trends"

---

### Template 4: Code Helper

**Name**: Code Helper
**Description**: Search for code examples and execute tests
**Tools Used**: web_search → code_exec → file_write

**Workflow**:
```
1. web_search(query: "python ${topic} example")
   ↓
2. code_exec(code: ${extracted_code})
   ↓
3. file_write(path: "/tmp/example.py", content: ${verified_code})
```

**Use Case**: "Find and test a sorting algorithm"

---

### Template 5: Smart File Organizer

**Name**: Smart File Organizer
**Description**: Read multiple files and organize by content
**Tools Used**: file_read (loop) → file_write (conditional)

**Workflow**:
```
1. Loop over file_list:
   ├─ file_read(path: ${file})
   ├─ Analyze content type
   └─ Decision: content_type
       ├─ If "code" → file_write("/organized/code/${file}")
       ├─ If "text" → file_write("/organized/docs/${file}")
       └─ Else → file_write("/organized/misc/${file}")
```

**Use Case**: "Organize my downloads folder by file type"

---

## 6. Technical Implementation

### 6.1 Frontend Components

#### SkillBuilder.jsx (Main Container)
```jsx
import React, { useState } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import SkillLibrary from './SkillLibrary';
import WorkflowCanvas from './WorkflowCanvas';
import SkillConfigPanel from './SkillConfigPanel';
import SkillTester from './SkillTester';
import AgentPerspectivePanel from './AgentPerspectivePanel';

export default function SkillBuilder() {
  const [currentSkill, setCurrentSkill] = useState(null);
  const [skills, setSkills] = useState([]);
  const [isTestPanelOpen, setIsTestPanelOpen] = useState(false);

  const handleSaveSkill = (skillDefinition) => {
    // Validate workflow
    if (!validateSkillWorkflow(skillDefinition)) {
      alert("Invalid workflow configuration");
      return;
    }

    // Save to backend
    fetch('/api/skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(skillDefinition)
    })
    .then(res => res.json())
    .then(saved => {
      setSkills([...skills, saved]);
      alert(`Skill "${saved.metadata.name}" saved!`);
    });
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="flex h-screen bg-gray-50">
        {/* Left: Skill Library */}
        <div className="w-80 border-r bg-white">
          <SkillLibrary
            skills={skills}
            onSelectSkill={setCurrentSkill}
            onNewSkill={() => setCurrentSkill(createEmptySkill())}
          />
        </div>

        {/* Center: Workflow Canvas */}
        <div className="flex-1 flex flex-col">
          <WorkflowCanvas
            skill={currentSkill}
            onUpdateSkill={setCurrentSkill}
          />

          {/* Bottom: Skill Tester (collapsible) */}
          {isTestPanelOpen && (
            <SkillTester
              skill={currentSkill}
              onClose={() => setIsTestPanelOpen(false)}
            />
          )}
        </div>

        {/* Right: Config Panel */}
        <div className="w-96 border-l bg-white">
          <SkillConfigPanel
            skill={currentSkill}
            onUpdateSkill={setCurrentSkill}
            onSave={handleSaveSkill}
            onTest={() => setIsTestPanelOpen(true)}
          />
        </div>

        {/* Floating: Agent Perspective */}
        <AgentPerspectivePanel skills={skills} />
      </div>
    </DndProvider>
  );
}
```

#### WorkflowCanvas.jsx (ReactFlow Integration)
```jsx
import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

import ToolNode from './nodes/ToolNode';
import DecisionNode from './nodes/DecisionNode';
import LoopNode from './nodes/LoopNode';
import MergeNode from './nodes/MergeNode';
import TransformNode from './nodes/TransformNode';
import ToolPalette from './ToolPalette';

const nodeTypes = {
  tool: ToolNode,
  decision: DecisionNode,
  loop: LoopNode,
  merge: MergeNode,
  transform: TransformNode,
};

export default function WorkflowCanvas({ skill, onUpdateSkill }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(skill?.workflow?.nodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(skill?.workflow?.edges || []);

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');

    const position = {
      x: event.clientX,
      y: event.clientY,
    };

    const newNode = {
      id: `node_${Date.now()}`,
      type,
      position,
      data: getDefaultNodeData(type),
    };

    setNodes((nds) => nds.concat(newNode));
  }, [setNodes]);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Update parent skill when nodes/edges change
  React.useEffect(() => {
    if (skill) {
      onUpdateSkill({
        ...skill,
        workflow: {
          ...skill.workflow,
          nodes,
          edges,
        },
      });
    }
  }, [nodes, edges]);

  return (
    <div className="flex flex-col h-full">
      {/* Tool Palette */}
      <ToolPalette />

      {/* ReactFlow Canvas */}
      <div className="flex-1" onDrop={onDrop} onDragOver={onDragOver}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}

function getDefaultNodeData(type) {
  switch (type) {
    case 'tool':
      return { tool_name: 'web_search', parameters: {} };
    case 'decision':
      return { condition: '', branches: { true: null, false: null } };
    case 'loop':
      return { iteration_source: '', loop_variable: 'item', body_nodes: [] };
    case 'merge':
      return { inputs: [], strategy: 'concatenate' };
    case 'transform':
      return { operation: 'extract_fields', config: {} };
    default:
      return {};
  }
}
```

#### nodes/ToolNode.jsx
```jsx
import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';

const TOOL_ICONS = {
  web_search: '🔍',
  file_write: '📝',
  file_read: '📖',
  calculator: '🔢',
  image_gen: '🎨',
  code_exec: '⚙️',
};

export default function ToolNode({ data, selected }) {
  const [showSettings, setShowSettings] = useState(false);
  const icon = TOOL_ICONS[data.tool_name] || '🔧';

  return (
    <div
      className={`
        bg-white rounded-lg border-2 shadow-lg min-w-[200px]
        ${selected ? 'border-blue-500' : 'border-gray-300'}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-t-lg border-b">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <span className="font-bold text-gray-900">{data.tool_name}</span>
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-1 hover:bg-gray-200 rounded"
          >
            ⚙️
          </button>
          <button className="p-1 hover:bg-red-100 rounded text-red-600">
            ×
          </button>
        </div>
      </div>

      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-blue-500"
      />

      {/* Parameters */}
      <div className="p-3 text-sm">
        {Object.entries(data.parameters || {}).map(([key, value]) => (
          <div key={key} className="mb-2">
            <span className="text-gray-600">{key}:</span>{' '}
            <span className="font-mono text-xs">{String(value)}</span>
          </div>
        ))}
      </div>

      {/* Status */}
      <div className="p-2 bg-gray-50 rounded-b-lg border-t text-xs">
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Status:</span>
          <span className="flex items-center gap-1">
            ⚪ Not executed
          </span>
        </div>
      </div>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 bg-green-500"
      />

      {/* Settings Modal */}
      {showSettings && (
        <div className="absolute top-full mt-2 left-0 z-50 bg-white border-2 border-gray-300 rounded-lg shadow-xl p-4 w-80">
          <h3 className="font-bold mb-3">Node Settings</h3>
          {/* Parameter editors */}
          <button
            onClick={() => setShowSettings(false)}
            className="mt-3 w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Done
          </button>
        </div>
      )}
    </div>
  );
}
```

#### SkillTester.jsx
```jsx
import React, { useState } from 'react';

export default function SkillTester({ skill, onClose }) {
  const [testInput, setTestInput] = useState({});
  const [execution, setExecution] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const runTest = async () => {
    setIsRunning(true);
    setExecution({ steps: [], status: 'running' });

    try {
      const response = await fetch('/api/skills/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skill_id: skill.id,
          test_input: testInput,
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const events = chunk.split('\n\n').filter(Boolean);

        for (const event of events) {
          if (event.startsWith('data: ')) {
            const data = JSON.parse(event.slice(6));

            setExecution(prev => ({
              ...prev,
              steps: [...prev.steps, data],
            }));
          }
        }
      }

      setExecution(prev => ({ ...prev, status: 'completed' }));
    } catch (error) {
      setExecution(prev => ({ ...prev, status: 'error', error: error.message }));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="border-t bg-white h-96 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-bold">Skill Tester</h2>
        <div className="flex gap-2">
          <button
            onClick={runTest}
            disabled={isRunning}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
          >
            {isRunning ? 'Running...' : 'Run Test'}
          </button>
          <button onClick={onClose} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
            Close
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {/* Test Input Form */}
        <div className="mb-6">
          <h3 className="font-bold mb-2">Test Input</h3>
          <div className="space-y-2">
            {skill?.input_parameters?.map(param => (
              <div key={param.name}>
                <label className="block text-sm font-medium text-gray-700">
                  {param.name} {param.required && <span className="text-red-500">*</span>}
                </label>
                <input
                  type={param.type === 'integer' ? 'number' : 'text'}
                  value={testInput[param.name] || ''}
                  onChange={(e) => setTestInput({
                    ...testInput,
                    [param.name]: e.target.value,
                  })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                  placeholder={param.description}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Execution Timeline */}
        {execution && (
          <div>
            <h3 className="font-bold mb-2">Execution Timeline</h3>
            <div className="space-y-2">
              {execution.steps.map((step, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                  <span className="text-2xl">
                    {step.status === 'success' ? '✅' :
                     step.status === 'error' ? '❌' :
                     step.status === 'running' ? '🔵' : '⚪'}
                  </span>
                  <div className="flex-1">
                    <div className="font-medium">
                      {i + 1}. {step.node_name}
                    </div>
                    <div className="text-sm text-gray-600">
                      {step.message}
                    </div>
                    {step.duration && (
                      <div className="text-xs text-gray-500 mt-1">
                        [{step.duration}ms]
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Final Result */}
            {execution.status === 'completed' && (
              <div className="mt-4">
                <h3 className="font-bold mb-2">Final Result</h3>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto">
                  {JSON.stringify(execution.steps[execution.steps.length - 1]?.result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

### 6.2 Backend API Endpoints

#### Skill Management
```python
# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import asyncio

app = FastAPI()

# In-memory skill storage (use database in production)
skills_db = {}

class Skill(BaseModel):
    id: str
    version: str
    metadata: Dict[str, Any]
    triggers: Dict[str, Any]
    input_parameters: List[Dict[str, Any]]
    output_format: Dict[str, Any]
    workflow: Dict[str, Any]
    examples: List[Dict[str, Any]]
    statistics: Dict[str, Any]

@app.post("/api/skills")
async def create_skill(skill: Skill):
    """Save a new skill definition."""
    skills_db[skill.id] = skill.dict()
    return skill

@app.get("/api/skills")
async def list_skills():
    """Get all saved skills."""
    return list(skills_db.values())

@app.get("/api/skills/{skill_id}")
async def get_skill(skill_id: str):
    """Get a specific skill."""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skills_db[skill_id]

@app.put("/api/skills/{skill_id}")
async def update_skill(skill_id: str, skill: Skill):
    """Update an existing skill."""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")
    skills_db[skill_id] = skill.dict()
    return skill

@app.delete("/api/skills/{skill_id}")
async def delete_skill(skill_id: str):
    """Delete a skill."""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")
    del skills_db[skill_id]
    return {"success": True}
```

#### Skill Execution
```python
# skill_executor.py

import asyncio
from typing import Dict, Any, AsyncGenerator
import time

class SkillExecutor:
    def __init__(self, tool_executor):
        self.tool_executor = tool_executor

    async def execute_skill(
        self,
        skill: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a skill workflow and yield progress events."""

        workflow = skill['workflow']
        nodes = {node['id']: node for node in workflow['nodes']}
        edges = workflow['edges']

        # Build execution graph
        graph = self._build_execution_graph(nodes, edges)

        # Topological sort for execution order
        execution_order = self._topological_sort(graph)

        # Execute nodes in order
        context = {'input': input_data}

        for node_id in execution_order:
            node = nodes[node_id]

            yield {
                'type': 'node_start',
                'node_id': node_id,
                'node_name': node.get('data', {}).get('tool_name', node['type']),
                'status': 'running'
            }

            start_time = time.time()

            try:
                result = await self._execute_node(node, context)
                context[node_id] = result

                duration_ms = int((time.time() - start_time) * 1000)

                yield {
                    'type': 'node_complete',
                    'node_id': node_id,
                    'node_name': node.get('data', {}).get('tool_name', node['type']),
                    'status': 'success',
                    'result': result,
                    'duration': duration_ms,
                    'message': f'Completed in {duration_ms}ms'
                }

            except Exception as e:
                yield {
                    'type': 'node_error',
                    'node_id': node_id,
                    'status': 'error',
                    'error': str(e),
                    'message': f'Error: {str(e)}'
                }
                raise

        # Return final result
        exit_node = workflow['exit_points'][0]
        yield {
            'type': 'skill_complete',
            'status': 'completed',
            'result': context.get(exit_node)
        }

    async def _execute_node(self, node: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a single node."""
        node_type = node['type']
        data = node['data']

        if node_type == 'tool':
            # Execute tool
            tool_name = data['tool_name']
            parameters = self._resolve_parameters(data['parameters'], context)

            result = await self.tool_executor.execute(tool_name, parameters)
            return result

        elif node_type == 'transform':
            # Apply transformation
            operation = data['operation']
            config = self._resolve_parameters(data['config'], context)

            if operation == 'extract_fields':
                return self._extract_fields(config)
            # ... other transformations

        elif node_type == 'decision':
            # Evaluate condition
            condition = self._evaluate_condition(data['condition'], context)
            return {'branch': 'true' if condition else 'false'}

        elif node_type == 'loop':
            # Execute loop body
            results = []
            items = self._resolve_value(data['iteration_source'], context)

            for item in items:
                loop_context = {**context, data['loop_variable']: item}
                # Execute body nodes
                # ...
                results.append(loop_result)

            return results

        elif node_type == 'merge':
            # Merge inputs
            inputs = [self._resolve_value(inp, context) for inp in data['inputs']]
            strategy = data['strategy']

            if strategy == 'concatenate':
                return ''.join(str(i) for i in inputs)
            elif strategy == 'merge_objects':
                return {**inputs[0], **inputs[1]}
            # ... other strategies

    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter values from context."""
        resolved = {}
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Variable reference
                path = value[2:-1]
                resolved[key] = self._resolve_value(path, context)
            else:
                resolved[key] = value
        return resolved

    def _resolve_value(self, path: str, context: Dict[str, Any]) -> Any:
        """Resolve a dotted path in context."""
        parts = path.split('.')
        value = context
        for part in parts:
            value = value.get(part)
            if value is None:
                break
        return value

    def _build_execution_graph(self, nodes: Dict, edges: List) -> Dict:
        """Build adjacency list from edges."""
        graph = {node_id: [] for node_id in nodes}
        for edge in edges:
            graph[edge['source']].append(edge['target'])
        return graph

    def _topological_sort(self, graph: Dict) -> List[str]:
        """Topological sort for execution order."""
        # Kahn's algorithm
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1

        queue = [node for node in graph if in_degree[node] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

# API endpoint
@app.post("/api/skills/test")
async def test_skill(request: Dict[str, Any]):
    """Test a skill with sample input."""
    skill_id = request['skill_id']
    test_input = request['test_input']

    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill = skills_db[skill_id]
    executor = SkillExecutor(tool_executor)

    async def event_generator():
        async for event in executor.execute_skill(skill, test_input):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
**Goal**: Basic workflow editor with tool nodes

- [ ] Set up ReactFlow canvas
- [ ] Implement ToolNode component
- [ ] Create tool palette (drag source)
- [ ] Basic node connection (edges)
- [ ] Save/load workflow to JSON
- [ ] Simple skill metadata form

**Deliverable**: Can create a 2-3 node workflow and save it

---

### Phase 2: Skill Execution (Week 3-4)
**Goal**: Execute simple linear workflows

- [ ] Backend skill executor with topological sort
- [ ] Tool execution integration
- [ ] Parameter resolution (${variable} syntax)
- [ ] Skill testing panel
- [ ] Execution visualization (step by step)
- [ ] Error handling and display

**Deliverable**: Can test and execute linear tool chains

---

### Phase 3: Advanced Nodes (Week 5-6)
**Goal**: Conditional logic and loops

- [ ] DecisionNode (if/else)
- [ ] LoopNode (iteration)
- [ ] MergeNode (combine data)
- [ ] TransformNode (data manipulation)
- [ ] Advanced edge types (conditional, loop)
- [ ] Complex workflow validation

**Deliverable**: Can create branching and looping workflows

---

### Phase 4: Agent Integration (Week 7-8)
**Goal**: Agent recognizes and uses skills

- [ ] Skill trigger matching system
- [ ] Agent skill library UI
- [ ] Automatic skill suggestion
- [ ] Agent perspective panel
- [ ] Skill usage statistics
- [ ] Agent "thinking" visualization

**Deliverable**: Agent automatically applies skills to user requests

---

### Phase 5: Templates & Polish (Week 9-10)
**Goal**: Pre-built templates and UX polish

- [ ] 10+ skill templates
- [ ] Template preview and import
- [ ] Skill duplication
- [ ] Advanced search/filtering
- [ ] Workflow export/import (JSON)
- [ ] Documentation and examples
- [ ] Performance optimization

**Deliverable**: Production-ready skill builder with rich template library

---

## 8. Success Metrics

### User Metrics
- **Skill Creation Rate**: Number of custom skills created per user
- **Skill Reuse**: Average times each skill is used
- **Template Usage**: % of skills based on templates vs. from scratch
- **Workflow Complexity**: Average nodes per skill

### Technical Metrics
- **Execution Success Rate**: % of skill executions that complete successfully
- **Average Execution Time**: Time per skill execution
- **Error Rate**: % of skill executions that fail
- **Canvas Performance**: FPS when editing large workflows (>20 nodes)

### Agent Effectiveness
- **Skill Match Accuracy**: % of requests correctly matched to skills
- **User Satisfaction**: Rating after skill-based responses
- **Skill Coverage**: % of user requests that match a skill vs. ad-hoc execution

---

## 9. Future Enhancements

### 9.1 Skill Marketplace
- Share skills publicly
- Browse community skills
- Rate and review skills
- Import others' skills with one click

### 9.2 AI-Assisted Skill Creation
- "Describe what you want, and I'll build the workflow"
- Automatic workflow optimization
- Suggest missing error handling
- Auto-generate skill from conversation history

### 9.3 Skill Versioning
- Track skill version history
- A/B test different workflow versions
- Rollback to previous versions
- Compare performance across versions

### 9.4 Advanced Node Types
- **API Call Node**: Make HTTP requests
- **Database Node**: Query databases
- **Email Node**: Send emails
- **Webhook Node**: Trigger external services
- **Schedule Node**: Run at specific times
- **Human-in-the-Loop Node**: Request user input mid-workflow

### 9.5 Collaborative Editing
- Multiple users edit same skill
- Real-time collaboration (like Figma)
- Comments on nodes
- Skill review workflow

---

## 10. Design Mockups

### 10.1 Full Application View

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  SkillBuilder                                              warren@aicraft.com  [?] [⚙️] │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│ ┌──────────────┬────────────────────────────────────────────────────┬──────────────┐ │
│ │              │                                                    │              │ │
│ │ SKILL        │  WORKFLOW CANVAS                                   │ CONFIG       │ │
│ │ LIBRARY      │                                                    │ PANEL        │ │
│ │              │  ┌──────────────────────────────────────────────┐ │              │ │
│ │ Search       │  │ Tools:  🔍 📝 📖 🔢 🎨 ⚙️  🔀  🔁          │ │ Name:        │ │
│ │ [________]   │  └──────────────────────────────────────────────┘ │ Research &   │ │
│ │              │                                                    │ Summarize    │ │
│ │ Built-in (2) │                                                    │              │ │
│ │ • Chat       │         ┌──────────┐                              │ Description: │ │
│ │ • Calc       │         │ 🔍 START │                              │ Search web   │ │
│ │              │         │web_search│                              │ and create   │ │
│ │ Custom (5)   │         │ ${query} │                              │ summary doc  │ │
│ │ ★ Research   │         └────┬─────┘                              │              │ │
│ │   & Summ.    │              │                                     │ Triggers:    │ │
│ │   [Edit]     │              ▼                                     │ • research   │ │
│ │              │         ┌──────────┐                              │ • summarize  │ │
│ │ • Data       │         │ 🔄 Trans │                              │              │ │
│ │   Analysis   │         │ Extract  │                              │ Inputs:      │ │
│ │   [Edit]     │         │ fields   │                              │ 1. query     │ │
│ │              │         └────┬─────┘                              │    (string)  │ │
│ │ • Content    │              │                                     │              │ │
│ │   Creator    │              ▼                                     │ Outputs:     │ │
│ │   [Edit]     │         ┌──────────┐                              │ • file_path  │ │
│ │              │         │ 📝 END   │                              │ • sources    │ │
│ │ • File Org.  │         │file_write│                              │              │ │
│ │   [Edit]     │         │ ${path}  │                              │              │ │
│ │              │         └──────────┘                              │ [Test Skill] │ │
│ │ • Email      │                                                    │ [Save Skill] │ │
│ │   Responder  │                                                    │              │ │
│ │   [Edit]     │                                                    │              │ │
│ │              │                                                    │              │ │
│ │ Templates    │  [Mini Map]                                        │              │ │
│ │ • Web        │  ┌─────┐                                           │              │ │
│ │   Research   │  │ ● │ │                                           │              │ │
│ │ • Code       │  │  ●  │                                           │              │ │
│ │   Helper     │  │   ● │                                           │              │ │
│ │ ...          │  └─────┘                                           │              │ │
│ │              │                                                    │              │ │
│ │              │                                                    │              │ │
│ │ [+ New]      │                                                    │              │ │
│ │ [Import]     │                                                    │              │ │
│ │              │                                                    │              │ │
│ └──────────────┴────────────────────────────────────────────────────┴──────────────┘ │
│                                                                                        │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ SKILL TESTER                                              [Collapse] [Close]     │ │
│ ├──────────────────────────────────────────────────────────────────────────────────┤ │
│ │ Test Input: query: "AI safety research 2025"              [Run Test]            │ │
│ │                                                                                  │ │
│ │ ✅ 1. web_search [120ms] → Found 3 results                                      │ │
│ │ ✅ 2. transform [15ms] → Extracted 6 fields                                     │ │
│ │ 🔵 3. file_write [running...] → Writing to /tmp/research_summary.md            │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────┐
│ 🤖 AGENT VIEW         [−][×]│
├────────────────────────────┤
│       _____                │
│      /     \               │
│     |  ^_^  |              │
│      \_____/               │
│                            │
│ Skills: 7 total            │
│ ├─ Built-in: 2            │
│ └─ Custom: 5              │
│                            │
│ Most Used:                 │
│ 🔍 Research (42×)          │
│ 📊 Analysis (18×)          │
│                            │
│ "I can now help with       │
│  7 different types of      │
│  tasks!"                   │
└────────────────────────────┘
```

---

## 11. Appendix: Example Workflows

### Example 1: Complex Research Workflow

```
Input: "Research AI safety and create presentation"

Workflow:
1. web_search(query: "AI safety 2025")
   ↓
2. Decision: results.count > 0?
   ├─ TRUE → Continue
   └─ FALSE → Error("No results found")
   ↓
3. Loop over results (max 5):
   ├─ extract_fields([title, snippet, url])
   ├─ file_write(/tmp/source_{i}.txt)
   └─ collect results
   ↓
4. Merge all sources → combined_text
   ↓
5. Transform: format_as_slides(combined_text)
   ↓
6. file_write(/tmp/presentation.md)
   ↓
7. Return: {file: "/tmp/presentation.md", sources: 5}
```

### Example 2: Data Pipeline with Conditional Processing

```
Input: data_file="/data/sales.csv", threshold=1000

Workflow:
1. file_read(path: data_file)
   ↓
2. calculator(expression: "SUM(column_B)")
   ↓
3. Decision: sum > threshold?
   ├─ TRUE → Branch A
   │   ├─ image_gen("Chart showing high sales")
   │   └─ file_write("/tmp/high_sales_report.md")
   │
   └─ FALSE → Branch B
       ├─ file_write("/tmp/low_sales_alert.txt")
       └─ Return: {alert: "Sales below threshold"}
```

---

## Summary

The Custom Skills Builder transforms the agent from a passive tool executor into an active skill learner. By creating reusable workflows through visual programming, users teach the agent new capabilities that become permanent parts of its repertoire.

**Key Innovations**:
1. **Visual Workflow Editor**: Drag-and-drop node-based interface (ReactFlow)
2. **Skill Library**: Personal collection of reusable workflows
3. **Agent Perspective**: First-person view of growing capabilities
4. **Live Testing**: Real-time execution visualization
5. **Template System**: Pre-built workflows for common tasks

**Technical Stack**:
- Frontend: React + ReactFlow + Tailwind CSS
- Backend: FastAPI + Anthropic SDK
- Execution: Topological sort + async streaming

**Expected Impact**:
- Users create 5-10 custom skills within first week
- 80% of repetitive tasks automated through skills
- Agent becomes 3x more efficient for common workflows
- Skills reused average 15 times each

This design provides a complete blueprint for implementation, from UI mockups to backend APIs to example workflows. The system is extensible, allowing future additions like skill marketplace, AI-assisted creation, and collaborative editing.
