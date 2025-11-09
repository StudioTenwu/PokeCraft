# AICraft Prototypes - User Experience Exploration

## Overview
Based on the AICraft vision document, we're exploring 5 key user experiences through interactive prototypes. Each prototype focuses on a specific aspect of the agent-raising experience.

## 5 Key User Experiences

### 1. **Agent Evolution Dashboard** (Port 5173)
**Director Mode - Pokemon-style Agent Growth**
- Configure 4 primitives: Perception, Memory, Tools, Communication
- Visual stat system showing agent capabilities
- Watch agent respond immediately to new abilities
- See capabilities unlock and grow

### 2. **Observer View** (Port 5174)
**First-Person Agent Experience**
- Step into your agent's perspective
- Experience constrained perception and memory
- View agent's internal thoughts and reasoning
- Edit memories to help agent process experiences ("therapy mode")
- Understand agent limitations viscerally

### 3. **Artifact Canvas** (Port 5175)
**Creation Playground**
- Watch agent create in real-time (drawings, text, code, calculations)
- Gallery of everything the agent has made
- Export artifacts to use elsewhere
- Visual feedback of agent creativity growing

### 4. **Quest System** (Port 5176)
**Progressive Discovery Through Challenges**
- Non-linear learning through scenarios
- Agent struggles with tasks → child discovers solutions
- Unlock primitives through understanding, not instructions
- "Aha!" moments emerge naturally

### 5. **Multi-Agent Arena** (Port 5177)
**Agent Collaboration & Societies**
- Create multiple agents with different capabilities
- Watch them communicate and collaborate
- Compare personalities (Haiku vs Sonnet vs Ollama)
- Emergent social behaviors and problem-solving

---

## Launch All Prototypes

```bash
cd /Users/wz/Desktop/zPersonalProjects/AICraft
python3 start_all_prototypes.py
```

Wait 10-15 seconds, then open:
- **Evolution Dashboard**: http://localhost:5173
- **Observer View**: http://localhost:5174
- **Artifact Canvas**: http://localhost:5175
- **Quest System**: http://localhost:5176
- **Multi-Agent Arena**: http://localhost:5177

---

## Design Principles (from AICraft.txt)

1. **Primitives over curriculum** - Composable building blocks, not linear tutorials
2. **Low floor, high ceiling** - Easy to start, endless to master
3. **Microworld reflects world** - Skills transfer to real scenarios

---

## Troubleshooting

**Port already in use?**
```bash
# Kill processes on specific ports
lsof -ti:3000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
lsof -ti:5174 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:8002 | xargs kill -9
```

**Dependencies not installed?**
```bash
# For each prototype's frontend:
cd <prototype>/frontend && npm install

# For prototypes 3 & 4 backend:
cd <prototype>/backend && pip install -r requirements.txt
```

**Prototype 3 needs API key:**
```bash
cd prototypes/prototype3/backend
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

---

## Next Steps

Once all three are running, try:
1. **Compare UX**: Which is most intuitive?
2. **Test learning**: Can you discover without instructions?
3. **Identify favorite**: Which prototype excites you most?

Enjoy exploring! 🎨✨
