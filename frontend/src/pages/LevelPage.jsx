import { useParams } from 'react-router-dom'
import './LevelPage.css'

function LevelPage() {
  const { levelId } = useParams()

  return (
    <div className="level-page">
      <div className="level-header">
        <h1>Level {levelId}: Coming Soon</h1>
        <p>The interactive grid world will appear here</p>
      </div>

      <div className="level-layout">
        <aside className="control-panel">
          <h2>Agent Configuration</h2>
          <div className="prompt-editor">
            <label>System Prompt:</label>
            <textarea
              placeholder="You are an agent in a grid world..."
              rows={8}
            />
          </div>

          <div className="tools-section">
            <h3>Available Tools</h3>
            <div className="tools-list">
              <label>
                <input type="checkbox" defaultChecked />
                move_up()
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                move_down()
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                move_left()
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                move_right()
              </label>
            </div>
          </div>

          <button className="run-button">Run Agent</button>
        </aside>

        <main className="grid-container">
          <div className="grid-world">
            <p>Grid visualization coming soon...</p>
          </div>
        </main>

        <aside className="insights-panel">
          <h2>Agent Insights</h2>

          <div className="reasoning-trace">
            <h3>Reasoning Trace</h3>
            <div className="trace-log">
              <p className="trace-empty">Agent hasn't run yet</p>
            </div>
          </div>

          <div className="metrics">
            <h3>Metrics</h3>
            <div className="metric">
              <span>Steps:</span>
              <span>0</span>
            </div>
            <div className="metric">
              <span>Reward:</span>
              <span>0.0</span>
            </div>
            <div className="metric">
              <span>Success:</span>
              <span>-</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default LevelPage
