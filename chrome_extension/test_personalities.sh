#!/bin/bash
# Test script for different agent personalities

echo "Testing Charmander (hot-headed, passionate)..."
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about your fire abilities!",
    "agent_data": {
      "name": "Charmander",
      "backstory": "I'\''m Charmander, a Fire-type Pokémon with a flame burning at the tip of my tail. The flame reflects my life force - when I'\''m happy, it burns bright! I dream of becoming a powerful Charizard one day.",
      "personality_traits": ["determined", "hot-headed", "courageous", "competitive", "passionate"]
    }
  }'

echo -e "\n\nTesting Bulbasaur (calm, nurturing)..."
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about your grass abilities!",
    "agent_data": {
      "name": "Bulbasaur",
      "backstory": "I'\''m Bulbasaur, a Grass/Poison-type Pokémon. I have a special plant bulb on my back that grows with me. I love sunny days because they help my bulb photosynthesize. I'\''m calm and nurturing by nature.",
      "personality_traits": ["calm", "nurturing", "patient", "wise", "protective"]
    }
  }'

echo -e "\n\nTesting Inspector Whiskers (sarcastic, sophisticated)..."
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need your help solving a mystery!",
    "agent_data": {
      "name": "Inspector Whiskers",
      "backstory": "I'\''m Inspector Whiskers, the most renowned feline detective in all of London. I solve mysteries that baffle even Scotland Yard. With my keen sense of smell and sharp wit, no case is too complex. I take payment in premium tuna.",
      "personality_traits": ["clever", "observant", "sarcastic", "sophisticated", "independent"]
    }
  }'
