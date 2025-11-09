# AICraft: Functional Requirements Document

**Version:** 1.0
**Date:** November 8, 2024
**Authors:** Warren Zhu & Matthew Kotzbauer

---

## Executive Summary

AICraft is an agent-raising environment where children **build and configure AI agents** to complete real-world tasks, not complete tasks *about* AI. The core activity is **engineering the agent**, not doing the work themselves.

### Key Principle

**Children are ENGINEERS, not WORKERS.**

```
❌ Wrong: "Write a poem" (child does the work)
✅ Right: "Build an agent that can write poems" (child engineers the solution)

❌ Wrong: "Identify this image" (child identifies)
✅ Right: "Build an agent that can identify images" (child configures vision)

❌ Wrong: "Debug this code" (child debugs)
✅ Right: "Build an agent that can debug code" (child adds debugging tools)
```

---

## 1. Core User Experience

### 1.1 The Agent Engineering Loop

```
┌─────────────────────────────────────────┐
│  1. Encounter Real-World Task           │
│     "A user needs help writing poetry"  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  2. Analyze Requirements                │
│     "What does my agent need to do this?"│
│     - Text generation? ✓                │
│     - Creative examples? Need web search│
│     - Remember user's style? Need memory│
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  3. Configure Agent                     │
│     Add: Web Search capability          │
│     Add: Long-term memory               │
│     Adjust: Creativity level → High     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  4. Deploy & Watch                      │
│     Agent attempts task autonomously    │
│     Child WATCHES agent work            │
│     Success or failure?                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  5. Iterate                             │
│     If failed: What was missing?        │
│     Add capabilities, retry             │
│     If succeeded: Try harder task       │
└─────────────────────────────────────────┘
```

### 1.2 What the Child Does vs. What the Agent Does

| Child's Role (Engineer) | Agent's Role (Worker) |
|------------------------|----------------------|
| Analyze task requirements | Execute the task |
| Configure capabilities | Use capabilities |
| Add tools | Use tools |
| Set personality/strategy | Apply personality |
| Debug failures | Attempt solutions |
| Iterate on design | Perform work |
| **Think about HOW** | **Do the WHAT** |

---

## 2. Task Design Requirements

### 2.1 Task Categories: Real-World Problems

Tasks should be **authentic problems that real users have**, not artificial "AI exercises."

**✅ Good Task Examples:**

1. **"Help Users" Category**
   - "A busy parent needs dinner recipe suggestions"
   - "A student needs help organizing their notes"
   - "A teacher needs to generate quiz questions from a textbook"
   - "A writer needs feedback on their story"

2. **"Create Things" Category**
   - "Design birthday party invitations"
   - "Generate social media content for a business"
   - "Create educational flashcards from lecture notes"
   - "Build a simple game or interactive story"

3. **"Solve Problems" Category**
   - "Analyze why a website is slow"
   - "Find and fix bugs in code"
   - "Organize messy data into a spreadsheet"
   - "Research and compare product options"

4. **"Automate Tasks" Category**
   - "Monitor news for specific topics"
   - "Send reminders based on calendar"
   - "Categorize and file emails"
   - "Generate weekly summaries of activity"

**❌ Bad Task Examples (Meta-tasks about AI):**
- "Write a poem about AI"
- "Explain how neural networks work"
- "Describe what an AI agent is"
- "List the benefits of machine learning"

### 2.2 Task Structure

Every task must have:

```javascript
const task = {
  // Real-world context
  scenario: "A user named Alice is planning her friend's birthday",
  request: "She needs creative invitation text that's fun and exciting",

  // What the agent needs (not revealed upfront)
  requiredCapabilities: [
    'text_generation',
    'web_search', // for invitation examples
    'creativity_tuning'
  ],

  optionalCapabilities: [
    'image_generation', // for visual invitations
    'memory' // to remember Alice's friend's interests
  ],

  // Success criteria (objective)
  successConditions: {
    containsKey: ['party details', 'excitement', 'RSVP info'],
    creativity: 'high',
    length: '50-150 words'
  },

  // What child learns
  designLessons: [
    "Text generation alone isn't enough for creative tasks",
    "Web search helps find inspiration/examples",
    "Creativity parameter affects output tone"
  ]
}
```

### 2.3 Progression Through Complexity

**Level 1 (Tutorial): Single Capability**
- Tasks require exactly 1 capability
- Clear cause-effect: "No vision? Can't see image!"
- Example: "Read this text message and reply"

**Level 2 (Basic): Two Capabilities**
- Tasks need 2 capabilities working together
- Introduction to composition
- Example: "Search web + generate summary"

**Level 3 (Intermediate): Multi-Capability + Strategy**
- 3+ capabilities
- Child must choose strategy (creative vs. factual)
- Example: "Research topic + write engaging article"

**Level 4 (Advanced): Memory + Personalization**
- Agent must remember previous interactions
- Adapt to user preferences
- Example: "Weekly newsletter personalized to user interests"

**Level 5 (Expert): Multi-Agent Coordination**
- Multiple agents with different specializations
- Delegation and collaboration
- Example: "Content creation pipeline: Research → Write → Edit → Format"

---

## 3. Map-Based World Design

### 3.1 Environment = Use Case Context

Each environment represents a **real-world use case**, not an AI concept.

**✅ Good Environments:**

**🏠 Home Helper Hub**
- Context: Helping with household tasks
- Tasks: Recipe suggestions, shopping lists, schedule coordination
- Unlocks: Basic text, web search, memory

**🎨 Creative Workshop**
- Context: Making art, stories, designs
- Tasks: Story generation, image creation, music composition
- Unlocks: Image generation, creativity tuning, style transfer

**📚 Study Companion**
- Context: Learning and education
- Tasks: Quiz generation, note summarization, concept explanation
- Unlocks: Document reading, knowledge retrieval, teaching mode

**💼 Productivity Office**
- Context: Work and organization
- Tasks: Email drafting, data organization, meeting summaries
- Unlocks: File access, calendar integration, task management

**🎮 Game Maker Studio**
- Context: Interactive experiences
- Tasks: Game logic, NPC dialogue, puzzle generation
- Unlocks: Code execution, state management, interaction design

**🤝 Community Center**
- Context: Helping others, social good
- Tasks: Accessibility features, translation, content moderation
- Unlocks: Multi-language, accessibility tools, safety filters

**❌ Bad Environments (Abstract AI concepts):**
- "Vision Dojo" - too abstract
- "Memory Temple" - doesn't reflect real use
- "Code Colosseum" - coding is a tool, not a context

### 3.2 Task Discovery in Environments

**Random Encounters** should feel like **real user requests**:

```
╔══════════════════════════════════════════╗
║  A Wild Request Appeared!                ║
╠══════════════════════════════════════════╣
║                                          ║
║  👤 "Hi! I'm Sarah, a teacher.           ║
║      I need help creating a quiz         ║
║      from this chapter. Can your         ║
║      agent help me?"                     ║
║                                          ║
║  📄 [Attached: Biology Chapter 3]        ║
║                                          ║
║  [🤖 Try to Help] [🏃 Skip]              ║
╚══════════════════════════════════════════╝
```

NOT:
```
❌ "Challenge: Process this document"
❌ "Test your agent's comprehension"
```

### 3.3 Boss Encounters = Complex Projects

Each environment has a **capstone project** that requires full mastery:

**Home Helper Hub Boss:**
"Plan an entire week of meals, create shopping list, generate recipes, all personalized to dietary restrictions"

**Creative Workshop Boss:**
"Create a complete illustrated children's storybook with consistent characters and engaging narrative"

**Study Companion Boss:**
"Be a personal tutor for an entire subject, adapting to learning style and tracking progress"

---

## 4. Agent Configuration Interface

### 4.1 Configuration is THE Gameplay

The core interaction is **configuring the agent**, not using it.

**Required Interface Elements:**

1. **Capability Selector**
   - Visual cards for each capability
   - Shows: Name, description, cost (energy/complexity)
   - Locked until level requirement
   - Drag-and-drop or toggle to enable

2. **Strategy Tuner**
   - Sliders for abstract parameters:
     - Creativity (factual ←→ imaginative)
     - Verbosity (concise ←→ detailed)
     - Formality (casual ←→ professional)
     - Speed vs. Quality
   - These affect HOW agent uses capabilities

3. **Memory Manager**
   - What should agent remember?
   - Long-term facts vs. short-term context
   - Privacy/forget controls

4. **Tool Workshop**
   - Browse available tools
   - Configure tool parameters
   - Chain tools together (advanced)

5. **Personality Designer**
   - Agent's "voice" and style
   - Helpful, funny, formal, enthusiastic, etc.
   - Examples: "Like a teacher", "Like a friend", "Like an expert"

### 4.2 Feedback: Watch Agent Work

After configuration, child **observes agent** attempting task:

```
╔══════════════════════════════════════════╗
║  Your Agent is Working...                ║
╠══════════════════════════════════════════╣
║  Agent: "Let me search for examples..."  ║
║  🔍 Using: Web Search                    ║
║  ✓ Found 5 invitation examples           ║
║                                          ║
║  Agent: "Analyzing fun language..."      ║
║  🧠 Using: Text Analysis                 ║
║  ✓ Identified playful tone               ║
║                                          ║
║  Agent: "Generating invitation..."       ║
║  ✍️ Using: Creative Text Generation      ║
║  ✓ Draft complete!                       ║
║                                          ║
║  [View Output] [Retry] [Adjust Agent]    ║
╚══════════════════════════════════════════╝
```

**Key: Child WATCHES, doesn't DO**

### 4.3 Success/Failure Analysis

When agent fails, system helps child **diagnose the problem**:

```
╔══════════════════════════════════════════╗
║  Task Failed: Invitation Too Generic     ║
╠══════════════════════════════════════════╣
║  What went wrong?                        ║
║                                          ║
║  ❌ Agent couldn't find creative         ║
║     examples because it has no          ║
║     Web Search capability               ║
║                                          ║
║  💡 Suggestion: Add Web Search to       ║
║     find inspiration                    ║
║                                          ║
║  ❌ Agent used very formal tone because ║
║     Creativity slider is set to Low     ║
║                                          ║
║  💡 Suggestion: Increase Creativity     ║
║     slider for fun tasks                ║
║                                          ║
║  [Add Web Search] [Adjust Creativity]    ║
╚══════════════════════════════════════════╝
```

This teaches **debugging and iteration** without the child doing the task.

---

## 5. Progression & Unlocking

### 5.1 What Unlocks?

**Capabilities** (the tools):
- Basic: Text generation, reading
- Intermediate: Web search, vision, memory
- Advanced: Code execution, image generation
- Expert: Multi-agent coordination, fine-tuning

**Environments** (the contexts):
- Level 1: Home Helper
- Level 3: Creative Workshop, Study Companion
- Level 6: Productivity Office, Game Maker
- Level 10: Community Center

**Parameters** (the strategies):
- Level 1: Creativity, Verbosity
- Level 4: Formality, Speed/Quality
- Level 7: Custom strategy creation

### 5.2 How You Level Up

**XP is earned by:**
1. Successfully deploying agent to complete task (100 XP)
2. Improving agent after failure (50 XP)
3. Completing all tasks in environment (200 XP bonus)
4. Creative solutions (bonus XP)

**NOT earned by:**
- Completing tasks yourself
- Spending time in interface
- Random exploration (unless encountering tasks)

### 5.3 Badges & Achievements

**Specialist Badges:**
- 🏠 "Home Helper Expert" - Complete all home tasks
- 🎨 "Creative Director" - Complete all creative tasks
- 📚 "Study Sensei" - Complete all education tasks

**Engineering Badges:**
- 🔧 "Tool Master" - Use all available tools
- 🧩 "Problem Solver" - Fix 10 failed deployments
- ⚡ "Efficient Engineer" - Complete task with minimal capabilities
- 🎯 "Perfectionist" - Get 5 perfect scores

**Discovery Badges:**
- 🗺️ "Explorer" - Visit all environments
- 🎲 "Risk Taker" - Accept 20 random encounters
- 👑 "Champion" - Beat all boss encounters

---

## 6. First-Person "Empathy Mode"

### 6.1 Purpose

Help child understand **what it's like to be the agent** with limited capabilities.

### 6.2 How It Works

**Switch Perspective:**
```
Normal Mode: Configure agent → Deploy → Watch
Empathy Mode: Become agent → Try task yourself → Feel constraints
```

**Example Flow:**

1. **Task:** "Help user book a restaurant reservation"

2. **Child enters Empathy Mode:**
   ```
   You are the agent. You have:
   - Text generation ✓
   - Web access ✗
   - Memory ✗
   - Phone calling ✗

   User asks: "Book me a table at Mario's for 7pm tonight"

   What can you do?
   > _________________________________
   ```

3. **Child tries:**
   - "I'll search for Mario's phone number" → ❌ No web access
   - "I'll call them" → ❌ No phone tool
   - "Let me remember where it is" → ❌ No memory

4. **Aha moment:**
   ```
   💡 You felt frustrated because you were missing tools!

   This is what your agent feels like without:
   - Web Search (to find contact info)
   - Phone/API tool (to actually book)
   - Memory (to remember user preferences)

   [Exit Empathy Mode] [Add These Capabilities]
   ```

### 6.3 When to Use Empathy Mode

**Required:**
- Tutorial tasks (teach the concept)
- After 3 consecutive failures (help diagnose)

**Optional:**
- Any time via "👀 Experience as Agent" button
- Before deploying to preview constraints

---

## 7. Pokemon-Style "Battles"

### 7.1 Framing Tasks as Encounters

Tasks are presented as **challenges to overcome**, not tests to pass.

**Battle UI:**

```
╔══════════════════════════════════════════╗
║  CREATIVE CHALLENGE                      ║
╠══════════════════════════════════════════╣
║                                          ║
║  YOUR AGENT              CHALLENGE       ║
║  Level 5 🤖              Write Birthday  ║
║  ████████░░ 80%          Invitation      ║
║                          ★★☆☆☆           ║
║  Capabilities:           Difficulty: 2   ║
║  • Text Gen ✓                           ║
║  • Web Search ✓          Requires:       ║
║  • Creativity ✓          • Text Gen      ║
║                          • Creativity    ║
║  ┌────────────────────────────────────┐ ║
║  │ Agent: "Searching for examples..." │ ║
║  │ ⚡ Using Web Search (-10 energy)   │ ║
║  │ ✓ Found 5 examples!                │ ║
║  │                                    │ ║
║  │ Agent: "Generating invitation..."  │ ║
║  │ ✍️ Using Creative Text Gen         │ ║
║  │                                    │ ║
║  │ "🎉 You're Invited! Join us for    │ ║
║  │  an unforgettable celebration...  │ ║
║  └────────────────────────────────────┘ ║
║                                          ║
║  User Feedback: ⭐⭐⭐⭐⭐ "Perfect!"      ║
║  +150 XP | +1 Creative Badge Progress   ║
╚══════════════════════════════════════════╝

[⚔️ Next Challenge] [🔧 Improve Agent] [📊 Stats]
```

### 7.2 "Gym Leaders" = Themed Challenges

Each environment has a **boss user** with a complex, multi-step need:

**Home Helper Boss: "The Busy Parent"**
```
"Hi! I'm Sam, a parent of 3. I need help with:
1. Weekly meal planning (dietary restrictions)
2. Shopping list generation
3. Recipe instructions
4. Leftover management

Can your agent handle all of this?"

Requires: Memory, Web Search, Text Gen, Reasoning
Reward: 500 XP, Home Helper Champion Badge
```

**Creative Workshop Boss: "The Author"**
```
"I'm writing a children's book and need:
1. Character consistency across 10 pages
2. Engaging narrative arc
3. Illustrations that match story
4. Age-appropriate language

Can your agent be my creative partner?"

Requires: Image Gen, Long-term Memory, Text Gen, Creativity
Reward: 500 XP, Creative Director Badge
```

---

## 8. Exportable Agents

### 8.1 Agent as Artifact

The final product is **the configured agent**, not the task outputs.

**Export Options:**

1. **Save Configuration**
   ```json
   {
     "name": "My Creative Helper",
     "capabilities": ["text_gen", "web_search", "image_gen"],
     "personality": "enthusiastic",
     "creativity": 0.8,
     "memory_enabled": true
   }
   ```

2. **Share with Friends**
   - Generate shareable code
   - Others can import your agent
   - Remix and improve

3. **Deploy to Real APIs** (advanced)
   - Export as Claude prompt
   - Use in actual applications
   - "Real-world transfer"

### 8.2 Agent Collection

Like Pokemon, children collect and curate agents:

**My Agents:**
- 🏠 "Home Helper Max" - Specialized in recipes & schedules
- 🎨 "Creative Spark" - High creativity, makes art and stories
- 📚 "Study Buddy" - Explains concepts, generates quizzes
- 💼 "Work Assistant" - Formal, organized, detail-oriented

**View Collection** shows:
- Agent stats and specializations
- Tasks they've completed
- Success rate
- Unique configurations

---

## 9. Technical Requirements

### 9.1 Backend: Mock vs. Real LLM

**Phase 1 (Current): Mock Responses**
- Pre-scripted agent behaviors
- Deterministic success/failure
- Fast iteration, no API costs

**Phase 2 (Future): Real LLM Integration**
- Claude API / Ollama
- Actual agent execution
- Real task completion

**Both phases must:**
- Show realistic agent "thinking" process
- Demonstrate tool usage
- Produce actual task outputs

### 9.2 Frontend Requirements

**Must Have:**
- Visual capability selector (cards or tiles)
- Real-time agent work visualization
- Task output display
- Configuration persistence (localStorage)
- XP/level progress tracking

**Nice to Have:**
- Animated agent avatar
- Sound effects for success/failure
- Confetti on level up
- Dark mode

### 9.3 Data Structure

```javascript
// Agent Configuration
const agentConfig = {
  capabilities: ['text_gen', 'web_search'],
  parameters: {
    creativity: 0.7,
    verbosity: 0.5,
    formality: 0.3
  },
  memory: {
    enabled: true,
    shortTerm: [],
    longTerm: []
  },
  tools: ['search_web', 'generate_text', 'read_document']
};

// Task Definition
const task = {
  id: 'creative_invitation_01',
  environment: 'home_helper',
  type: 'random_encounter',
  scenario: "Sarah needs party invitation",
  difficulty: 2,
  requiredCapabilities: ['text_gen'],
  recommendedCapabilities: ['web_search', 'creativity'],
  successCriteria: {
    hasElements: ['party_details', 'excitement'],
    minCreativity: 0.6
  }
};

// User Progress
const userProgress = {
  level: 5,
  xp: 750,
  unlockedCapabilities: ['text_gen', 'web_search', 'vision'],
  unlockedEnvironments: ['home_helper', 'creative_workshop'],
  badges: ['home_helper_expert', 'creative_novice'],
  completedTasks: ['task_001', 'task_002'],
  agentCollection: [agentConfig1, agentConfig2]
};
```

---

## 10. Success Metrics

### 10.1 Learning Outcomes

Children should be able to:

1. **Analyze** a task to determine required capabilities
2. **Configure** an agent with appropriate tools and parameters
3. **Debug** agent failures by identifying missing capabilities
4. **Iterate** on agent design to improve performance
5. **Transfer** knowledge to new contexts ("This is like that other task...")

### 10.2 Engagement Metrics

Track:
- Time spent configuring (should be high)
- Number of iterations per task (should increase with learning)
- Variety of configurations tried (exploration)
- Return rate (re-engagement)

### 10.3 Evidence of Understanding

Look for:
- Predictive behavior ("I think this task needs vision")
- Efficient solutions (minimal capabilities, maximum effect)
- Creative configurations (unexpected combinations that work)
- Self-explanation ("I added memory because...")

---

## 11. MVP Scope

### What to Build First

**Core Loop (Must Have):**
1. ✅ Task selection (from 1 environment)
2. ✅ Capability configuration (3-5 capabilities)
3. ✅ Agent deployment visualization
4. ✅ Success/failure feedback
5. ✅ Iteration (reconfigure and retry)

**Progression (Should Have):**
6. ✅ XP and leveling
7. ✅ 2-3 environments
8. ✅ 10-15 tasks total
9. ✅ Capability unlocking

**Polish (Nice to Have):**
10. ⚠️ Pokemon-style battle UI
11. ⚠️ Agent collection
12. ⚠️ Empathy mode
13. ⚠️ Real LLM integration

---

## 12. Design Principles Summary

### The Core Insight

**Children should BUILD agents, not BE agents.**

They are **engineers**, not **workers**.

### The Golden Rule

Every task should be answerable with:
**"How should I configure my agent to handle this?"**

NOT:
"How do I do this myself?"

### The Test

If you can complete the task without thinking about agent capabilities, **it's the wrong task**.

✅ Right: Forces configuration thinking
❌ Wrong: Just doing work

---

**End of Functional Requirements v1.0**

Next: Prototype implementation based on these requirements.
