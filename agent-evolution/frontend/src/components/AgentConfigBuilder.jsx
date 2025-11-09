import React, { useState } from 'react';
import { DndProvider, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import SystemPromptEditor from './SystemPromptEditor';
import ToolCard from './ToolCard';
import AgentArchitectureDiagram from './AgentArchitectureDiagram';

const AVAILABLE_TOOLS = ['web_search', 'file_write', 'file_read', 'calculator', 'image_gen', 'code_exec'];

function Stage1Builder({ config, onConfigChange, onDeploy }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Stage 1: Build Your Agent's Brain
        </h2>
        <p className="text-gray-600">
          Create a system prompt that defines your agent's personality and behavior.
          This is the foundation of how your agent thinks and responds.
        </p>
      </div>

      <SystemPromptEditor
        value={config.systemPrompt}
        onChange={(value) => onConfigChange({ ...config, systemPrompt: value })}
      />

      <div className="border-t pt-4">
        <h3 className="font-semibold text-gray-700 mb-3">Live Preview</h3>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-300">
          <p className="text-sm text-gray-700 mb-2">
            <strong>Test Prompt:</strong> "Tell me about yourself"
          </p>
          <div className="p-3 bg-white rounded border border-gray-200">
            <p className="text-sm text-gray-600 italic">
              {config.systemPrompt
                ? `With your custom prompt, the agent will respond based on: "${config.systemPrompt.substring(0, 100)}${config.systemPrompt.length > 100 ? '...' : ''}"`
                : 'Configure a system prompt to see how it shapes responses!'}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onDeploy}
          disabled={!config.systemPrompt?.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Deploy & Test Agent
        </button>
      </div>
    </div>
  );
}

function ToolLibraryDropZone({ tools, onToolAdd }) {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'TOOL',
    drop: (item) => onToolAdd(item.tool),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));

  return (
    <div
      ref={drop}
      className={`
        min-h-[200px] p-6 rounded-lg border-2 border-dashed transition-all
        ${isOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
      `}
    >
      <h3 className="font-semibold text-gray-700 mb-3">My Agent's Tool Library</h3>
      {tools.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p className="text-lg mb-2">📦 Drop tools here</p>
          <p className="text-sm">Drag tools from the available tools section</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {tools.map((tool) => (
            <ToolCard key={tool} tool={tool} status="visible" />
          ))}
        </div>
      )}
    </div>
  );
}

function Stage2Builder({ config, onConfigChange, onDeploy }) {
  const [availableTools, setAvailableTools] = useState(
    AVAILABLE_TOOLS.filter(t => !config.tools?.includes(t))
  );

  const handleToolAdd = (tool) => {
    if (!config.tools?.includes(tool)) {
      const newTools = [...(config.tools || []), tool];
      onConfigChange({ ...config, tools: newTools });
      setAvailableTools(availableTools.filter(t => t !== tool));
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
        <div className="border-b pb-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Stage 2: Build Your Agent's Tool Library
          </h2>
          <p className="text-gray-600">
            Select which tools your agent can SEE and understand. The agent won't execute them yet,
            but will recognize when they could be useful.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Available Tools</h3>
            <div className="space-y-3">
              {availableTools.map((tool) => (
                <ToolCard key={tool} tool={tool} draggable={true} />
              ))}
            </div>
          </div>

          <div>
            <ToolLibraryDropZone tools={config.tools || []} onToolAdd={handleToolAdd} />
          </div>
        </div>

        <div className="border-t pt-4">
          <h3 className="font-semibold text-gray-700 mb-3">Configuration Preview</h3>
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-300">
            <pre className="text-xs font-mono text-gray-800 overflow-x-auto">
              {JSON.stringify({ tools: config.tools || [] }, null, 2)}
            </pre>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onDeploy}
            disabled={!config.tools?.length}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold transition-colors"
          >
            Deploy & Test Tool Recognition
          </button>
        </div>
      </div>
    </DndProvider>
  );
}

function Stage3Builder({ config, onConfigChange, onDeploy }) {
  const handleToggleTool = (tool) => {
    const executableTools = config.executableTools || [];
    const newExecutableTools = executableTools.includes(tool)
      ? executableTools.filter(t => t !== tool)
      : [...executableTools, tool];
    onConfigChange({ ...config, executableTools: newExecutableTools });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Stage 3: Enable Tool Execution
        </h2>
        <p className="text-gray-600">
          Make tools executable! Your agent can now actually USE tools to accomplish tasks.
          Toggle tools to enable/disable execution.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold text-gray-700 mb-3">Tool Configuration</h3>
          <div className="space-y-3">
            {(config.tools || []).map((tool) => (
              <ToolCard
                key={tool}
                tool={tool}
                status={config.executableTools?.includes(tool) ? 'executable' : 'visible'}
                onToggle={handleToggleTool}
              />
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-700 mb-3">Execution Rules</h3>
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-300 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Turns: {config.maxTurns || 5}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={config.maxTurns || 5}
                onChange={(e) => onConfigChange({ ...config, maxTurns: parseInt(e.target.value) })}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-gray-600 mt-2">
                Controls how many times the agent can use tools in one conversation turn
              </p>
            </div>

            <div className="pt-4 border-t">
              <h4 className="font-medium text-gray-700 mb-2">Execution Flow</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center">1</span>
                  <span>Receive query</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-purple-500 text-white text-xs flex items-center justify-center">2</span>
                  <span>Plan approach</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-yellow-500 text-white text-xs flex items-center justify-center">3</span>
                  <span>Execute tool(s)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-green-500 text-white text-xs flex items-center justify-center">4</span>
                  <span>Process results</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center">5</span>
                  <span>Respond</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onDeploy}
          disabled={!config.executableTools?.length}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Deploy & Test Execution
        </button>
      </div>
    </div>
  );
}

function Stage4Builder({ config, onConfigChange, onDeploy }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Stage 4: Complete Agent Architecture
        </h2>
        <p className="text-gray-600">
          Configure your complete agent with all capabilities: custom prompts, multiple tools,
          and intelligent orchestration strategies.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-6">
          <SystemPromptEditor
            value={config.systemPrompt}
            onChange={(value) => onConfigChange({ ...config, systemPrompt: value })}
            showExamples={false}
          />

          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Tool Selection</h3>
            <div className="space-y-2">
              {AVAILABLE_TOOLS.map((tool) => (
                <label key={tool} className="flex items-center gap-3 p-3 bg-gray-50 rounded border border-gray-300 cursor-pointer hover:bg-blue-50">
                  <input
                    type="checkbox"
                    checked={config.executableTools?.includes(tool)}
                    onChange={(e) => {
                      const tools = config.executableTools || [];
                      const newTools = e.target.checked
                        ? [...tools, tool]
                        : tools.filter(t => t !== tool);
                      onConfigChange({
                        ...config,
                        tools: newTools,
                        executableTools: newTools
                      });
                    }}
                    className="w-5 h-5"
                  />
                  <span className="font-medium text-gray-700">{tool}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Turns: {config.maxTurns || 10}
            </label>
            <input
              type="range"
              min="1"
              max="20"
              value={config.maxTurns || 10}
              onChange={(e) => onConfigChange({ ...config, maxTurns: parseInt(e.target.value) })}
              className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chaining Strategy
            </label>
            <select
              value={config.chainingStrategy || 'adaptive'}
              onChange={(e) => onConfigChange({ ...config, chainingStrategy: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="sequential">Sequential - Use tools one at a time</option>
              <option value="parallel">Parallel - Use multiple tools simultaneously</option>
              <option value="adaptive">Adaptive - Agent decides the best approach</option>
            </select>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-gray-700 mb-3">Agent Architecture</h3>
            <AgentArchitectureDiagram config={config} />
          </div>

          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h4 className="font-semibold text-purple-900 mb-2">Configuration Summary</h4>
            <div className="space-y-1 text-sm text-purple-700">
              <p><strong>System Prompt:</strong> {config.systemPrompt ? 'Configured' : 'Not set'}</p>
              <p><strong>Tools:</strong> {config.executableTools?.length || 0} enabled</p>
              <p><strong>Max Turns:</strong> {config.maxTurns || 10}</p>
              <p><strong>Strategy:</strong> {config.chainingStrategy || 'adaptive'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onDeploy}
          disabled={!config.systemPrompt || !config.executableTools?.length}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold transition-colors"
        >
          Deploy Complete Agent
        </button>
      </div>
    </div>
  );
}

export default function AgentConfigBuilder({ stage, config, onConfigChange, onDeploy }) {
  const builders = {
    1: Stage1Builder,
    2: Stage2Builder,
    3: Stage3Builder,
    4: Stage4Builder,
  };

  const Builder = builders[stage];

  if (!Builder) {
    return <div>Invalid stage</div>;
  }

  return <Builder config={config} onConfigChange={onConfigChange} onDeploy={onDeploy} />;
}
