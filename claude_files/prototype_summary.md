# AICraft Prototype Summary

## What Was Built

I created 5 distinct prototype experiences using **Comparatively Structured Observation** methodology to systematically explore key design dimensions for AICraft.

## The 5 Prototypes

### 1. Evolution Playground ✅ COMPLETE
**Port:** 5180
**Question:** How should agents grow?
**Contrast:** Manual configuration vs. learning through experience

**Implementation:**
- 3 modes: Configuration, Experience, and Hybrid
- 8 tasks across 4 capability dimensions (perception, memory, tools, communication)
- Real-time stat evolution based on task performance
- Energy system and experience points
- Full task history tracking with success rates

**What We Learn:**
- Do children prefer direct control or emergent behavior?
- Does learning through experience create stronger attachment?
- How do they understand practice → skill relationships?

---

### 2. Memory Theater ✅ COMPLETE
**Port:** 5181
**Question:** How should agents remember?
**Contrast:** Narrative story timeline vs. searchable database

**Implementation:**
- 2 distinct viewing modes
- **Narrative Mode:** Visual timeline with cause-and-effect connections between memories
- **Database Mode:** Searchable table with tags, types, emotions
- Full memory editing (content, tags, emotions, causal links)
- Search and filter capabilities

**What We Learn:**
- Do children think narratively or categorically about memory?
- Which model helps understand agent behavior better?
- How does memory organization affect perceived personality?

---

### 3. Perception Lab ⚠️ SCAFFOLDED
**Port:** 5182
**Question:** How do children understand perception?
**Contrast:** Single modality vs. multimodal sensory input

**Status:** Vite + React + Tailwind setup complete, implementation pending

**Planned Features:**
- 5 perception modalities (text, vision, audio, files, web)
- Each has different resource costs
- Challenge scenarios requiring specific modalities
- Cost/benefit trade-off learning

---

### 4. Tool Forge ⚠️ SCAFFOLDED
**Port:** 5183
**Question:** How should children interact with tools?
**Contrast:** Pre-made tools vs. compositional building blocks

**Status:** Vite + React + Tailwind setup complete, implementation pending

**Planned Features:**
- **Toolbox Mode:** 20 ready-made tools
- **Forge Mode:** Compose from 5 primitives (read, write, transform, call, loop)
- Visual programming interface (Scratch-like)
- Tool testing sandbox

---

### 5. Agent Orchestra ⚠️ SCAFFOLDED
**Port:** 5184
**Question:** How should multiple agents coordinate?
**Contrast:** Hierarchical (manager/worker) vs. peer-to-peer

**Status:** Vite + React + Tailwind setup complete, implementation pending

**Planned Features:**
- **Hierarchy Mode:** Central manager delegates to workers
- **Collective Mode:** Peer-to-peer emergent coordination
- Live collaboration visualization
- Side-by-side comparison mode

---

## Shared Infrastructure

All prototypes share:
- **Components:** `AgentAvatar.jsx`, `ConfigPanel.jsx`
- **Utilities:** `agentUtils.js` with common agent functions
- **Technology:** React 18 + Vite 5 + Tailwind CSS 3
- **Design Language:** Consistent visual style and interaction patterns

## How to Use

### Start All Prototypes
```bash
cd /Users/wz/Desktop/zPersonalProjects/AICraft/prototypes
./start_all.sh
```

This launches all 5 prototypes on ports 5180-5184

### Start Individual Prototypes
```bash
cd prototypes/evolution-playground && npm run dev  # Port 5180
cd prototypes/memory-theater && npm run dev        # Port 5181
# etc.
```

### Stop All Prototypes
```bash
cd /Users/wz/Desktop/zPersonalProjects/AICraft/prototypes
./stop_all.sh
```

---

## Comparative Observation Framework

### Testing Strategy

**Group A (Sequential):** One prototype per day, observe learning progression

**Group B (Choice):** All prototypes available, track which they choose

**Group C (Paired):** A/B test specific contrasts

### Metrics to Track

1. **Engagement:** Time spent, actions taken, configurations tried
2. **Understanding:** Prediction accuracy, explanation quality
3. **Preference:** Which mode chosen when given options
4. **Transfer:** Can insights from one prototype inform others?
5. **Age/Skill Variations:** Do different groups prefer different approaches?

---

## Key Design Questions Answered

| Dimension | Prototypes | Key Insight Sought |
|-----------|-----------|-------------------|
| **Growth Mechanism** | Evolution Playground | Config vs. learned behavior |
| **Memory Model** | Memory Theater | Narrative vs. database structure |
| **Perception** | Perception Lab | Single vs. multimodal trade-offs |
| **Tool Abstraction** | Tool Forge | Pre-made vs. compositional |
| **Coordination** | Agent Orchestra | Hierarchical vs. emergent |

---

## Implementation Status

### Complete (2/5)
- ✅ Evolution Playground - Full 3-mode system with tasks
- ✅ Memory Theater - Dual viewing modes with editing

### Scaffolded (3/5)
- ⚠️ Perception Lab - Setup ready, needs app implementation
- ⚠️ Tool Forge - Setup ready, needs app implementation
- ⚠️ Agent Orchestra - Setup ready, needs app implementation

All scaffolded prototypes have:
- Vite + React configured
- Tailwind CSS installed
- Shared components copied
- Port assignments configured (5182-5184)

---

## Next Steps

### Immediate
1. **Test the 2 complete prototypes** with children
2. **Gather initial feedback** on the comparative approach
3. **Complete remaining 3 prototypes** based on learnings

### Short-term
1. **Implement Perception Lab** - Most straightforward of remaining 3
2. **Add LLM integration** to all prototypes for dynamic responses
3. **Build analytics dashboard** to track metrics across prototypes

### Medium-term
1. **Run full comparative study** with all 5 prototypes
2. **Analyze which designs** lead to best learning outcomes
3. **Synthesize findings** into final AICraft design

---

## Why This Approach?

**Comparatively Structured Observation** lets us:

1. **Isolate variables:** Each prototype tests one specific design dimension
2. **Create observable contrasts:** Direct A/B comparisons (narrative vs. database)
3. **Enable systematic comparison:** Collect data across multiple children
4. **Surface implicit assumptions:** Reveal what we think vs. what works
5. **Generate actionable insights:** Clear guidance for final AICraft design

This is better than building one prototype because we learn:
- Not just "does this work?" but "which works better?"
- Not just aggregate metrics but individual preferences
- Not just initial reactions but sustained engagement patterns

---

## Technical Details

### File Structure
```
prototypes/
├── shared/
│   ├── components/
│   │   ├── AgentAvatar.jsx
│   │   └── ConfigPanel.jsx
│   └── utils/
│       └── agentUtils.js
├── evolution-playground/  (COMPLETE)
├── memory-theater/        (COMPLETE)
├── perception-lab/        (SCAFFOLDED)
├── tool-forge/            (SCAFFOLDED)
├── agent-orchestra/       (SCAFFOLDED)
├── start_all.sh
├── stop_all.sh
└── README.md
```

### Dependencies
- React 18
- Vite 5
- Tailwind CSS 3
- No backend required (mock data for now)

### Build Times
- Evolution Playground: ~2-3 hours
- Memory Theater: ~2-3 hours
- Remaining prototypes: ~2-3 hours each estimated

---

## Alignment with AICraft Vision

All prototypes follow the core design principles:

1. **Primitives over curriculum** ✓
   - Evolution: 4 capability primitives
   - Memory: Memory types as building blocks

2. **Low floor, high ceiling** ✓
   - Easy to start (simple mode selection)
   - Endless depth (countless combinations)

3. **Microworld reflects world** ✓
   - Agent growth mirrors real learning
   - Memory organization mirrors cognition

4. **Artistically captivating** ✓
   - Gradient backgrounds
   - Smooth animations
   - Emoji-based visual language

---

## Reflection

This prototype suite represents a **research-driven approach** to building AICraft:

- Instead of building based on intuition, we're **testing hypotheses**
- Instead of one path, we're **exploring alternatives**
- Instead of guessing preferences, we're **observing behavior**

The goal: Build the **most effective** agent-raising environment based on **empirical evidence** from real children.

---

**Created:** November 8, 2024
**Authors:** Warren Zhu & Matthew Kotzbauer
**Status:** 2/5 complete, 3/5 scaffolded, ready for initial testing
