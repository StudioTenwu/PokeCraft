// Background service worker for PokéCraft Companion extension
// This script initializes multiple Pokémon agents and manages the side panel

// Define 4 default Pokémon agents
const DEFAULT_AGENTS = {
  pikachu: {
    id: "pikachu",
    name: "Pikachu",
    avatar_url: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    backstory: "I am Pikachu, an Electric-type Pokémon known for my lightning bolt-shaped tail and adorable cheeks that store electricity. I love adventures and making new friends!",
    personality_traits: ["energetic", "loyal", "brave", "friendly", "playful"]
  },
  charmander: {
    id: "charmander",
    name: "Charmander",
    avatar_url: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
    backstory: "I'm Charmander, a Fire-type Pokémon with a flame burning at the tip of my tail. The flame reflects my life force - when I'm happy, it burns bright! I dream of becoming a powerful Charizard one day.",
    personality_traits: ["determined", "hot-headed", "courageous", "competitive", "passionate"]
  },
  bulbasaur: {
    id: "bulbasaur",
    name: "Bulbasaur",
    avatar_url: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
    backstory: "I'm Bulbasaur, a Grass/Poison-type Pokémon. I have a special plant bulb on my back that grows with me. I love sunny days because they help my bulb photosynthesize. I'm calm and nurturing by nature.",
    personality_traits: ["calm", "nurturing", "patient", "wise", "protective"]
  },
  squirtle: {
    id: "squirtle",
    name: "Squirtle",
    avatar_url: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png",
    backstory: "I'm Squirtle, a Water-type Pokémon! My shell is super tough and protects me. I can shoot powerful water blasts and I love swimming in the ocean. I'm part of the Squirtle Squad!",
    personality_traits: ["cool", "playful", "mischievous", "confident", "tactical"]
  }
};

// Initialize extension on install or update
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('PokéCraft Companion extension event:', details.reason);

  if (details.reason === 'install') {
    // Fresh install - initialize with 4 Pokémon agents
    await chrome.storage.local.set({
      agents: DEFAULT_AGENTS,
      activeAgentId: 'pikachu',
      chatHistories: {
        pikachu: [],
        charmander: [],
        bulbasaur: [],
        squirtle: []
      }
    });
    console.log('Initialized 4 Pokémon agents');

  } else if (details.reason === 'update') {
    // Extension update - migrate existing data if needed
    const oldData = await chrome.storage.local.get(['agentData', 'chatHistory', 'agents']);

    // Check if this is an old version (single agent)
    if (oldData.agentData && !oldData.agents) {
      console.log('Migrating from single-agent to multi-agent...');

      // Migrate: preserve old chat history under Pikachu
      await chrome.storage.local.set({
        agents: DEFAULT_AGENTS,
        activeAgentId: 'pikachu',
        chatHistories: {
          pikachu: oldData.chatHistory || [],
          charmander: [],
          bulbasaur: [],
          squirtle: []
        }
      });

      // Clean up old keys
      await chrome.storage.local.remove(['agentData', 'chatHistory']);
      console.log('Migration complete - preserved chat history under Pikachu');

    } else if (!oldData.agents) {
      // No agents at all - initialize fresh
      await chrome.storage.local.set({
        agents: DEFAULT_AGENTS,
        activeAgentId: 'pikachu',
        chatHistories: {
          pikachu: [],
          charmander: [],
          bulbasaur: [],
          squirtle: []
        }
      });
      console.log('Initialized 4 Pokémon agents (no previous data)');
    } else {
      console.log('Multi-agent system already initialized');
    }
  }
});

// Open side panel when extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ windowId: tab.windowId });
});
