# Agent Engineering Playground

**Learn Agent Engineering Through Play**

An interactive, browser-based course where learners build and configure AI agents to solve progressively complex tasks in a Minecraft-inspired grid world.

## 🎯 Vision

> "Children learn the most in play, not in rote education."

This project embodies a philosophy: **AI enables play-based learning** by creating infinitely varied, interactive environments and making learning artifacts visible and exportable.

### What Makes This Different

- **No coding required**: Design agents using natural language
- **Immediate feedback**: See your agent think and act in real-time
- **Progressive complexity**: From simple navigation to multi-agent systems
- **Real-world transfer**: Export your agent to run in other environments

## 🎮 Course Structure

### Level 1: Hello, Agent (5 min)
Learn to control agent behavior with natural language prompts.
- **Environment**: Simple 5x5 grid with goal
- **Tools**: Basic movement commands
- **Learn**: Prompt engineering basics

### Level 2: Tool Use (10 min)
Teach agents to use tools strategically.
- **Environment**: Resource collection (wood, stone, crafting)
- **Tools**: `collect()`, `craft()`, `check_inventory()`
- **Learn**: Tool selection and sequencing

### Level 3: Planning & Reasoning (15 min)
Introduce ReAct-style chain-of-thought reasoning.
- **Environment**: Maze with locked doors, keys, pressure plates
- **Tools**: Exploration and reasoning
- **Learn**: How agents plan and debug their thinking

### Level 4: Multi-Agent Collaboration (20 min)
Design agents that work together.
- **Environment**: Collaborative building tasks
- **Tools**: Agent communication primitives
- **Learn**: Coordination and role specialization

### Level 5: Reward Shaping (15 min)
Understand how incentives shape behavior.
- **Environment**: Open world with multiple goals
- **Tools**: Custom reward function designer
- **Learn**: Alignment and unintended consequences

### Level 6: Real-World Export (Capstone)
Take your agent beyond the playground.
- Export to Minecraft mod
- Export to robot simulator
- Share as API

## 🏗️ Technical Architecture

### Backend (Python)
- **Agent Executor**: LLM-powered ReAct loop
- **Environment Engine**: Grid-based world simulation
- **API**: FastAPI server with WebSocket support

### Frontend (React)
- **Grid Renderer**: 2D pixel-art visualization
- **Prompt Editor**: Interactive agent configuration
- **Reasoning Trace**: Live view of agent's thoughts

### No Training Required
Agents use LLM reasoning directly (like AutoGPT/BabyAGI) for instant feedback.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- API key from one of: [Anthropic](https://console.anthropic.com/), [OpenAI](https://platform.openai.com/), or [Google AI Studio](https://makersuite.google.com/app/apikey) (for Gemini)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/RLCraft.git
cd RLCraft

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your API key to .env

# Frontend setup
cd ../frontend
npm install

# Run development servers
# Terminal 1 (backend)
cd backend
python -m uvicorn src.api.main:app --reload

# Terminal 2 (frontend)
cd frontend
npm run dev
```

Visit `http://localhost:5173` to start learning!

## 📖 Project Structure

```
RLCraft/
├── backend/
│   ├── src/
│   │   ├── agent/          # LLM agent executor and ReAct loop
│   │   ├── environment/    # Grid world, entities, tools
│   │   ├── api/            # FastAPI routes and WebSocket handlers
│   │   └── models/         # Data models and schemas
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components (GridWorld, PromptEditor, etc.)
│   │   ├── pages/          # Level pages
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Helper functions
│   ├── public/
│   └── package.json
├── docs/                   # Course content and guides
├── assets/                 # Images, sprites, sounds
└── README.md
```

## 🎨 Design Philosophy

### 1. Immediate Feedback
Every prompt change shows new behavior in seconds. No waiting for training.

### 2. Transparency
Show the agent's reasoning trace. Learners debug by reading agent thoughts.

### 3. Progressive Complexity
Start with 1 tool and 1 task. End with multi-agent systems and custom rewards.

### 4. Open-Ended Creativity
Later levels: "Design your own challenge." Gallery of learner creations.

### 5. Export/Transfer
Learned patterns apply to real agent engineering. Deploy these agents in production.

## 🤝 Contributing

This is an open-source educational project. Contributions welcome!

### Ways to Contribute
- Add new levels and challenges
- Improve environment physics
- Design new agent architectures
- Create export targets (new environments)
- Enhance UI/UX

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📚 Learning Resources

- [What is Agent Engineering?](docs/agent-engineering.md)
- [ReAct Explained](docs/react-pattern.md)
- [Prompt Engineering Guide](docs/prompt-guide.md)
- [Tool Use Best Practices](docs/tool-design.md)

## 🗺️ Roadmap

### Phase 1: Core Loop (Current)
- [ ] Basic grid environment
- [ ] LLM-based agent executor
- [ ] React UI with live visualization
- [ ] Level 1 & 2 content

### Phase 2: Course Content
- [ ] Levels 3-5 with progressive challenges
- [ ] Hint system (LLM-generated)
- [ ] Progress tracking

### Phase 3: Export & Share
- [ ] Export agent config (JSON)
- [ ] Gallery of solutions
- [ ] Leaderboard (optional)

### Phase 4: Advanced Features
- [ ] Minecraft mod integration
- [ ] Robot simulator export
- [ ] Multi-user collaboration

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built on the philosophy that **play is the natural learning interface** and **AI can make learning artifacts visible**.

Inspired by:
- Constructionist learning theory (Seymour Papert)
- Agent-based modeling education
- Interactive coding environments (Scratch, Code.org)

---

**Start your agent engineering journey today!**

Questions? Open an issue or reach out: [fuchengwarrenzhu@gmail.com](mailto:fuchengwarrenzhu@gmail.com)
