import './HomePage.css'

function HomePage() {
  return (
    <div className="home-page">
      <header className="hero">
        <h1>Agent Engineering Playground</h1>
        <p className="tagline">Learn Agent Engineering Through Play</p>
        <p className="description">
          Build and configure AI agents to solve progressively complex tasks
          in a Minecraft-inspired grid world.
        </p>
        <button className="cta-button">Start Learning</button>
      </header>

      <section className="levels-section">
        <h2>Course Levels</h2>
        <div className="levels-grid">
          {/* Level cards will be dynamically generated */}
          <div className="level-card">
            <div className="level-number">1</div>
            <h3>Hello, Agent</h3>
            <p>Control agent behavior with natural language</p>
            <span className="duration">5 min</span>
          </div>

          <div className="level-card locked">
            <div className="level-number">2</div>
            <h3>Tool Use</h3>
            <p>Teach agents to use tools strategically</p>
            <span className="duration">10 min</span>
          </div>

          <div className="level-card locked">
            <div className="level-number">3</div>
            <h3>Planning & Reasoning</h3>
            <p>Introduce ReAct-style chain-of-thought</p>
            <span className="duration">15 min</span>
          </div>

          <div className="level-card locked">
            <div className="level-number">4</div>
            <h3>Multi-Agent Collaboration</h3>
            <p>Design agents that work together</p>
            <span className="duration">20 min</span>
          </div>

          <div className="level-card locked">
            <div className="level-number">5</div>
            <h3>Reward Shaping</h3>
            <p>Understand how incentives shape behavior</p>
            <span className="duration">15 min</span>
          </div>

          <div className="level-card locked">
            <div className="level-number">6</div>
            <h3>Real-World Export</h3>
            <p>Take your agent beyond the playground</p>
            <span className="duration">Capstone</span>
          </div>
        </div>
      </section>

      <footer className="home-footer">
        <p>Built with the philosophy that play is the natural learning interface</p>
      </footer>
    </div>
  )
}

export default HomePage
