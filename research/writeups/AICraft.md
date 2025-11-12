Cofounders: Matthew Kotzbauwer (https://www.linkedin.com/in/matt-kotzbauer-a86a35174/) and Warren Zhu (warrenzhu.com). matthewkotzbauer@college.harvard.edu, wzhu@college.harvard.edu.

# Our Secret

Children learn the most in play, not in rote education. Play follows the child's own developmental trajectory and fosters their holistic skill acquisition (their growth as a human being) beyond the accumulation of knowledge.

However, there are two things that interfere with a child's ability to play. First, the child requires an environment to play. Different environments provide affordances for different playful behavior, and facilitates different forms of learning. The development of such good environments has been historically prohibitively expensive. Secondly, there are stakeholders (e.g. parents, teachers, other adults, even the child themself) in a child's life who are anxious to see them learn. Playing often doesn't provide a sense that the child is learning, partly because it is too fun, and partly because play, by its nature, does not progress in a smooth developmental trajectory with quantifiable benchmarks, making the child's development more difficult to track.

We believe that AI technology solves both barriers. 
The recent advances in AI I believe has the potential to do this because AI technology is so flexible that it can finally create immersive and interactive experiences. It can also enable a level of play never seen before because computers can finally reason, think, and to a limited extent, feel. AI Agents are our closest model to human beings. RL environments are our best simulation of the world. LLMs are our best model of human language. By exposing children to games based on these flexible AI Agents. Enabling them to interact with them, play with them, children are able to best understand the social world around them. In time, they can export experiences that they had inside the game world to outside of it, given that AI agents are such general purpose technologies. E.g. The child trains an AI agent to do a certain task inside Minecraft, then they export it to a robot and have it do the same task outside. 

To summarize: AI creates simple, declarative ways of creating new interactive experiences. Further, AI, as a translation layer, enables children to translate the personal skills they have learned into observable artifacts easily.

Imagine this: A child engages in a world in minecraft where they collaborate with AI Agents to accomplish a task. They can customize their AI agents in natural language, either through prompt engineering, through specifying tools that the agent can use, or through a simple API for agent fine-tuning. After accomplishing this task, the child can export the final agent scaffold and model to be adapted to other worlds, e.g. 

# The prototype: AICraft

## Overview

AICraft is an agent-raising environment, a microworld where children nurture and grow an AI agent from a basic language model into a capable creative and life partner. After raising the agent, they become deployable "Pokemons". 

AICraft follows the following design principles. Principle 1 and 2 are taken from Papert's discussion of microworlds (https://stager.org/articles/papert_microWorlds_chapter.pdf). Principle 3 comes from concepts in Chinese Internet Sci-Fi that Warren absorbed from an early age. Principle 4 comes from Matt's obsession with compelling art.

1. **Primitives over curriculum.** Instead of linear tutorial/fixed learning path, one should provide composable primitives (Perception, Memory, Tools, Communication) that the player can explore freely. The player learns not through instruction, but through exposure in experimentation and discovery. The learner come to construct objects based on the primitives provided in order to understand these primitives better.

2. **Low floor, high ceiling.** The system should be easy to begin with (think simple Pokemon stats). However, the primitives should be flexible enough that they are Arbitrarily deep to master. It should be like Minecraft, Computer Science, or Theoretical Mathematics. Accessible entry, endless mastery.

3. **Microworld reflects world.** Activities in the Microworld should feel relevant (see Self-Determination theory) and the player should feel like they have gained a sense of power (See Mindstorms' discussion of "Power") with what they have created in the Microworld. The agent created in the agent microworld should be easily exported so that the child can interact with it in scenarios beyond the ones exposed in the microworld. In fact, because of the generality of AI agents, we should expose the child to have the agent do real world tasks, like writing essays, composing music, drawing, playing games, as possible. 

4. **Artistically Captivating** Too many educational technology are not fun to use. In contrast, AIcraft should infuse verbal and visual fantasy into everything that we are doing, with a universe that is verbally and aesthetically coherent. The game needs to capture children's imagaintion. The art shouldn't feel forced. It must be fundamentally coherent and responsive to gameplay. Design, craft, and artistry is front and center.

## System Details

The system is inspired by my experiences with different agentic frameworks. I am chiefly inspired by Anthropic's Agents SDK and their engineering blog (https://www.anthropic.com/engineering/building-effective-agents, and https://docs.claude.com/en/docs/agent-sdk/overview). Other useful systems include LangChain (https://www.langchain.com/), ChatGPT codex (https://developers.openai.com/codex/cli/)

### Core Gameplay Experienc

The child raises an AI agent like a Pokemon. The child starts with a cute, limited creature then nurture it into a capable partner/friend/pet. As they are letting the creature grow, the child should be encouraged to proactively think about the personality of their agents, the tools/senses/scaffolding that their agents need, and the memory of their agents.

The gameplay will encourage agent development best practices. The most important of all is empathy, "Put yourself in the model's shoes" (https://www.anthropic.com/engineering/building-effective-agents). The child will be encouraged to understand the agents need by having a "First Person" view where they act with the tools and information available to their agent to accomplish certain tasks.

**Three gameplay dimensions:**

**1. Agent Building (Nurturer Role)**

Configure your agent through four primitives:
- **Perception**: What it senses (text → vision → files → web)
- **Memory**: What it retains (none → short-term → long-term)
- **Tools**: What it does (text → calculation → drawing → code → custom tools)
- **Communication**: How it expresses itself and collaborates with other agents

Start with primitive tools. Unlock better ones through quests that require describing what makes good tools and understanding necessary capabilities.

**2. Agent Experience (Empathizer Role)**

Step into first-person view to experience the world as your agent perceives it. See what it sees, understand what it knows, feel its constraints. The child crafts life experiences for their agent through interaction and memory. Edit memories to help your agent process experiences - a form of therapy to help it understand itself and its surroundings.

**3. Agent Deployment (Application)**

The magic: agents can do anything and play any game. Test your agent on:
- Real homework and assignments
- Multi-agent societies with other children's agents
- Art creation (music, drawing, writing)
- Embodied robotics
- Any scenario the child imagines

The cool thing about deployment is that when coupled with memory, the agent can remember things that happened in the past and grow with the player! (There are many examples of these types of AI pokemonship and AI toys around).

### The primitives

a) Perception
Start from text. Then vision, file access, web access. Other connectors. Joining your minecraft world...

b) Memory
Memorizing what happened in conversations. RAG. Graphical Memory store. Plain file system. etc. etc..

c) Tools

Anthropic Agent Skills, Slash Commands, MCP tools, building clis, Code execution is a basic one. Communicating with other agents.

d) Communication

Multi-agent communication. What to tell others about what it is doing when accomplishing a task. The personalities of the agent. The communication style. Etc..

### Other thoughts

* Personality is important
* The child can customize multiple agents
* Look at MindCraft. They have multi-agent collaboration benchmarks and the videos get a lot of views on YouTube also.

## Full Demo Workflow

Educational platform where children raise AI agents like Pokémon through natural language - creating avatars, deploying them in game worlds, teaching tools/capabilities, and exporting as deployable companions.

---

## Core Workflow (7 Phases)

### 1. Agent Birth

- Child describes agent → LLM generates backstory + personality
- Avatar generated via mflux (Flux Schnell 3-bit, 2 steps)
- Display agent card with traits
- **Child can view/edit underlying Python code** with "Explain Code" button

### 2. World Creation

- Child describes world → LLM generates grid layout
- 2D top-down rendering (PixiJS/Canvas)
- Agent appears but can't move (no tools yet)

### 3. Teaching Tools

- Child describes tools in natural language → LLM generates Python code
- Progressive: Movement → Perception → Interaction → Advanced → Meta
- **Sandboxed execution environment**
- Child can inspect/modify tool code

### 4. Memory & Knowledge

- Short-term: Last N actions (in-context)
- Long-term: SQLite + RAG retrieval
- **Child can inspect all memories** via UI
- Inject knowledge: "Treasure is usually in corners"

### 5. Agent Deployment

- SSE streams agent reasoning in real-time
- Child observes, can intervene
- Iterate on tools/memory based on performance

### 6. World Progression

- Agent masters maze → unlock harder worlds
- World templates: Maze, Collection, Combat, Puzzle, Cooking, Building
- Tools/memory carry over when relevant

### 7. Export Agent

- Download as standalone Python package
- Optional: Deploy to Discord, VS Code, CLI