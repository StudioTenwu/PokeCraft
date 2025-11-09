import React, { useState, useEffect } from 'react';
import StageIndicator from './components/StageIndicator';
import AgentChat from './components/AgentChat';
import AgentConfigBuilder from './components/AgentConfigBuilder';
import ExecutionVisualizer from './components/ExecutionVisualizer';

function App() {
  const [currentStage, setCurrentStage] = useState(1);
  const [stages, setStages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [agentConfig, setAgentConfig] = useState({
    systemPrompt: '',
    tools: [],
    executableTools: [],
    maxTurns: 5,
    chainingStrategy: 'adaptive'
  });
  const [isBuilderMode, setIsBuilderMode] = useState(true);
  const [showExecutionViz, setShowExecutionViz] = useState(false);

  useEffect(() => {
    // Fetch stage information from backend
    fetch('http://localhost:8001/api/stages')
      .then(res => res.json())
      .then(data => {
        setStages(data.stages);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch stages:', err);
        setLoading(false);
      });
  }, []);

  const handleStageChange = (newStage) => {
    if (newStage <= currentStage || newStage === currentStage + 1) {
      setCurrentStage(newStage);
      setIsBuilderMode(true); // Reset to builder mode when changing stages
      setShowExecutionViz(false);
    }
  };

  const handleDeploy = () => {
    setIsBuilderMode(false);
    setShowExecutionViz(currentStage >= 3);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Agent Evolution...</p>
        </div>
      </div>
    );
  }

  const currentStageInfo = stages.find(s => s.id === currentStage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Agent Evolution: 4 Stages of Development
          </h1>
          <p className="text-gray-600 mt-2">
            Interactive demonstration of how AI agents evolve from simple chat to sophisticated tool-using systems
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Stage indicator */}
          <StageIndicator
            stages={stages}
            currentStage={currentStage}
            onStageChange={handleStageChange}
          />

          {/* Builder/Chat Toggle */}
          {!isBuilderMode && (
            <div className="flex justify-end">
              <button
                onClick={() => setIsBuilderMode(true)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
              >
                Back to Builder
              </button>
            </div>
          )}

          {/* Interactive Builder */}
          {isBuilderMode ? (
            <AgentConfigBuilder
              stage={currentStage}
              config={agentConfig}
              onConfigChange={setAgentConfig}
              onDeploy={handleDeploy}
            />
          ) : (
            <>
              {/* Configuration Summary */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-purple-900">Active Configuration</h3>
                    <p className="text-sm text-purple-700 mt-1">
                      {currentStage === 1 && "Testing basic chat with custom system prompt"}
                      {currentStage === 2 && `Testing tool recognition with ${agentConfig.tools?.length || 0} visible tools`}
                      {currentStage === 3 && `Testing tool execution with ${agentConfig.executableTools?.length || 0} executable tools`}
                      {currentStage === 4 && `Testing complete agent with ${agentConfig.executableTools?.length || 0} tools and ${agentConfig.chainingStrategy} strategy`}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="inline-block px-3 py-1 bg-green-500 text-white rounded-full text-sm font-semibold">
                      DEPLOYED
                    </span>
                  </div>
                </div>
              </div>

              {/* Chat interface */}
              <div style={{ height: '600px' }}>
                <AgentChat
                  currentStage={currentStage}
                  currentStageInfo={currentStageInfo}
                  config={agentConfig}
                />
              </div>

              {/* Execution Visualizer */}
              {showExecutionViz && (
                <ExecutionVisualizer
                  toolEvents={[]}
                  isActive={true}
                />
              )}

              {/* Stage details */}
              {currentStageInfo && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    Stage {currentStage}: {currentStageInfo.name}
                  </h2>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-gray-700 mb-2">What's New in This Stage</h3>
                      <p className="text-gray-600">{currentStageInfo.description}</p>

                      <h3 className="font-semibold text-gray-700 mt-4 mb-2">Capabilities</h3>
                      <ul className="list-disc list-inside text-gray-600 space-y-1">
                        {currentStageInfo.capabilities.map((cap, idx) => (
                          <li key={idx}>{cap}</li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold text-gray-700 mb-2">Key Test Activity</h3>
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h4 className="font-medium text-blue-900 mb-2">
                          {currentStageInfo.key_activity?.title}
                        </h4>
                        <p className="text-sm text-blue-700 mb-3">
                          "{currentStageInfo.key_activity?.prompt}"
                        </p>
                        <p className="text-xs text-blue-600">
                          {currentStage === 1 && "Watch how the agent maintains conversation context"}
                          {currentStage === 2 && "See the agent recognize it needs the web_search tool"}
                          {currentStage === 3 && "Observe the agent execute tools and process results"}
                          {currentStage === 4 && "Experience multi-tool chaining in action"}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 pb-8 text-center text-gray-600 text-sm">
        <p>
          Based on{' '}
          <a
            href="https://ampcode.com/how-to-build-an-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            "How to Build an Agent"
          </a>
          {' '}by Thorsten Ball
        </p>
      </footer>
    </div>
  );
}

export default App;
