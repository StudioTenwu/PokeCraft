# Agent Perspective Panel - Quick Reference Card

> **1-page cheat sheet for developers implementing the Agent Perspective Panel**

---

## 🎯 What Am I Building?

A persistent bottom panel showing agent's internal reasoning in real-time.

**4 Tabs:** What I See | What I Can Do | What I'm Thinking | My Limitations

---

## 📦 Component Checklist

```
✓ AgentPerspectivePanel.jsx      Main container with tabs
✓ WhatISee.jsx                   Context + input analysis
✓ WhatICanDo.jsx                 Tool inventory + relevance
✓ WhatImThinking.jsx             Reasoning timeline (CORE)
✓ MyLimitations.jsx              Capability gaps
✓ ReasoningTimeline.jsx          Step-by-step visualization
✓ ConfidenceMeter.jsx            Visual confidence indicator
✓ usePerspectiveStream.js        Data management hook
```

---

## 🔌 Integration Points

### Frontend (5-line changes)
```jsx
// In App.jsx, add below chat:
import AgentPerspectivePanel from './components/AgentPerspectivePanel';

<AgentPerspectivePanel
  currentStage={currentStage}
  config={agentConfig}
  messages={messages}
  isStreaming={isStreaming}
/>
```

### Backend (30-line changes)
```python
# In stages.py, emit reasoning events:
async def emit_reasoning_step(step_type, description, confidence):
    yield {
        "event": "reasoning_step",
        "data": json.dumps({
            "type": step_type,
            "timestamp": time.time() * 1000,
            "description": description,
            "confidence": confidence
        })
    }

# Usage in agent loop:
await emit_reasoning_step("parsing", "Parsing user input", 0.95)
await emit_reasoning_step("tool_evaluation", "Evaluating tools", 0.85)
```

---

## 📊 Data Structures

### Reasoning Step
```typescript
{
  type: 'parsing' | 'analyzing' | 'tool_evaluation' | 'tool_selection' |
        'execution' | 'processing' | 'formatting' | 'complete' | 'error',
  timestamp: number,           // Unix ms
  duration: number,            // ms
  description: string,
  confidence: number,          // 0-1
  details?: object            // Type-specific data
}
```

### Tool Evaluation
```typescript
{
  name: string,
  score: number,              // 0-1 relevance
  reasoning: string,
  isExecutable: boolean,
  parameters?: object
}
```

---

## 🎨 Styling Guide

### Colors
```css
/* Step types */
📝 Parsing:        blue-500    (bg-blue-50 border-blue-200)
🔍 Analyzing:      yellow-500  (bg-yellow-50 border-yellow-200)
⚖️ Tool Eval:      purple-500  (bg-purple-50 border-purple-200)
✓ Selection:       green-500   (bg-green-50 border-green-200)
⚡ Execution:      orange-500  (bg-orange-50 border-orange-200)
⚙️ Processing:     indigo-500  (bg-indigo-50 border-indigo-200)
📋 Formatting:     pink-500    (bg-pink-50 border-pink-200)
✅ Complete:       green-500   (bg-green-50 border-green-200)
❌ Error:          red-500     (bg-red-50 border-red-200)

/* Confidence levels */
HIGH (70%+):       green-500
MEDIUM (40-69%):   yellow-500
LOW (<40%):        red-500
```

### Dimensions
```css
Panel height (collapsed): 48px
Panel height (expanded):  432px
Content area:             384px (scrollable)
Tab height:               48px
```

---

## ⚡ Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Initial Load | < 200ms | Code splitting |
| Tab Switch | < 50ms | React.memo |
| Step Render | < 16ms | Virtualization |
| SSE Process | < 10ms | Debouncing |
| Memory | < 50MB | Incremental render |
| Bundle | < 150KB | Tree shaking |

---

## 🔑 Key Features Per Tab

### Tab 1: What I See
```jsx
<WhatISee contextState={contextState} messages={messages} />

Displays:
- System prompt (truncated)
- Message count
- Latest query analysis
  - Intent detection
  - Keywords extraction
  - Expected output
- Stage capabilities (checkmarks)
```

### Tab 2: What I Can Do
```jsx
<WhatICanDo availableTools={tools} config={config} />

Displays:
- Tool cards (executable badge)
- Relevance score per tool
- Confidence meters
- Use-case descriptions
- Expandable schemas
- Skills list
```

### Tab 3: What I'm Thinking ⭐
```jsx
<WhatImThinking reasoningTrace={trace} isStreaming={isStreaming} />

Displays:
- Live reasoning timeline
- Color-coded steps
- Confidence per step
- Tool evaluation details
- Performance stats
- Export button
```

### Tab 4: My Limitations
```jsx
<MyLimitations limitations={limitations} currentStage={stage} />

Displays:
- Cannot do list (red)
- How to unlock (blue)
- Can do grid (green)
- Stage progress
```

---

## 🌊 SSE Event Flow

```
User sends message
    ↓
Backend emits:
    → reasoning_step (parsing)
    → reasoning_step (analyzing)
    → reasoning_step (tool_evaluation)
    → reasoning_step (tool_selection)
    → tool_use (existing event)
    → reasoning_step (execution)
    → tool_result (existing event)
    → reasoning_step (processing)
    → text (existing event)
    → reasoning_step (complete)
    ↓
Frontend parses events
    ↓
usePerspectiveStream updates state
    ↓
Components re-render
```

---

## 🎹 Keyboard Shortcuts

```
Tab              Navigate elements
Arrow Keys       Switch tabs (when focused)
Escape           Collapse panel
Ctrl+P           Pin/unpin
Ctrl+E           Export trace
Ctrl+1/2/3/4     Jump to specific tab
```

---

## ♿ Accessibility Requirements

```jsx
// All tabs must have:
role="tab"
aria-selected={activeTab === 'thinking'}
aria-controls="thinking-panel"

// All panels must have:
role="tabpanel"
aria-labelledby="thinking-tab"
hidden={activeTab !== 'thinking'}

// Confidence meters must have:
role="meter"
aria-valuemin="0"
aria-valuemax="100"
aria-valuenow={confidence * 100}

// Live regions for updates:
<div role="status" aria-live="polite" aria-atomic="true">
  {isStreaming ? 'Agent is thinking' : 'Response complete'}
</div>
```

---

## 🧪 Testing Checklist

### Visual
- [ ] Panel expands/collapses smoothly
- [ ] All tabs render correctly
- [ ] Timeline animates properly
- [ ] Confidence meters fill correctly
- [ ] Error states show properly

### Functional
- [ ] SSE events parsed correctly
- [ ] State updates in real-time
- [ ] Export produces valid JSON
- [ ] Keyboard shortcuts work
- [ ] Mobile responsive

### Accessibility
- [ ] Tab order logical
- [ ] Focus indicators visible
- [ ] Screen reader announces updates
- [ ] Color contrast ≥ 4.5:1
- [ ] No focus traps

### Performance
- [ ] Panel loads < 200ms
- [ ] No layout shifts
- [ ] Memory usage acceptable
- [ ] 60fps animations
- [ ] Large traces don't freeze

---

## 🐛 Common Issues & Solutions

### Issue: Timeline doesn't update in real-time
```jsx
// Solution: Check SSE event parsing in usePerspectiveStream
// Ensure event type matches exactly: "reasoning_step"
```

### Issue: Confidence meters show 0%
```jsx
// Solution: Verify confidence is number 0-1, not percentage
confidence: 0.95  // ✓ Correct
confidence: 95    // ✗ Wrong
```

### Issue: Panel blocks chat interface
```css
/* Solution: Ensure proper z-index and positioning */
.agent-perspective-panel {
  position: fixed;
  bottom: 0;
  z-index: 50;  /* Below modals (100) but above chat (10) */
}
```

### Issue: Large traces cause lag
```jsx
// Solution: Use virtualization for 100+ steps
import { FixedSizeList } from 'react-window';
// Or implement incremental rendering
```

---

## 📝 Example Implementation (Minimal)

```jsx
// 1. Create panel component
function AgentPerspectivePanel({ currentStage, messages, isStreaming }) {
  const [activeTab, setActiveTab] = useState('thinking');
  const [isCollapsed, setIsCollapsed] = useState(false);

  const { reasoningTrace } = usePerspectiveStream(messages, isStreaming);

  return (
    <div className={`fixed bottom-0 w-full bg-white shadow-2xl ${
      isCollapsed ? 'h-12' : 'h-96'
    }`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-3">
        <span>Agent First-Person View</span>
        <button onClick={() => setIsCollapsed(!isCollapsed)}>
          {isCollapsed ? '⬆️' : '⬇️'}
        </button>
      </div>

      {!isCollapsed && (
        <>
          {/* Tabs */}
          <div className="flex border-b">
            {['see', 'do', 'thinking', 'limits'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={activeTab === tab ? 'border-b-2 border-purple-500' : ''}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="p-4 h-80 overflow-y-auto">
            {activeTab === 'thinking' && (
              <ReasoningTimeline trace={reasoningTrace} />
            )}
          </div>
        </>
      )}
    </div>
  );
}

// 2. Add to App.jsx
<AgentPerspectivePanel
  currentStage={currentStage}
  messages={messages}
  isStreaming={isStreaming}
/>
```

---

## 🚀 Quick Start (5 Steps)

1. **Create component files** (8 files in `/src/components/perspective/`)
2. **Create hook** (`usePerspectiveStream.js`)
3. **Add to App.jsx** (5 lines)
4. **Enhance backend** (emit reasoning events in `stages.py`)
5. **Test & iterate** (use example traces for testing)

---

## 📚 Full Documentation

- **Summary:** `agent-perspective-panel-summary.md` (13 KB)
- **Design:** `agent-perspective-panel-design.md` (75 KB)
- **Mockups:** `agent-perspective-panel-mockups.md` (45 KB)
- **Index:** `AGENT_PERSPECTIVE_PANEL_INDEX.md`

**Location:** `/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/`

---

## 💪 You Got This!

Start with Tab 3 (What I'm Thinking) - it's the core innovation.
Build the timeline, get SSE events flowing, then add other tabs.

**Estimated Time:**
- Minimal MVP (just timeline): 1-2 days
- Full 4-tab panel: 1 week
- Polished with all features: 2-3 weeks

---

**Questions? Reference the full design docs or ping the team!**
