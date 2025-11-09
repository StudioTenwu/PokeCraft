# Agent 2: Custom Skills Builder - Implementation Checklist

## Overview
This checklist guides the implementation of the Custom Skills Builder, a visual workflow editor that allows users to create reusable agent skills by combining tools.

**Related Documents**:
- Full Design: `/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/agent2_custom_skills_builder_design.md`
- Quick Reference: `/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/agent2_quick_reference.md`
- Templates: `/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/agent2_skill_templates.json`

---

## Phase 1: Foundation (Week 1-2)

### Frontend Setup

- [ ] **Install Dependencies**
  ```bash
  cd frontend
  npm install reactflow react-dnd react-dnd-html5-backend
  ```

- [ ] **Create Component Structure**
  - [ ] `src/components/skill-builder/SkillBuilder.jsx` (main container)
  - [ ] `src/components/skill-builder/WorkflowCanvas.jsx` (ReactFlow wrapper)
  - [ ] `src/components/skill-builder/ToolPalette.jsx` (drag source)
  - [ ] `src/components/skill-builder/SkillLibrary.jsx` (left sidebar)
  - [ ] `src/components/skill-builder/SkillConfigPanel.jsx` (right sidebar)

- [ ] **Implement ToolPalette Component**
  - [ ] Display all available tools as draggable cards
  - [ ] Tool icons and names from TOOL_SCHEMAS
  - [ ] Drag-and-drop using react-dnd
  - [ ] Visual feedback during drag

- [ ] **Implement WorkflowCanvas Component**
  - [ ] Initialize ReactFlow
  - [ ] Handle drop events from ToolPalette
  - [ ] Create new ToolNode on drop
  - [ ] Enable node connection (edges)
  - [ ] Add Background, Controls, MiniMap

- [ ] **Implement ToolNode Component**
  ```jsx
  // src/components/skill-builder/nodes/ToolNode.jsx
  - [ ] Display tool icon and name
  - [ ] Input/output handles (top/bottom)
  - [ ] Parameter display
  - [ ] Settings button (opens modal)
  - [ ] Delete button
  - [ ] Execution status indicator
  ```

- [ ] **Implement SkillConfigPanel Component**
  - [ ] Skill name input
  - [ ] Description textarea
  - [ ] Trigger keywords list (add/remove)
  - [ ] Input parameters list (add/remove/edit)
  - [ ] Save button
  - [ ] Test button

- [ ] **Add State Management**
  ```jsx
  const [currentSkill, setCurrentSkill] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  ```

- [ ] **Implement Save/Load Workflow**
  - [ ] Convert ReactFlow state to skill JSON
  - [ ] POST to `/api/skills`
  - [ ] Load skill from JSON into ReactFlow
  - [ ] Handle errors gracefully

### Backend Setup

- [ ] **Create Skill Models**
  ```python
  # backend/models/skill.py
  - [ ] SkillMetadata model
  - [ ] SkillTriggers model
  - [ ] SkillWorkflow model
  - [ ] Complete Skill model
  ```

- [ ] **Implement Skill Storage**
  ```python
  # backend/skill_storage.py
  - [ ] In-memory dict (for MVP)
  - [ ] CRUD operations
  - [ ] Future: SQLite/PostgreSQL
  ```

- [ ] **Create API Endpoints**
  ```python
  # backend/main.py
  - [ ] POST /api/skills (create)
  - [ ] GET /api/skills (list all)
  - [ ] GET /api/skills/{id} (get one)
  - [ ] PUT /api/skills/{id} (update)
  - [ ] DELETE /api/skills/{id} (delete)
  ```

- [ ] **Add Validation**
  - [ ] Validate workflow structure
  - [ ] Check for circular dependencies
  - [ ] Ensure all nodes have valid tool names
  - [ ] Verify input/output connections

### Testing

- [ ] **Manual Testing**
  - [ ] Create a 2-node workflow (web_search → file_write)
  - [ ] Save skill to backend
  - [ ] Load skill from backend
  - [ ] Edit and re-save skill
  - [ ] Delete skill

- [ ] **UI/UX Verification**
  - [ ] Drag-and-drop feels smooth
  - [ ] Node connections are clear
  - [ ] Save button provides feedback
  - [ ] Error messages are helpful

---

## Phase 2: Skill Execution (Week 3-4)

### Backend Execution Engine

- [ ] **Create SkillExecutor Class**
  ```python
  # backend/skill_executor.py
  - [ ] __init__(tool_executor)
  - [ ] execute_skill(skill, input_data) → AsyncGenerator
  - [ ] _execute_node(node, context)
  - [ ] _resolve_parameters(params, context)
  - [ ] _resolve_value(path, context)
  ```

- [ ] **Implement Topological Sort**
  - [ ] Build execution graph from edges
  - [ ] Kahn's algorithm for topological ordering
  - [ ] Detect cycles (should fail validation)
  - [ ] Handle disconnected nodes

- [ ] **Node Execution Logic**
  - [ ] ToolNode: execute tool with resolved params
  - [ ] Store result in context with node_id as key
  - [ ] Handle errors per node
  - [ ] Emit progress events

- [ ] **Parameter Resolution**
  ```python
  # Handle variable syntax: ${input.query}, ${node_1.results}
  - [ ] Parse ${...} syntax
  - [ ] Navigate context with dot notation
  - [ ] Support nested paths (${node_1.results.count})
  - [ ] Return error if path not found
  ```

- [ ] **Event Streaming**
  - [ ] Yield `node_start` event
  - [ ] Yield `node_complete` event with result
  - [ ] Yield `node_error` event on failure
  - [ ] Yield `skill_complete` event at end
  - [ ] Include timing information

- [ ] **API Endpoint**
  ```python
  # POST /api/skills/test
  - [ ] Accept skill_id and test_input
  - [ ] Load skill from storage
  - [ ] Create SkillExecutor
  - [ ] Stream events as SSE
  - [ ] Handle errors gracefully
  ```

### Frontend Testing Panel

- [ ] **Create SkillTester Component**
  ```jsx
  // src/components/skill-builder/SkillTester.jsx
  - [ ] Collapsible panel at bottom
  - [ ] Test input form (from skill.input_parameters)
  - [ ] Run Test button
  - [ ] Execution timeline display
  - [ ] Final result display
  ```

- [ ] **Implement Test Input Form**
  - [ ] Generate inputs from skill.input_parameters
  - [ ] Text inputs for strings
  - [ ] Number inputs for integers
  - [ ] Required field validation
  - [ ] Default values

- [ ] **Execution Timeline**
  - [ ] List of steps (one per node)
  - [ ] Status icons (⚪ pending, 🔵 running, ✅ success, ❌ error)
  - [ ] Duration display (ms)
  - [ ] Result preview for each step
  - [ ] Auto-scroll to current step

- [ ] **SSE Integration**
  ```jsx
  - [ ] useAgentStream hook (reuse from Stage 1-4)
  - [ ] Parse SSE events
  - [ ] Update timeline as events arrive
  - [ ] Handle errors
  - [ ] Show "completed" when done
  ```

- [ ] **Data Flow Visualization**
  - [ ] Simple text-based flow diagram
  - [ ] Show data values between steps
  - [ ] Highlight active step
  - [ ] Display data types and sizes

### Testing

- [ ] **Create Test Skills**
  - [ ] Simple: web_search → file_write
  - [ ] Medium: web_search → transform → file_write
  - [ ] Complex: with multiple branches

- [ ] **Execute Test Skills**
  - [ ] Verify execution order is correct
  - [ ] Check parameter resolution works
  - [ ] Confirm results are stored in context
  - [ ] Test error handling (invalid params)

- [ ] **Verify UI Updates**
  - [ ] Timeline updates in real-time
  - [ ] Status icons change correctly
  - [ ] Final result displays properly
  - [ ] Errors show helpful messages

---

## Phase 3: Advanced Nodes (Week 5-6)

### New Node Types

- [ ] **DecisionNode Component**
  ```jsx
  // src/components/skill-builder/nodes/DecisionNode.jsx
  - [ ] Diamond shape or distinct styling
  - [ ] Condition input (expression editor)
  - [ ] Two output handles: "true" and "false"
  - [ ] Show evaluated result during testing
  ```

- [ ] **DecisionNode Execution**
  ```python
  # In skill_executor.py
  - [ ] Parse condition expression
  - [ ] Evaluate with context
  - [ ] Return branch decision
  - [ ] Support: ==, !=, >, <, >=, <=, &&, ||
  ```

- [ ] **LoopNode Component**
  ```jsx
  // src/components/skill-builder/nodes/LoopNode.jsx
  - [ ] Loop icon
  - [ ] Iteration source input (${array})
  - [ ] Loop variable name input
  - [ ] Max iterations input
  - [ ] Body nodes selection
  ```

- [ ] **LoopNode Execution**
  ```python
  - [ ] Resolve iteration_source to array
  - [ ] For each item:
  -     [ ] Create loop context with item
  -     [ ] Execute body nodes
  -     [ ] Collect results
  - [ ] Respect max_iterations limit
  - [ ] Return array of results
  ```

- [ ] **MergeNode Component**
  ```jsx
  // src/components/skill-builder/nodes/MergeNode.jsx
  - [ ] Multiple input handles
  - [ ] Merge strategy selector (concatenate, merge_objects, combine_arrays)
  - [ ] Single output handle
  ```

- [ ] **MergeNode Execution**
  ```python
  - [ ] Resolve all inputs
  - [ ] Apply strategy:
  -     [ ] concatenate: join strings
  -     [ ] merge_objects: spread operator
  -     [ ] combine_arrays: flatten
  - [ ] Return merged result
  ```

- [ ] **TransformNode Component**
  ```jsx
  // src/components/skill-builder/nodes/TransformNode.jsx
  - [ ] Transform operation selector
  - [ ] Config inputs (varies by operation)
  - [ ] Preview transformed data
  ```

- [ ] **TransformNode Execution**
  ```python
  - [ ] extract_fields: pick specific fields from object
  - [ ] format_text: apply string formatting
  - [ ] filter_array: keep items matching condition
  - [ ] map_array: transform each item
  ```

### Enhanced Edge Types

- [ ] **Conditional Edges**
  - [ ] Visual: dashed line for "false" branch
  - [ ] Labeled edges ("true", "false")
  - [ ] Special routing for decision nodes

- [ ] **Loop Edges**
  - [ ] Visual: curved arrow for loop back
  - [ ] Special handling in execution

### Workflow Validation

- [ ] **Enhanced Validation**
  - [ ] Decision nodes have exactly 2 outputs
  - [ ] Loop nodes have valid iteration source
  - [ ] Transform nodes have required config
  - [ ] Type compatibility checks between nodes
  - [ ] No orphaned nodes

### Testing

- [ ] **Test Decision Workflow**
  - [ ] Create workflow with if/else branches
  - [ ] Test both branches execute correctly
  - [ ] Verify only one branch runs

- [ ] **Test Loop Workflow**
  - [ ] Create workflow with loop over array
  - [ ] Verify body executes N times
  - [ ] Check results are collected

- [ ] **Test Complex Workflow**
  - [ ] Combine loops, decisions, and merges
  - [ ] Verify execution order is correct
  - [ ] Test edge cases (empty arrays, false conditions)

---

## Phase 4: Agent Integration (Week 7-8)

### Skill Trigger Matching

- [ ] **Create SkillMatcher Class**
  ```python
  # backend/skill_matcher.py
  - [ ] __init__(skills_db)
  - [ ] find_matching_skill(user_message)
  - [ ] _match_keywords(message, skill)
  - [ ] _match_patterns(message, skill)
  - [ ] _calculate_confidence(message, skill)
  ```

- [ ] **Keyword Matching**
  - [ ] Tokenize user message
  - [ ] Check if any trigger keywords present
  - [ ] Case-insensitive matching
  - [ ] Partial word matching

- [ ] **Pattern Matching**
  - [ ] Support wildcard patterns ("research * and summarize")
  - [ ] Convert to regex
  - [ ] Match against message
  - [ ] Extract variables from wildcards

- [ ] **Confidence Scoring**
  - [ ] Keyword count / total keywords
  - [ ] Pattern match quality
  - [ ] Historical success rate
  - [ ] Combined score 0-1

- [ ] **API Endpoint**
  ```python
  # POST /api/skills/match
  - [ ] Accept user message
  - [ ] Return top matching skills
  - [ ] Include confidence scores
  - [ ] Return skill metadata
  ```

### Agent Skill Integration

- [ ] **Modify Agent Stage Handlers**
  ```python
  # In stages.py - add skill awareness
  - [ ] Before tool execution, check for skill matches
  - [ ] If confidence > threshold:
  -     [ ] Suggest skill to agent
  -     [ ] Execute skill instead of ad-hoc tools
  - [ ] Track skill usage
  ```

- [ ] **Agent Skill Selection**
  - [ ] Agent system prompt includes available skills
  - [ ] Agent can choose to use skill or not
  - [ ] Agent explains why using skill
  - [ ] Agent can fall back to ad-hoc if skill fails

- [ ] **Skill Execution Tracking**
  - [ ] Update skill.statistics.times_used
  - [ ] Track success/failure rate
  - [ ] Record execution time
  - [ ] Update last_used timestamp

### Frontend Agent Perspective

- [ ] **Create AgentPerspectivePanel Component**
  ```jsx
  // src/components/skill-builder/AgentPerspectivePanel.jsx
  - [ ] Floating panel (draggable)
  - [ ] Agent avatar
  - [ ] Skill count (built-in + custom)
  - [ ] Most used skills list
  - [ ] Recent additions
  - [ ] "Agent thinking" text
  - [ ] Capability tree
  ```

- [ ] **Agent Thinking Updates**
  - [ ] Update when skill created
  - [ ] Update when skill used
  - [ ] Show current capabilities
  - [ ] Celebrate milestones (5 skills, 10 skills, etc.)

- [ ] **Capability Tree**
  - [ ] Group skills by category
  - [ ] Show skill hierarchy
  - [ ] Visual representation of growth

### SkillLibrary Enhancements

- [ ] **Display Skill Statistics**
  - [ ] Times used badge
  - [ ] Success rate percentage
  - [ ] Last used timestamp
  - [ ] Star popular skills

- [ ] **Skill Search**
  - [ ] Filter by name
  - [ ] Filter by category
  - [ ] Filter by tag
  - [ ] Sort by usage, success rate, date

- [ ] **Skill Actions**
  - [ ] Edit (load into canvas)
  - [ ] Duplicate (create copy)
  - [ ] Delete (with confirmation)
  - [ ] Export (download JSON)

### Testing

- [ ] **Test Skill Matching**
  - [ ] Message "research AI" → matches "Research & Summarize"
  - [ ] Message "analyze data" → matches "Data Analysis Pipeline"
  - [ ] Message "hello" → no match
  - [ ] Confidence scores are reasonable

- [ ] **Test Agent Integration**
  - [ ] Agent suggests skill when appropriate
  - [ ] Agent executes skill correctly
  - [ ] Agent explains skill usage
  - [ ] Agent falls back to ad-hoc when needed

- [ ] **Test Statistics Tracking**
  - [ ] Usage count increments
  - [ ] Success rate updates correctly
  - [ ] Last used timestamp updates

---

## Phase 5: Templates & Polish (Week 9-10)

### Skill Templates

- [ ] **Implement Template Loading**
  - [ ] Load from `agent2_skill_templates.json`
  - [ ] Display in SkillLibrary under "Templates"
  - [ ] Preview template (show workflow diagram)
  - [ ] "Use Template" button

- [ ] **Create All Templates**
  - [ ] Web Research
  - [ ] Data Analysis Pipeline
  - [ ] Content Creator
  - [ ] Code Helper
  - [ ] Smart File Organizer
  - [ ] +5 more creative templates

- [ ] **Template Customization**
  - [ ] Load template into canvas
  - [ ] User can modify before saving
  - [ ] Save as new custom skill
  - [ ] Track "based on template X"

### Import/Export

- [ ] **Skill Export**
  - [ ] Export button in SkillLibrary
  - [ ] Download skill as JSON file
  - [ ] Include all metadata and workflow

- [ ] **Skill Import**
  - [ ] Import button in SkillLibrary
  - [ ] Upload JSON file
  - [ ] Validate structure
  - [ ] Add to library

- [ ] **Bulk Import**
  - [ ] Import multiple skills from ZIP
  - [ ] Template packs
  - [ ] Community skill collections

### Documentation

- [ ] **User Guide**
  - [ ] Getting started tutorial
  - [ ] Creating your first skill
  - [ ] Understanding node types
  - [ ] Testing and debugging
  - [ ] Best practices

- [ ] **Developer Docs**
  - [ ] Component architecture
  - [ ] Adding new node types
  - [ ] Custom transform operations
  - [ ] API reference

- [ ] **Examples**
  - [ ] 10+ example skills
  - [ ] Video walkthrough
  - [ ] Common patterns
  - [ ] Troubleshooting guide

### UI/UX Polish

- [ ] **Visual Improvements**
  - [ ] Smooth animations
  - [ ] Consistent color scheme
  - [ ] Professional icons
  - [ ] Responsive layout

- [ ] **Accessibility**
  - [ ] Keyboard shortcuts
  - [ ] Screen reader support
  - [ ] High contrast mode
  - [ ] Focus indicators

- [ ] **Error Handling**
  - [ ] Helpful error messages
  - [ ] Validation feedback
  - [ ] Recovery suggestions
  - [ ] Toast notifications

- [ ] **Performance**
  - [ ] Optimize ReactFlow rendering
  - [ ] Lazy load skill library
  - [ ] Debounce save operations
  - [ ] Cache skill data

### Testing & QA

- [ ] **End-to-End Testing**
  - [ ] Create skill from template
  - [ ] Customize and save
  - [ ] Test execution
  - [ ] Agent uses skill automatically
  - [ ] Export and re-import skill

- [ ] **Browser Testing**
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge

- [ ] **Performance Testing**
  - [ ] Large workflows (20+ nodes)
  - [ ] Many skills (50+ in library)
  - [ ] Concurrent executions
  - [ ] Memory usage

- [ ] **User Testing**
  - [ ] 5+ users try the system
  - [ ] Gather feedback
  - [ ] Identify pain points
  - [ ] Iterate on UX

---

## Final Deliverables

### Code
- [ ] All frontend components implemented
- [ ] All backend APIs implemented
- [ ] All node types working
- [ ] All templates created
- [ ] Tests passing

### Documentation
- [ ] User guide complete
- [ ] Developer docs complete
- [ ] API reference complete
- [ ] Example skills documented

### Deployment
- [ ] Production build working
- [ ] Docker images created
- [ ] Deployment scripts ready
- [ ] Environment variables documented

### Demo
- [ ] Demo video recorded
- [ ] Live demo prepared
- [ ] Screenshots captured
- [ ] Presentation deck created

---

## Success Criteria

- [ ] Users can create a skill in < 5 minutes
- [ ] Skill execution success rate > 95%
- [ ] Agent correctly matches skills 80% of the time
- [ ] System handles 20+ node workflows smoothly
- [ ] Documentation is clear and helpful
- [ ] Code is maintainable and well-tested

---

## Notes

**Key Challenges**:
1. Making workflow editor intuitive for non-programmers
2. Robust parameter resolution (${...} syntax)
3. Efficient skill matching (performance at scale)
4. Clear error messages for workflow validation

**Innovation Opportunities**:
1. AI suggests workflow improvements
2. Auto-generate skill from conversation history
3. Collaborative skill editing
4. Skill marketplace with ratings

**Technical Debt to Avoid**:
1. Hardcoding tool schemas (should be dynamic)
2. In-memory storage (migrate to DB early)
3. No tests (write tests alongside code)
4. Poor error handling (handle all edge cases)

---

**Ready to start Phase 1?** Begin with installing ReactFlow and creating the basic SkillBuilder container!
