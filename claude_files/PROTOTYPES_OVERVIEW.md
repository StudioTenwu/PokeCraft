# AICraft: 5 Prototype Experiences

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  COMPARATIVELY STRUCTURED                        │
│                     OBSERVATION METHOD                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   EVOLUTION      │  │     MEMORY       │  │   PERCEPTION     │
│   PLAYGROUND     │  │    THEATER       │  │      LAB         │
│                  │  │                  │  │                  │
│  Port: 5180  ✅  │  │  Port: 5181  ✅  │  │  Port: 5182  ⚠️  │
│                  │  │                  │  │                  │
│  Manual Config   │  │  Narrative vs    │  │  Single vs       │
│     vs.          │  │   Database       │  │  Multimodal      │
│  Learned Behavior│  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐
│   TOOL FORGE     │  │     AGENT        │
│                  │  │   ORCHESTRA      │
│  Port: 5183  ⚠️  │  │  Port: 5184  ⚠️  │
│                  │  │                  │
│  Pre-made vs     │  │  Hierarchical vs │
│  Compositional   │  │   Peer-to-Peer   │
│                  │  │                  │
└──────────────────┘  └──────────────────┘

Legend: ✅ Complete  ⚠️ Scaffolded
```

## Design Dimensions Matrix

```
Dimension           | Prototype            | A vs. B
--------------------|----------------------|-------------------------
Growth Mechanism    | Evolution Playground | Config vs. Learned
Memory Structure    | Memory Theater       | Narrative vs. Database
Perception Model    | Perception Lab       | Single vs. Multimodal
Tool Abstraction    | Tool Forge           | Pre-made vs. Compositional
Coordination Pattern| Agent Orchestra      | Hierarchical vs. Peer
```

## Quick Access

```bash
# Start all
cd prototypes && ./start_all.sh

# Access URLs
Evolution:  http://localhost:5180
Memory:     http://localhost:5181
Perception: http://localhost:5182
Tools:      http://localhost:5183
Orchestra:  http://localhost:5184

# Stop all
cd prototypes && ./stop_all.sh
```

## Implementation Details

### Complete Prototypes (2/5)

#### 1. Evolution Playground
- **3 modes:** Config, Experience, Hybrid
- **8 tasks** across 4 capabilities
- **Energy system** with task rewards
- **Real-time stat evolution**
- **Task history** with success tracking

#### 2. Memory Theater
- **2 viewing modes:** Narrative timeline, Database table
- **Memory editing:** Content, tags, emotions, types
- **Causal relationships:** Memory A → Memory B
- **Search/filter:** Find memories by content or tags
- **5 emotion types:** Happy, Excited, Neutral, Confused, Sad

### Scaffolded Prototypes (3/5)

Perception Lab, Tool Forge, and Agent Orchestra have:
- ✅ Vite + React + Tailwind configured
- ✅ Shared components installed
- ✅ Port assignments (5182-5184)
- ❌ App logic not yet implemented

## Shared Components

```javascript
// AgentAvatar.jsx
<AgentAvatar
  name="Agent"
  level={5}
  mood="happy"  // happy, neutral, thinking, excited, confused, sleeping
  size="xl"     // sm, md, lg, xl
  animated={true}
/>

// ConfigPanel.jsx
<ConfigPanel title="Settings">
  <ConfigPanel.Slider label="Perception" value={50} onChange={...} />
  <ConfigPanel.Toggle label="Vision" checked={true} onChange={...} />
  <ConfigPanel.Select label="Mode" options={...} onChange={...} />
</ConfigPanel>

// agentUtils.js
calculateAgentLevel(stats) → number
determineAgentMood(successRate, energy) → string
generateAgentResponse(context, capabilities) → string
```

## Testing Protocol

### Phase 1: Individual Testing (Week 1)
- Test each complete prototype separately
- 5 children per prototype
- 30-minute sessions
- Observe natural exploration patterns

### Phase 2: Comparative Testing (Week 2)
- **Group A:** Sequential exposure (Evolution → Memory)
- **Group B:** Choice (both available, track preference)
- **Group C:** Alternating (start with different prototype)

### Phase 3: Analysis (Week 3)
- Which mode do children prefer when given choice?
- Do preferences correlate with age/experience?
- Which design creates "aha" moments faster?
- Which leads to better understanding of primitives?

## Success Metrics

### Engagement
- ⏱️ Time spent exploring (without prompting)
- 🔄 Number of different configurations tried
- 🔁 Return rate (multiple sessions)
- 💡 Spontaneous "aha!" moments observed

### Understanding
- 🎯 Can predict what config changes will do
- 📝 Can explain why combinations work/don't work
- 🎨 Can design agents for specific purposes
- 🔀 Can transfer knowledge between prototypes

### Preference
- 👍 Explicit choice when both modes available
- ⏰ Time spent in each mode
- 🎭 Expressed enjoyment/frustration
- 🗣️ Verbal feedback and suggestions

## Key Research Questions

1. **Do children prefer direct control or emergent behavior?**
   - Evolution Playground tests this

2. **How do children naturally conceptualize memory?**
   - Memory Theater tests this

3. **Can children understand perception cost/benefit trade-offs?**
   - Perception Lab will test this

4. **Do children prefer convenience or creativity in tools?**
   - Tool Forge will test this

5. **Which coordination model is more intuitive?**
   - Agent Orchestra will test this

## Next Actions

### Immediate (This Week)
- [x] Complete Evolution Playground
- [x] Complete Memory Theater
- [x] Create shared infrastructure
- [x] Set up remaining 3 prototypes
- [x] Write documentation
- [ ] Test Evolution Playground with 3-5 users
- [ ] Test Memory Theater with 3-5 users

### Short-term (Next 2 Weeks)
- [ ] Implement Perception Lab (easiest of remaining)
- [ ] Implement Tool Forge
- [ ] Implement Agent Orchestra
- [ ] Run comparative study with all 5

### Medium-term (Next Month)
- [ ] Analyze which designs work best
- [ ] Synthesize findings into final AICraft design
- [ ] Add LLM integration to all prototypes
- [ ] Build comparison dashboard

## File Locations

```
/Users/wz/Desktop/zPersonalProjects/AICraft/
├── prototypes/
│   ├── evolution-playground/     ✅ Complete
│   ├── memory-theater/           ✅ Complete
│   ├── perception-lab/           ⚠️ Scaffolded
│   ├── tool-forge/               ⚠️ Scaffolded
│   ├── agent-orchestra/          ⚠️ Scaffolded
│   ├── shared/                   Components & utils
│   ├── start_all.sh              Startup script
│   ├── stop_all.sh               Shutdown script
│   └── README.md                 Main documentation
└── claude_files/
    ├── prototype_summary.md      Detailed summary
    └── PROTOTYPES_OVERVIEW.md    This file
```

## Philosophy

This approach embodies:

1. **Empiricism over intuition** - Test, don't guess
2. **Comparison over isolation** - A vs. B reveals more than A alone
3. **Observation over instruction** - Watch what children do naturally
4. **Iteration over perfection** - Build quickly, learn fast, improve
5. **Evidence over opinion** - Let data guide final design

## The Ultimate Goal

Use these 5 prototypes to answer definitively:

> "What is the **most effective** way to help children understand AI agents through interactive play?"

Not what we **think** works.
What **actually** works.
Proven through systematic observation of real children.

---

**Status:** 2/5 complete, ready for initial comparative testing
**Next:** Test complete prototypes, gather feedback, iterate
**Timeline:** 2 weeks to completion of all 5
