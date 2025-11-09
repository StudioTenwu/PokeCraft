# AICraft Visualization System Design

## Phase Overview
After completing 34 rounds of core microworld mechanics (506 tests), we now implement the presentation layer that brings agents to life visually, aurally, and through animation.

## Design Principles
1. **Visual Personality** - Agent appearance reflects personality traits and emotions
2. **Readable State** - UI clearly shows agent capabilities, knowledge, emotions, relationships
3. **Immersive Experience** - Players feel connected to their agents through rich visual feedback
4. **Playful Aesthetic** - Design reflects the wonder and imagination of raising AI partners

## Phase 1: UI/Visualization Foundation (Rounds 35-36)

### Round 35: Agent Visual Representation
**Goal:** Create visual renderings of agents showing:
- Basic avatar appearance (personality-based)
- Emotional expression (eyes, posture, colors)
- Status indicators (health, happiness, energy)
- Personality quirks in visual form

**Key Systems:**
1. **AgentAvatar** - Visual properties of an agent
   - Base appearance (character type, size, color palette)
   - Current emotional state (reflected in expressions)
   - Personality traits (visible in style/design)
   - Status badges (tools unlocked, expertise, achievements)

2. **EmotionalExpression** - How emotions look
   - Eye states (happy squint, sad droop, angry glare, surprised wide)
   - Color auras (happy=warm, sad=cool, angry=red, neutral=balanced)
   - Posture indicators (confident stance, slouched, defensive)
   - Animation triggers (flinch for anger, bounce for joy)

3. **PersonalityVisuals** - Personality traits in appearance
   - CURIOUS: Wide eyes, forward lean, bright highlights
   - CAUTIOUS: Narrowed eyes, backward lean, muted colors
   - BOLD: Chest-out stance, sharp colors, confident expression
   - ANALYTICAL: Thoughtful expression, geometric patterns
   - IMPULSIVE: Dynamic posture, bright irregular colors
   - EMPATHETIC: Soft eyes, warm colors, open posture
   - SELFISH: Self-focused positioning, cool colors, sharp lines

4. **StatusDisplay** - Quick visual information
   - Health bar / energy level
   - Knowledge indicators (expertise badges by domain)
   - Tool capabilities (visual icons for each unlocked tool)
   - Relationship indicators (bonds with player, other agents)
   - Achievement badges (quests completed, milestones)

**Test Categories (20+ tests):**
- Avatar creation with personality baseline
- Emotional expression rendering
- Status indicator calculations
- Personality visual reflection
- Avatar customization
- Visual state transitions

### Round 36: Relationship & Knowledge Visualization
**Goal:** Visualize the complex systems of relationships and knowledge

**Key Systems:**
1. **RelationshipVisualization** - Show agent social networks
   - Bond strength indicators (visual proximity, connection lines)
   - Trust levels (color intensity, connection stability)
   - Shared goals (synchronized visuals, linked indicators)
   - Multi-agent society visualization (node graphs, hierarchies)

2. **KnowledgeVisualization** - Make learning visible
   - Knowledge graph (topics as nodes, prerequisites as edges)
   - Expertise display (proficiency by domain)
   - Learning progress (tier progression visuals)
   - Learning strategy indicators

3. **MemoryVisualization** - Show memory state
   - Memory timeline (visual history of experiences)
   - Emotional memory markers (color-coded by emotional charge)
   - Memory associations (connected memories)
   - Suppressed/edited memory indicators

4. **SocietyVisualization** - Group dynamics
   - Governance structure (hierarchy or flat visualization)
   - Member roles and positions
   - Collective goals and treasury
   - Inter-agent relationships

**Test Categories (20+ tests):**
- Relationship graph generation
- Knowledge graph structure
- Expertise tier visualization
- Memory timeline display
- Society hierarchy rendering
- Visual update on state changes

## Phase 2: Audio/Voice Design (Round 37)

**Goal:** Voice synthesis that reflects personality, emotion, and speech patterns

**Key Systems:**
1. **VoiceProfile** - Agent voice characteristics
   - Base voice (age, gender, accent options)
   - Emotional voice modulation (pitch changes, pace changes)
   - Speech pattern effects (formal=slower, casual=faster, poetic=melodic)
   - Personality speech quirks (analytical=precise, impulsive=fast)

2. **EmotionalAudio** - How emotions sound
   - Happy: Higher pitch, faster pace, lighter tone
   - Sad: Lower pitch, slower pace, heavier tone
   - Angry: Harsh tone, staccato delivery, intensity
   - Fearful: Quivering, hesitant, uncertain delivery

3. **DialogueRendering** - Text-to-speech with personality
   - Apply emotional modulation to dialogue
   - Apply speech pattern to dialogue
   - Blend multiple traits for final rendering
   - Generate natural pauses and emphasis

## Phase 3: Animation System (Round 38)

**Goal:** Behavioral animations bring agents to life

**Key Systems:**
1. **AnimationTrigger** - What causes movement
   - Emotional state changes (happy bounce, sad droop)
   - Action execution (tool usage animations)
   - Communication (gesture for dialogue)
   - Achievement (celebration animation)

2. **BehaviorAnimation** - How agents move
   - Idle animations (breathing, small movements)
   - Emote animations (joy, sadness, fear, anger)
   - Action animations (thinking, working, creating)
   - Interaction animations (greeting, bonding, conflict)

3. **TransitionAnimation** - Smooth state changes
   - Between emotions
   - Between activities
   - Between knowledge tiers
   - Between locations/contexts

## Visual Design Language

### Color System
- **Happy (Joy/Trust):** Warm colors (gold, orange, warm pink)
- **Sad (Sadness):** Cool muted colors (gray-blue, indigo)
- **Angry (Anger):** Hot colors (red, orange-red, burgundy)
- **Fearful (Fear):** Dark cool colors (dark blue, purple)
- **Excited (Anticipation/Surprise):** Bright primary colors (bright yellow, bright pink)
- **Calm (Neutral):** Balanced colors (sage, soft gray, muted teal)

### Typography
- **Formal Speech:** Serif, measured spacing
- **Casual Speech:** Sans-serif, relaxed spacing
- **Poetic Speech:** Serif italic, artistic layout
- **Technical Speech:** Monospace, precise alignment
- **Childlike Speech:** Rounded sans-serif, playful spacing
- **Verbose Speech:** Large text, generous spacing
- **Terse Speech:** Minimal text, compact layout

### Shape Language
- **Curious:** Rounded, open shapes, forward-leaning
- **Cautious:** Angular, closed shapes, backward-leaning
- **Bold:** Confident straight lines, solid shapes
- **Analytical:** Geometric precision, structured layout
- **Impulsive:** Irregular, dynamic shapes, movement lines
- **Empathetic:** Soft curves, embracing shapes
- **Selfish:** Self-contained shapes, isolated positioning

## Implementation Strategy

### Round 35 Focus
1. Design and implement AgentAvatar dataclass with all visual properties
2. Create EmotionalExpression system that maps emotions to visuals
3. Implement StatusDisplay with achievement/knowledge indicators
4. 20+ comprehensive tests for visual rendering
5. Ensure all personality traits have distinct visual representations

### Round 36 Focus
1. Build relationship graph visualization engine
2. Create knowledge graph from KnowledgeBase connections
3. Implement memory timeline with emotional markers
4. Support society structure visualization
5. 20+ tests for complex multi-entity visualization

### Round 37 Focus
1. Design VoiceProfile with customization options
2. Implement emotional voice modulation
3. Create speech pattern voice effects
4. Integrate with DialogueSystem from Round 31
5. Voice synthesis output with personality

### Round 38 Focus
1. Define animation triggers for all emotional states
2. Implement behavior animation library
3. Create smooth transitions between states
4. Support action-specific animations
5. Performance optimization for smooth playback

## Success Metrics
- Visual representations accurately reflect agent state within 100ms updates
- Audio reflects personality, emotion, and speech pattern distinctly
- Animations feel responsive and natural (no jarring transitions)
- Player can intuitively understand agent state from visuals
- System scales to multiple agents without performance degradation
- Visual/audio design is cohesive and "artistically captivating"

## Next Steps After Visualization Phase
1. **Integration Phase** - Connect visualization systems to existing agent logic
2. **UI Framework** - Build web/desktop UI with visualization components
3. **Community Features** - Share agents, trading, cooperation visualization
4. **Educational Scaffolding** - Learning path guidance with visual feedback
5. **Robotics Integration** - Export visualized agents to physical robots
