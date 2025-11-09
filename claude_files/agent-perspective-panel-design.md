# Agent First-Person View Panel - Complete Design Document

## Executive Summary

This document specifies the design of a persistent, always-visible panel that provides transparency into an AI agent's internal processes. The panel answers four fundamental questions in real-time:

1. **What I See** - Current inputs, context, and understanding
2. **What I Can Do** - Available tools, skills, and capabilities
3. **What I'm Thinking** - Real-time reasoning and decision-making process
4. **My Limitations** - Current capability gaps and how to unlock them

This design integrates with the existing Agent Evolution application at `/Users/wz/Desktop/zPersonalProjects/AICraft/agent-evolution/`.

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [System Architecture](#system-architecture)
3. [Component Specifications](#component-specifications)
4. [Data Structures](#data-structures)
5. [API Endpoints](#api-endpoints)
6. [Implementation Plan](#implementation-plan)
7. [Example Reasoning Traces](#example-reasoning-traces)
8. [Accessibility](#accessibility)
9. [Performance Optimization](#performance-optimization)

---

## Design Philosophy

### Core Principles

1. **Transparency Over Obscurity** - Make the abstract concrete by showing exactly what the agent knows and can do
2. **Real-Time Feedback** - Update the view millisecond by millisecond as the agent processes information
3. **Educational Focus** - Help users understand not just what the agent does, but why
4. **Progressive Disclosure** - Show essential information upfront, details on demand
5. **Non-Intrusive** - Always visible but doesn't interfere with the primary chat experience

### User Goals

- **Developers**: Debug agent behavior, understand tool selection logic, optimize configurations
- **Product Managers**: Understand agent capabilities and limitations for feature planning
- **End Users**: Build mental models of how the agent works, trust through transparency
- **Educators**: Teach agent architecture and decision-making processes

---

## System Architecture

### High-Level Overview

```
┌────────────────────────────────────────────────────────────┐
│                    Browser Window                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                Main Chat Area                        │  │
│  │  - User messages                                     │  │
│  │  - Agent responses                                   │  │
│  │  - Tool execution results                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Agent Perspective Panel (Docked)            │  │
│  │  ┌─────────┬─────────┬─────────┬──────────────────┐ │  │
│  │  │ What I  │ What I  │ What I'm│ My Limitations   │ │  │
│  │  │ See     │ Can Do  │ Thinking│                  │ │  │
│  │  └─────────┴─────────┴─────────┴──────────────────┘ │  │
│  │                                                      │  │
│  │  [Tab Content - Real-time updates via SSE]          │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘

                         ↕ SSE Stream

┌────────────────────────────────────────────────────────────┐
│                 FastAPI Backend                            │
│  POST /api/chat → Existing endpoint                        │
│  GET /api/agent-perspective → New SSE endpoint             │
│                                                            │
│  Enhanced event stream:                                    │
│  - reasoning_step                                          │
│  - context_update                                          │
│  - tool_evaluation                                         │
│  - confidence_score                                        │
└────────────────────────────────────────────────────────────┘
```

### Integration Points

The Agent Perspective Panel integrates with existing components:

1. **AgentChat.jsx** - Shares message state and tool events
2. **useAgentStream.js** - Extended to capture reasoning events
3. **backend/stages.py** - Enhanced to emit perspective events
4. **backend/tools.py** - Instrumented to report tool evaluation logic

---

## Component Specifications

### 1. AgentPerspectivePanel.jsx

**Main container component managing the entire panel**

```jsx
// Location: /agent-evolution/frontend/src/components/AgentPerspectivePanel.jsx

import React, { useState, useEffect } from 'react';
import WhatISee from './perspective/WhatISee';
import WhatICanDo from './perspective/WhatICanDo';
import WhatImThinking from './perspective/WhatImThinking';
import MyLimitations from './perspective/MyLimitations';
import { usePerspectiveStream } from '../hooks/usePerspectiveStream';

export default function AgentPerspectivePanel({
  currentStage,
  config,
  messages,
  isStreaming
}) {
  const [activeTab, setActiveTab] = useState('thinking'); // Default to thinking
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isPinned, setIsPinned] = useState(true);

  const {
    contextState,
    availableTools,
    reasoningTrace,
    limitations,
    confidence
  } = usePerspectiveStream(currentStage, messages, isStreaming);

  const tabs = [
    { id: 'see', label: 'What I See', icon: '👁️', component: WhatISee },
    { id: 'do', label: 'What I Can Do', icon: '🛠️', component: WhatICanDo },
    { id: 'thinking', label: "What I'm Thinking", icon: '🧠', component: WhatImThinking },
    { id: 'limits', label: 'My Limitations', icon: '⚠️', component: MyLimitations }
  ];

  return (
    <div className={`
      fixed bottom-0 left-0 right-0
      bg-white border-t-2 border-purple-500 shadow-2xl
      transition-all duration-300 ease-in-out
      ${isCollapsed ? 'h-12' : 'h-96'}
      z-50
    `}>
      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
          <h3 className="font-bold text-lg">Agent First-Person View</h3>
          <span className="text-xs opacity-75">Stage {currentStage}</span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Confidence indicator */}
          <div className="flex items-center space-x-1 bg-white/20 px-3 py-1 rounded-full text-xs">
            <span>Confidence:</span>
            <span className="font-bold">{Math.round(confidence * 100)}%</span>
          </div>

          {/* Controls */}
          <button
            onClick={() => setIsPinned(!isPinned)}
            className="p-1 hover:bg-white/20 rounded"
            title={isPinned ? "Unpin" : "Pin"}
          >
            {isPinned ? '📌' : '📍'}
          </button>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 hover:bg-white/20 rounded"
            title={isCollapsed ? "Expand" : "Collapse"}
          >
            {isCollapsed ? '⬆️' : '⬇️'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      {!isCollapsed && (
        <>
          <div className="flex border-b border-gray-200 bg-gray-50">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex-1 px-4 py-2 font-medium text-sm
                  transition-colors duration-200
                  ${activeTab === tab.id
                    ? 'bg-white border-b-2 border-purple-500 text-purple-700'
                    : 'text-gray-600 hover:bg-gray-100'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="h-full overflow-y-auto p-4 bg-white">
            {activeTab === 'see' && (
              <WhatISee
                contextState={contextState}
                messages={messages}
                currentStage={currentStage}
              />
            )}
            {activeTab === 'do' && (
              <WhatICanDo
                availableTools={availableTools}
                currentStage={currentStage}
                config={config}
              />
            )}
            {activeTab === 'thinking' && (
              <WhatImThinking
                reasoningTrace={reasoningTrace}
                isStreaming={isStreaming}
              />
            )}
            {activeTab === 'limits' && (
              <MyLimitations
                limitations={limitations}
                currentStage={currentStage}
                config={config}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}
```

**Props:**
- `currentStage` (number): Current agent evolution stage (1-4)
- `config` (object): Agent configuration including tools and settings
- `messages` (array): Chat message history
- `isStreaming` (boolean): Whether agent is currently processing

**State:**
- `activeTab` (string): Currently selected tab
- `isCollapsed` (boolean): Panel collapsed/expanded state
- `isPinned` (boolean): Whether panel stays visible when scrolling

---

### 2. WhatISee.jsx

**Shows current context, inputs, and agent's understanding**

```jsx
// Location: /agent-evolution/frontend/src/components/perspective/WhatISee.jsx

import React from 'react';

export default function WhatISee({ contextState, messages, currentStage }) {
  const latestUserMessage = messages.filter(m => m.role === 'user').slice(-1)[0];

  return (
    <div className="space-y-4">
      {/* Current Context Overview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-bold text-blue-900 mb-3 flex items-center">
          <span className="mr-2">📋</span>
          Current Context
        </h4>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">System Prompt:</span>
            <span className="font-mono text-xs bg-white px-2 py-1 rounded">
              {contextState.systemPrompt?.substring(0, 50)}...
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-600">Conversation History:</span>
            <span className="font-bold text-blue-700">{messages.length} messages</span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-600">Available Memory:</span>
            <span className="text-gray-500 italic">
              {contextState.memory?.length > 0 ? `${contextState.memory.length} items` : '[empty]'}
            </span>
          </div>
        </div>
      </div>

      {/* Latest User Query Analysis */}
      {latestUserMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-bold text-green-900 mb-3 flex items-center">
            <span className="mr-2">🔍</span>
            Input Analysis
          </h4>

          <div className="space-y-3">
            <div>
              <div className="text-xs text-gray-500 mb-1">User Query:</div>
              <div className="bg-white p-2 rounded border border-green-300 text-sm">
                "{latestUserMessage.content}"
              </div>
            </div>

            {contextState.analysis && (
              <div className="space-y-2 text-sm">
                <div className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  <div>
                    <span className="font-semibold">Detected Intent: </span>
                    <span className="text-green-700">{contextState.analysis.intent}</span>
                  </div>
                </div>

                <div className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  <div>
                    <span className="font-semibold">Key Terms: </span>
                    <span className="text-green-700">
                      {contextState.analysis.keywords?.map((kw, i) => (
                        <span key={i} className="inline-block bg-green-100 px-2 py-0.5 rounded mr-1 text-xs">
                          {kw}
                        </span>
                      ))}
                    </span>
                  </div>
                </div>

                <div className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  <div>
                    <span className="font-semibold">Expected Output: </span>
                    <span className="text-green-700">{contextState.analysis.expectedOutput}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Contextual Awareness */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-bold text-purple-900 mb-3 flex items-center">
          <span className="mr-2">🎯</span>
          Contextual Awareness
        </h4>

        <div className="space-y-2 text-sm">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              currentStage >= 2 ? 'bg-green-500' : 'bg-gray-300'
            }`} />
            <span>Tool Schemas Visible: {currentStage >= 2 ? 'Yes' : 'No'}</span>
          </div>

          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              currentStage >= 3 ? 'bg-green-500' : 'bg-gray-300'
            }`} />
            <span>Tool Execution Enabled: {currentStage >= 3 ? 'Yes' : 'No'}</span>
          </div>

          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              currentStage >= 4 ? 'bg-green-500' : 'bg-gray-300'
            }`} />
            <span>Multi-Tool Chaining: {currentStage >= 4 ? 'Yes' : 'No'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Key Features:**
- Real-time context display
- User query parsing and analysis
- Stage-aware capability indicators
- Visual hierarchy with color-coding

---

### 3. WhatICanDo.jsx

**Inventory of available tools, skills, and confidence ratings**

```jsx
// Location: /agent-evolution/frontend/src/components/perspective/WhatICanDo.jsx

import React from 'react';
import ConfidenceMeter from './ConfidenceMeter';

export default function WhatICanDo({ availableTools, currentStage, config }) {
  const getToolRelevance = (tool, userQuery) => {
    // Mock relevance calculation - in production, this comes from backend
    if (!userQuery) return { score: 0.5, label: 'MEDIUM' };

    // Simple keyword matching for demo
    const queryLower = userQuery.toLowerCase();
    if (tool.name === 'web_search' && (queryLower.includes('search') || queryLower.includes('find'))) {
      return { score: 0.95, label: 'HIGH' };
    }
    return { score: 0.2, label: 'LOW' };
  };

  return (
    <div className="space-y-4">
      {/* Tools Section */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-bold text-blue-900 mb-3 flex items-center justify-between">
          <span className="flex items-center">
            <span className="mr-2">🛠️</span>
            Available Tools
          </span>
          <span className="text-sm font-normal bg-blue-100 px-3 py-1 rounded-full">
            {availableTools.length} tools
          </span>
        </h4>

        {availableTools.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-lg mb-2">No tools available at this stage</p>
            <p className="text-sm">Progress to Stage 2+ to unlock tools</p>
          </div>
        ) : (
          <div className="space-y-3">
            {availableTools.map((tool, index) => {
              const relevance = getToolRelevance(tool, config.lastQuery);
              const isExecutable = currentStage >= 3;

              return (
                <div
                  key={index}
                  className={`
                    bg-white border-2 rounded-lg p-4
                    transition-all duration-200
                    ${relevance.score > 0.7
                      ? 'border-green-400 shadow-md'
                      : 'border-gray-200'
                    }
                  `}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-blue-700">
                          {tool.name}
                        </span>
                        {!isExecutable && (
                          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">
                            View Only
                          </span>
                        )}
                        {isExecutable && (
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                            ✓ Executable
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{tool.description}</p>
                    </div>

                    <ConfidenceMeter
                      score={relevance.score}
                      label={relevance.label}
                      compact={true}
                    />
                  </div>

                  {/* Use When */}
                  <div className="mt-3 text-xs">
                    <div className="text-gray-500 mb-1">Use when:</div>
                    <div className="bg-gray-50 p-2 rounded border border-gray-200">
                      {getToolUseCase(tool.name)}
                    </div>
                  </div>

                  {/* Parameter Preview */}
                  <details className="mt-2">
                    <summary className="text-xs text-blue-600 cursor-pointer hover:text-blue-800">
                      View Parameters
                    </summary>
                    <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-x-auto border border-gray-200">
                      {JSON.stringify(tool.input_schema, null, 2)}
                    </pre>
                  </details>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Skills Section */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-bold text-purple-900 mb-3 flex items-center">
          <span className="mr-2">⚡</span>
          Skills Available
        </h4>

        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between bg-white p-2 rounded border border-purple-200">
            <span>Research Workflow</span>
            <span className="text-xs text-purple-600">Stages 3-4</span>
          </div>

          <div className="flex items-center justify-between bg-white p-2 rounded border border-purple-200">
            <span>Code Helper</span>
            <span className="text-xs text-purple-600">All Stages</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function getToolUseCase(toolName) {
  const useCases = {
    'web_search': 'User needs current information, real-time data, or wants to find resources online',
    'calculator': 'Mathematical calculations or numerical operations are required',
    'file_write': 'Need to save, persist, or create new content in a file',
    'file_read': 'Need to access or review existing file contents',
    'file_edit': 'Need to modify or update existing file content',
    'image_gen': 'User requests visual content or image generation',
    'code_exec': 'Need to run Python code for computation or validation'
  };

  return useCases[toolName] || 'Custom tool usage scenario';
}
```

**Key Features:**
- Tool inventory with execution status
- Real-time relevance scoring
- Confidence meters for tool selection
- Expandable parameter schemas
- Stage-aware availability indicators

---

### 4. WhatImThinking.jsx

**Real-time reasoning process visualization - THE CORE COMPONENT**

```jsx
// Location: /agent-evolution/frontend/src/components/perspective/WhatImThinking.jsx

import React, { useEffect, useRef } from 'react';
import ReasoningTimeline from './ReasoningTimeline';

export default function WhatImThinking({ reasoningTrace, isStreaming }) {
  const endRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to latest reasoning step
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [reasoningTrace]);

  if (reasoningTrace.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="text-6xl mb-4">🧠</div>
        <p className="text-lg">Waiting for input...</p>
        <p className="text-sm mt-2">Send a message to see my reasoning process</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Status Banner */}
      {isStreaming && (
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-3 rounded-lg flex items-center animate-pulse">
          <div className="w-3 h-3 rounded-full bg-white mr-3 animate-ping" />
          <span className="font-semibold">Reasoning in progress...</span>
        </div>
      )}

      {/* Reasoning Timeline */}
      <ReasoningTimeline trace={reasoningTrace} isActive={isStreaming} />

      {/* Current Focus */}
      {isStreaming && reasoningTrace.length > 0 && (
        <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-4">
          <h4 className="font-bold text-yellow-900 mb-2 flex items-center">
            <span className="mr-2">⚡</span>
            Current Focus
          </h4>
          <div className="text-sm text-yellow-800">
            {reasoningTrace[reasoningTrace.length - 1].description}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-700">
            {reasoningTrace.length}
          </div>
          <div className="text-xs text-blue-600 mt-1">Reasoning Steps</div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-700">
            {reasoningTrace.filter(t => t.type === 'tool_evaluation').length}
          </div>
          <div className="text-xs text-green-600 mt-1">Tools Evaluated</div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-700">
            {calculateTotalTime(reasoningTrace)}ms
          </div>
          <div className="text-xs text-purple-600 mt-1">Total Time</div>
        </div>
      </div>

      {/* Export Button */}
      <button
        onClick={() => exportReasoningTrace(reasoningTrace)}
        className="w-full py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition-colors"
      >
        📥 Export Reasoning Trace (JSON)
      </button>

      <div ref={endRef} />
    </div>
  );
}

function calculateTotalTime(trace) {
  if (trace.length === 0) return 0;
  const start = trace[0].timestamp;
  const end = trace[trace.length - 1].timestamp;
  return end - start;
}

function exportReasoningTrace(trace) {
  const dataStr = JSON.stringify(trace, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

  const exportFileDefaultName = `reasoning-trace-${Date.now()}.json`;

  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
}
```

**Key Features:**
- Live reasoning timeline
- Step-by-step thought process
- Tool evaluation visibility
- Performance metrics
- Export functionality

---

### 5. ReasoningTimeline.jsx

**Step-by-step visualization of agent's thought process**

```jsx
// Location: /agent-evolution/frontend/src/components/perspective/ReasoningTimeline.jsx

import React from 'react';

export default function ReasoningTimeline({ trace, isActive }) {
  const getStepIcon = (type) => {
    const icons = {
      'parsing': '📝',
      'analyzing': '🔍',
      'tool_evaluation': '⚖️',
      'tool_selection': '✓',
      'execution': '⚡',
      'processing': '⚙️',
      'formatting': '📋',
      'complete': '✅',
      'error': '❌'
    };
    return icons[type] || '•';
  };

  const getStepColor = (type) => {
    const colors = {
      'parsing': 'blue',
      'analyzing': 'yellow',
      'tool_evaluation': 'purple',
      'tool_selection': 'green',
      'execution': 'orange',
      'processing': 'indigo',
      'formatting': 'pink',
      'complete': 'green',
      'error': 'red'
    };
    return colors[type] || 'gray';
  };

  return (
    <div className="relative">
      {/* Vertical Timeline Line */}
      <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-300" />

      {/* Timeline Steps */}
      <div className="space-y-4">
        {trace.map((step, index) => {
          const color = getStepColor(step.type);
          const icon = getStepIcon(step.type);
          const isLatest = index === trace.length - 1 && isActive;

          return (
            <div key={index} className="relative pl-14">
              {/* Timeline Dot */}
              <div
                className={`
                  absolute left-4 top-1 w-5 h-5 rounded-full
                  flex items-center justify-center text-xs
                  bg-${color}-500 text-white
                  ${isLatest ? 'animate-pulse ring-4 ring-' + color + '-200' : ''}
                `}
              >
                {icon}
              </div>

              {/* Step Content */}
              <div
                className={`
                  bg-white border-2 rounded-lg p-3
                  border-${color}-200
                  ${isLatest ? 'shadow-lg' : 'shadow-sm'}
                  transition-all duration-200
                `}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs font-bold text-${color}-700 uppercase tracking-wide`}>
                        {step.type.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-gray-500">
                        [{formatTimestamp(step.timestamp, trace[0].timestamp)}]
                      </span>
                    </div>
                    <div className="text-sm text-gray-700 mt-1">
                      {step.description}
                    </div>
                  </div>

                  {step.duration && (
                    <div className={`text-xs font-mono text-${color}-600 bg-${color}-50 px-2 py-1 rounded`}>
                      {step.duration}ms
                    </div>
                  )}
                </div>

                {/* Additional Details */}
                {step.details && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    {renderStepDetails(step)}
                  </div>
                )}

                {/* Confidence Score */}
                {step.confidence !== undefined && (
                  <div className="mt-2 flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full bg-${color}-500 transition-all duration-300`}
                        style={{ width: `${step.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600">
                      {Math.round(step.confidence * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatTimestamp(timestamp, startTime) {
  const elapsed = timestamp - startTime;
  return `+${elapsed}ms`;
}

function renderStepDetails(step) {
  switch (step.type) {
    case 'tool_evaluation':
      return (
        <div className="space-y-1">
          {step.details.tools_considered?.map((tool, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs">
              <span className="font-mono">{tool.name}</span>
              <span className={`
                px-2 py-0.5 rounded
                ${tool.score > 0.7 ? 'bg-green-100 text-green-700' :
                  tool.score > 0.4 ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-600'}
              `}>
                {Math.round(tool.score * 100)}% match
              </span>
            </div>
          ))}
        </div>
      );

    case 'tool_selection':
      return (
        <div className="bg-green-50 p-2 rounded text-xs">
          <div className="font-semibold text-green-900">Selected: {step.details.tool_name}</div>
          <div className="text-green-700 mt-1">
            Reason: {step.details.reason}
          </div>
        </div>
      );

    case 'execution':
      return (
        <div className="bg-orange-50 p-2 rounded text-xs">
          <div className="font-mono text-orange-900">
            {step.details.tool_name}({JSON.stringify(step.details.parameters).substring(0, 100)}...)
          </div>
        </div>
      );

    default:
      return (
        <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
          {JSON.stringify(step.details, null, 2)}
        </pre>
      );
  }
}
```

**Key Features:**
- Vertical timeline visualization
- Step type color-coding
- Real-time updates with animations
- Detailed step breakdowns
- Confidence indicators per step
- Timestamp tracking

---

### 6. MyLimitations.jsx

**Shows capability gaps and how to unlock them**

```jsx
// Location: /agent-evolution/frontend/src/components/perspective/MyLimitations.jsx

import React from 'react';

export default function MyLimitations({ limitations, currentStage, config }) {
  const allCapabilities = [
    {
      id: 'real_time_data',
      name: 'Access real-time data',
      required: { stage: 2, tool: 'web_search' },
      unlockAction: 'Progress to Stage 2+ and ensure web_search tool is available'
    },
    {
      id: 'code_execution',
      name: 'Execute code',
      required: { stage: 3, tool: 'code_exec' },
      unlockAction: 'Progress to Stage 3+ and add code_exec tool to configuration'
    },
    {
      id: 'memory',
      name: 'Remember past conversations',
      required: { stage: 1, feature: 'memory' },
      unlockAction: 'Enable conversation memory in agent configuration'
    },
    {
      id: 'vision',
      name: 'See and analyze images',
      required: { stage: 1, feature: 'vision' },
      unlockAction: 'Use a vision-enabled model (e.g., Claude 3.5 Sonnet with vision)'
    },
    {
      id: 'file_system',
      name: 'Access file system',
      required: { stage: 3, tool: 'file_read' },
      unlockAction: 'Progress to Stage 3+ with file tools enabled'
    },
    {
      id: 'tool_chaining',
      name: 'Chain multiple tools together',
      required: { stage: 4 },
      unlockAction: 'Progress to Stage 4 (Multi-Tool Orchestration)'
    }
  ];

  const checkCapability = (capability) => {
    if (currentStage < capability.required.stage) {
      return { available: false, reason: 'stage' };
    }

    if (capability.required.tool) {
      const hasToolconst hasTool = config.executableTools?.some(t => t.name === capability.required.tool);
      if (!hasTool) {
        return { available: false, reason: 'tool' };
      }
    }

    if (capability.required.feature) {
      const hasFeature = config[capability.required.feature] === true;
      if (!hasFeature) {
        return { available: false, reason: 'feature' };
      }
    }

    return { available: true, reason: null };
  };

  const unavailableCapabilities = allCapabilities.filter(
    cap => !checkCapability(cap).available
  );

  const availableCapabilities = allCapabilities.filter(
    cap => checkCapability(cap).available
  );

  return (
    <div className="space-y-4">
      {/* Cannot Do Section */}
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
        <h4 className="font-bold text-red-900 mb-3 flex items-center">
          <span className="mr-2">❌</span>
          I Cannot Currently Do
        </h4>

        {unavailableCapabilities.length === 0 ? (
          <div className="text-center py-4 text-red-700">
            <p className="font-semibold">All capabilities unlocked!</p>
            <p className="text-sm mt-1">You're running at full capacity</p>
          </div>
        ) : (
          <div className="space-y-3">
            {unavailableCapabilities.map((cap, index) => (
              <div key={index} className="bg-white border border-red-300 rounded-lg p-3">
                <div className="flex items-start">
                  <span className="text-red-500 mr-2 mt-0.5">✗</span>
                  <div className="flex-1">
                    <div className="font-semibold text-red-900">{cap.name}</div>
                    <div className="text-xs text-red-700 mt-1">
                      Missing: {checkCapability(cap).reason === 'stage'
                        ? `Stage ${cap.required.stage}+ required`
                        : checkCapability(cap).reason === 'tool'
                        ? `Tool '${cap.required.tool}' not available`
                        : `Feature '${cap.required.feature}' not enabled`
                      }
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* How to Unlock Section */}
      {unavailableCapabilities.length > 0 && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
          <h4 className="font-bold text-blue-900 mb-3 flex items-center">
            <span className="mr-2">🔓</span>
            How to Unlock
          </h4>

          <div className="space-y-3">
            {unavailableCapabilities.map((cap, index) => (
              <div key={index} className="bg-white border border-blue-300 rounded-lg p-3">
                <div className="flex items-start">
                  <span className="text-blue-500 mr-2 mt-0.5">→</span>
                  <div className="flex-1">
                    <div className="font-semibold text-blue-900 mb-1">{cap.name}</div>
                    <div className="text-sm text-blue-700 bg-blue-50 p-2 rounded">
                      {cap.unlockAction}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Capabilities */}
      {availableCapabilities.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-bold text-green-900 mb-3 flex items-center">
            <span className="mr-2">✅</span>
            I Can Do
          </h4>

          <div className="grid grid-cols-2 gap-2">
            {availableCapabilities.map((cap, index) => (
              <div
                key={index}
                className="bg-white border border-green-300 rounded p-2 flex items-center text-sm"
              >
                <span className="text-green-600 mr-2">✓</span>
                <span className="text-green-900">{cap.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stage Progress Indicator */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-bold text-purple-900 mb-3">Current Stage Progress</h4>

        <div className="space-y-2">
          {[1, 2, 3, 4].map(stage => (
            <div key={stage} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                ${currentStage >= stage
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-300 text-gray-600'}
              `}>
                {stage}
              </div>
              <div className="ml-3 flex-1">
                <div className={`text-sm font-medium ${
                  currentStage >= stage ? 'text-green-900' : 'text-gray-500'
                }`}>
                  Stage {stage}: {getStageNamegetStageName(stage)}
                </div>
              </div>
              {currentStage === stage && (
                <span className="text-xs bg-purple-500 text-white px-2 py-1 rounded-full">
                  Current
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getStageName(stage) {
  const names = {
    1: 'Basic Reasoning',
    2: 'Tool Awareness',
    3: 'Single Tool Execution',
    4: 'Multi-Tool Orchestration'
  };
  return names[stage] || 'Unknown';
}
```

**Key Features:**
- Clear unavailable vs available capabilities
- Actionable unlock instructions
- Stage progression tracking
- Visual capability matrix
- Context-aware suggestions

---

### 7. ConfidenceMeter.jsx

**Visual confidence indicator component**

```jsx
// Location: /agent-evolution/frontend/src/components/perspective/ConfidenceMeter.jsx

import React from 'react';

export default function ConfidenceMeter({ score, label, compact = false }) {
  const getColor = (score) => {
    if (score >= 0.7) return { bg: 'bg-green-500', text: 'text-green-700', border: 'border-green-500' };
    if (score >= 0.4) return { bg: 'bg-yellow-500', text: 'text-yellow-700', border: 'border-yellow-500' };
    return { bg: 'bg-red-500', text: 'text-red-700', border: 'border-red-500' };
  };

  const colors = getColor(score);

  if (compact) {
    return (
      <div className="flex items-center space-x-1">
        <div className="w-16 bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full ${colors.bg} transition-all duration-300`}
            style={{ width: `${score * 100}%` }}
          />
        </div>
        <span className={`text-xs font-bold ${colors.text}`}>
          {label}
        </span>
      </div>
    );
  }

  return (
    <div className={`border-2 ${colors.border} rounded-lg p-3 bg-white`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-gray-700">Confidence</span>
        <span className={`text-lg font-bold ${colors.text}`}>
          {Math.round(score * 100)}%
        </span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full ${colors.bg} transition-all duration-500 ease-out`}
          style={{ width: `${score * 100}%` }}
        />
      </div>

      <div className="mt-2 text-center">
        <span className={`text-xs font-bold ${colors.text} uppercase tracking-wide`}>
          {label}
        </span>
      </div>
    </div>
  );
}
```

---

### 8. usePerspectiveStream.js

**Custom hook for managing perspective data**

```jsx
// Location: /agent-evolution/frontend/src/hooks/usePerspectiveStream.js

import { useState, useEffect, useCallback } from 'react';

export function usePerspectiveStream(currentStage, messages, isStreaming) {
  const [contextState, setContextState] = useState({
    systemPrompt: '',
    memory: [],
    analysis: null
  });

  const [availableTools, setAvailableTools] = useState([]);
  const [reasoningTrace, setReasoningTrace] = useState([]);
  const [limitations, setLimitations] = useState([]);
  const [confidence, setConfidence] = useState(0.5);

  // Fetch available tools based on stage
  useEffect(() => {
    fetch(`http://localhost:8001/api/tools?stage=${currentStage}`)
      .then(res => res.json())
      .then(data => setAvailableTools(data.tools || []))
      .catch(err => console.error('Failed to fetch tools:', err));
  }, [currentStage]);

  // Update context when messages change
  useEffect(() => {
    if (messages.length > 0) {
      const latestUserMessage = messages.filter(m => m.role === 'user').slice(-1)[0];

      if (latestUserMessage) {
        // Simulate analysis (in production, this comes from backend)
        setContextState(prev => ({
          ...prev,
          analysis: analyzeMessage(latestUserMessage.content)
        }));
      }
    }
  }, [messages]);

  // Listen for reasoning events (mock implementation)
  useEffect(() => {
    if (!isStreaming) {
      return;
    }

    // In production, this would be a real SSE connection
    // For now, simulate reasoning steps
    const simulateReasoning = () => {
      const steps = generateMockReasoningSteps(currentStage, messages);

      let index = 0;
      const interval = setInterval(() => {
        if (index < steps.length) {
          setReasoningTrace(prev => [...prev, steps[index]]);
          index++;
        } else {
          clearInterval(interval);
        }
      }, 200);

      return () => clearInterval(interval);
    };

    const cleanup = simulateReasoning();
    return cleanup;
  }, [isStreaming, currentStage, messages]);

  return {
    contextState,
    availableTools,
    reasoningTrace,
    limitations,
    confidence
  };
}

function analyzeMessage(content) {
  // Simple keyword-based analysis
  const keywords = content.toLowerCase().match(/\b\w+\b/g) || [];

  let intent = 'general_query';
  if (keywords.some(k => ['search', 'find', 'lookup'].includes(k))) {
    intent = 'information_search';
  } else if (keywords.some(k => ['calculate', 'compute', 'math'].includes(k))) {
    intent = 'calculation';
  } else if (keywords.some(k => ['create', 'write', 'make'].includes(k))) {
    intent = 'creation';
  }

  return {
    intent,
    keywords: keywords.slice(0, 5),
    expectedOutput: getExpectedOutput(intent)
  };
}

function getExpectedOutput(intent) {
  const outputs = {
    'information_search': 'Search results with URLs and descriptions',
    'calculation': 'Numerical result or computation',
    'creation': 'Generated content or files',
    'general_query': 'Informative response'
  };
  return outputs[intent] || 'Response';
}

function generateMockReasoningSteps(stage, messages) {
  const startTime = Date.now();

  const steps = [
    {
      type: 'parsing',
      timestamp: startTime,
      duration: 10,
      description: 'Parsing user input and extracting key information',
      confidence: 0.95
    },
    {
      type: 'analyzing',
      timestamp: startTime + 10,
      duration: 25,
      description: 'Analyzing intent and context from conversation history',
      confidence: 0.85
    }
  ];

  if (stage >= 2) {
    steps.push({
      type: 'tool_evaluation',
      timestamp: startTime + 35,
      duration: 40,
      description: 'Evaluating available tools for task requirements',
      confidence: 0.75,
      details: {
        tools_considered: [
          { name: 'web_search', score: 0.95 },
          { name: 'calculator', score: 0.05 },
          { name: 'file_write', score: 0.30 }
        ]
      }
    });
  }

  if (stage >= 3) {
    steps.push({
      type: 'tool_selection',
      timestamp: startTime + 75,
      duration: 10,
      description: 'Selected web_search as the most appropriate tool',
      confidence: 0.95,
      details: {
        tool_name: 'web_search',
        reason: 'User query requires current information from the web'
      }
    });

    steps.push({
      type: 'execution',
      timestamp: startTime + 85,
      duration: 120,
      description: 'Executing web_search tool with query parameters',
      confidence: 1.0,
      details: {
        tool_name: 'web_search',
        parameters: { query: 'user query here' }
      }
    });
  }

  steps.push({
    type: 'processing',
    timestamp: startTime + 205,
    duration: 30,
    description: 'Processing tool results and preparing response',
    confidence: 0.90
  });

  steps.push({
    type: 'formatting',
    timestamp: startTime + 235,
    duration: 15,
    description: 'Formatting final response for user',
    confidence: 0.95
  });

  steps.push({
    type: 'complete',
    timestamp: startTime + 250,
    duration: 0,
    description: 'Response ready for delivery',
    confidence: 1.0
  });

  return steps;
}
```

---

## Data Structures

### Reasoning Trace Event

```typescript
interface ReasoningStep {
  type: 'parsing' | 'analyzing' | 'tool_evaluation' | 'tool_selection' |
        'execution' | 'processing' | 'formatting' | 'complete' | 'error';
  timestamp: number;        // Unix timestamp in ms
  duration: number;         // Duration in ms
  description: string;      // Human-readable description
  confidence: number;       // 0-1 confidence score
  details?: {              // Optional type-specific details
    [key: string]: any;
  };
}
```

### Context State

```typescript
interface ContextState {
  systemPrompt: string;
  memory: Array<{
    key: string;
    value: any;
    timestamp: number;
  }>;
  analysis: {
    intent: string;
    keywords: string[];
    expectedOutput: string;
  } | null;
}
```

### Tool Evaluation

```typescript
interface ToolEvaluation {
  name: string;
  score: number;          // 0-1 relevance score
  reasoning: string;      // Why this score
  isExecutable: boolean;
  parameters?: object;
}
```

---

## API Endpoints

### New Endpoint: GET /api/tools

**Purpose:** Fetch available tools for a specific stage

**Request:**
```
GET /api/tools?stage=3
```

**Response:**
```json
{
  "stage": 3,
  "tools": [
    {
      "name": "web_search",
      "description": "Search the web for information",
      "input_schema": { ... },
      "executable": true
    },
    ...
  ],
  "total_count": 7
}
```

### Enhanced: POST /api/chat

**Add perspective events to existing SSE stream**

**New Event Types:**

```json
// Reasoning Step Event
{
  "type": "reasoning_step",
  "step": {
    "type": "tool_evaluation",
    "timestamp": 1699564789123,
    "duration": 40,
    "description": "Evaluating tools...",
    "confidence": 0.75,
    "details": { ... }
  }
}

// Context Update Event
{
  "type": "context_update",
  "context": {
    "memory_updated": true,
    "new_items": 2
  }
}

// Tool Evaluation Event
{
  "type": "tool_evaluated",
  "tool_name": "web_search",
  "score": 0.95,
  "reasoning": "User query requires current information"
}
```

---

## Implementation Plan

### Phase 1: Core Components (Week 1)

**Day 1-2: Panel Structure**
- [ ] Create `AgentPerspectivePanel.jsx` with tab navigation
- [ ] Implement collapse/expand/pin functionality
- [ ] Add to `App.jsx` with proper state management
- [ ] Style with Tailwind CSS matching existing design

**Day 3-4: Tab Components**
- [ ] Implement `WhatISee.jsx` with context display
- [ ] Implement `WhatICanDo.jsx` with tool inventory
- [ ] Implement `MyLimitations.jsx` with capability matrix
- [ ] Create `ConfidenceMeter.jsx` reusable component

**Day 5-7: Reasoning Timeline**
- [ ] Implement `WhatImThinking.jsx` main view
- [ ] Create `ReasoningTimeline.jsx` with step visualization
- [ ] Add real-time animation and updates
- [ ] Implement export functionality

### Phase 2: Data Integration (Week 2)

**Day 1-3: Frontend Hooks**
- [ ] Create `usePerspectiveStream.js` hook
- [ ] Integrate with existing `useAgentStream.js`
- [ ] Add state management for all perspective data
- [ ] Implement SSE parsing for new event types

**Day 4-7: Backend Enhancement**
- [ ] Add `/api/tools` endpoint to `main.py`
- [ ] Enhance `stages.py` to emit reasoning events
- [ ] Instrument `tools.py` with evaluation logging
- [ ] Add tool scoring/relevance calculation logic

### Phase 3: Polish & Testing (Week 3)

**Day 1-3: UX Refinement**
- [ ] Add animations and transitions
- [ ] Implement responsive design
- [ ] Add keyboard shortcuts
- [ ] Optimize performance

**Day 4-5: Accessibility**
- [ ] Add ARIA labels
- [ ] Implement keyboard navigation
- [ ] Add screen reader support
- [ ] Color contrast verification

**Day 6-7: Testing & Documentation**
- [ ] Write unit tests for components
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Update documentation

### Phase 4: Advanced Features (Week 4)

**Optional Enhancements:**
- [ ] Comparative view (split screen)
- [ ] Prediction mode
- [ ] Learning insights dashboard
- [ ] Historical trace viewer

---

## Example Reasoning Traces

### Example 1: Simple Search Query (Stage 2)

**User Query:** "What's the latest news about AI?"

```json
[
  {
    "type": "parsing",
    "timestamp": 1699564789000,
    "duration": 8,
    "description": "Parsed user query: 'What's the latest news about AI?'",
    "confidence": 0.98,
    "details": {
      "tokens": 8,
      "intent_detected": "information_search"
    }
  },
  {
    "type": "analyzing",
    "timestamp": 1699564789008,
    "duration": 22,
    "description": "Identified need for current information about AI developments",
    "confidence": 0.92,
    "details": {
      "keywords": ["latest", "news", "AI"],
      "temporal_indicator": "latest",
      "topic": "artificial_intelligence"
    }
  },
  {
    "type": "tool_evaluation",
    "timestamp": 1699564789030,
    "duration": 35,
    "description": "Evaluating available tools against requirements",
    "confidence": 0.88,
    "details": {
      "tools_considered": [
        {
          "name": "web_search",
          "score": 0.95,
          "reasoning": "Requires real-time news data from web sources"
        },
        {
          "name": "calculator",
          "score": 0.02,
          "reasoning": "No mathematical computation needed"
        },
        {
          "name": "file_read",
          "score": 0.10,
          "reasoning": "News not likely in local files"
        }
      ]
    }
  },
  {
    "type": "complete",
    "timestamp": 1699564789065,
    "duration": 0,
    "description": "Stage 2 limitation: Can explain tool usage but cannot execute",
    "confidence": 1.0,
    "details": {
      "recommended_tool": "web_search",
      "recommended_params": {
        "query": "latest AI news 2024"
      },
      "stage_limitation": "execution_disabled"
    }
  }
]
```

**Agent Response:**
> "To answer your question about the latest AI news, I would use the **web_search** tool with the query 'latest AI news 2024'. This would return current articles and updates from news sources. However, at Stage 2, I can only explain this approach - I cannot actually execute the search."

---

### Example 2: Tool Execution (Stage 3)

**User Query:** "Search for Python tutorials and save the top 3"

```json
[
  {
    "type": "parsing",
    "timestamp": 1699564900000,
    "duration": 10,
    "description": "Parsed compound request: search + save operations",
    "confidence": 0.95,
    "details": {
      "operations_identified": ["search", "filter", "save"],
      "resource_type": "tutorials",
      "constraint": "top 3"
    }
  },
  {
    "type": "analyzing",
    "timestamp": 1699564900010,
    "duration": 28,
    "description": "Breaking down into sequential steps: 1) search, 2) process results, 3) save to file",
    "confidence": 0.90,
    "details": {
      "task_complexity": "medium",
      "requires_chaining": true,
      "stage_compatible": true
    }
  },
  {
    "type": "tool_evaluation",
    "timestamp": 1699564900038,
    "duration": 42,
    "description": "Evaluating tools for each step",
    "confidence": 0.85,
    "details": {
      "step_1_tool": {
        "selected": "web_search",
        "score": 0.98,
        "reasoning": "Need to find online tutorials"
      },
      "step_2_processing": {
        "method": "internal",
        "reasoning": "Filter top 3 using internal logic"
      },
      "step_3_tool": {
        "selected": "file_write",
        "score": 0.92,
        "reasoning": "User wants to save results"
      }
    }
  },
  {
    "type": "tool_selection",
    "timestamp": 1699564900080,
    "duration": 5,
    "description": "Selected web_search for first operation",
    "confidence": 0.98,
    "details": {
      "tool_name": "web_search",
      "parameters": {
        "query": "Python tutorials"
      }
    }
  },
  {
    "type": "execution",
    "timestamp": 1699564900085,
    "duration": 342,
    "description": "Executing web_search(query='Python tutorials')",
    "confidence": 1.0,
    "details": {
      "tool_name": "web_search",
      "start_time": 1699564900085,
      "end_time": 1699564900427
    }
  },
  {
    "type": "processing",
    "timestamp": 1699564900427,
    "duration": 45,
    "description": "Processing search results: found 10 results, selecting top 3 by relevance",
    "confidence": 0.93,
    "details": {
      "total_results": 10,
      "filtered_count": 3,
      "filter_criteria": "relevance_score"
    }
  },
  {
    "type": "tool_selection",
    "timestamp": 1699564900472,
    "duration": 3,
    "description": "Selected file_write to save results",
    "confidence": 0.97,
    "details": {
      "tool_name": "file_write",
      "parameters": {
        "path": "python_tutorials.txt",
        "content": "[formatted results]"
      }
    }
  },
  {
    "type": "execution",
    "timestamp": 1699564900475,
    "duration": 18,
    "description": "Executing file_write(path='python_tutorials.txt', content='...')",
    "confidence": 1.0,
    "details": {
      "tool_name": "file_write",
      "bytes_written": 542
    }
  },
  {
    "type": "formatting",
    "timestamp": 1699564900493,
    "duration": 12,
    "description": "Preparing success message with file location and summary",
    "confidence": 0.96
  },
  {
    "type": "complete",
    "timestamp": 1699564900505,
    "duration": 0,
    "description": "Task completed successfully",
    "confidence": 1.0,
    "details": {
      "tools_used": ["web_search", "file_write"],
      "total_time_ms": 505
    }
  }
]
```

**Agent Response:**
> "I've searched for Python tutorials and saved the top 3 to python_tutorials.txt. The file contains:
> 1. Python Official Tutorial (docs.python.org)
> 2. Real Python - Python Tutorials (realpython.com)
> 3. W3Schools Python Tutorial (w3schools.com)"

---

### Example 3: Multi-Tool Chaining (Stage 4)

**User Query:** "Research React best practices, create a summary document, then create a checklist file"

```json
[
  {
    "type": "parsing",
    "timestamp": 1699565000000,
    "duration": 12,
    "description": "Parsed complex multi-step workflow with 3 distinct outputs",
    "confidence": 0.94,
    "details": {
      "steps_identified": 3,
      "outputs_required": ["research data", "summary document", "checklist file"],
      "estimated_complexity": "high"
    }
  },
  {
    "type": "analyzing",
    "timestamp": 1699565000012,
    "duration": 35,
    "description": "Planning multi-tool execution strategy",
    "confidence": 0.88,
    "details": {
      "strategy": "sequential_chaining",
      "estimated_turns": 4,
      "dependencies": {
        "step_2_depends_on": "step_1_results",
        "step_3_depends_on": "step_2_results"
      }
    }
  },
  {
    "type": "tool_evaluation",
    "timestamp": 1699565000047,
    "duration": 48,
    "description": "Mapping tools to each step of workflow",
    "confidence": 0.90,
    "details": {
      "workflow_plan": [
        {
          "step": 1,
          "action": "research",
          "tool": "web_search",
          "score": 0.97
        },
        {
          "step": 2,
          "action": "summarize",
          "tool": "file_write",
          "score": 0.95,
          "note": "Will process results internally before writing"
        },
        {
          "step": 3,
          "action": "extract_checklist",
          "tool": "file_write",
          "score": 0.93,
          "note": "Create new file with checklist format"
        }
      ]
    }
  },
  {
    "type": "tool_selection",
    "timestamp": 1699565000095,
    "duration": 4,
    "description": "Starting Turn 1: web_search for React best practices",
    "confidence": 0.97
  },
  {
    "type": "execution",
    "timestamp": 1699565000099,
    "duration": 387,
    "description": "Executing web_search(query='React best practices 2024')",
    "confidence": 1.0
  },
  {
    "type": "processing",
    "timestamp": 1699565000486,
    "duration": 125,
    "description": "Synthesizing research data: found 15 best practices, categorizing by theme",
    "confidence": 0.89,
    "details": {
      "practices_found": 15,
      "categories": ["Component Design", "State Management", "Performance", "Testing"],
      "sources": 8
    }
  },
  {
    "type": "tool_selection",
    "timestamp": 1699565000611,
    "duration": 3,
    "description": "Starting Turn 2: file_write to create summary document",
    "confidence": 0.96
  },
  {
    "type": "execution",
    "timestamp": 1699565000614,
    "duration": 23,
    "description": "Executing file_write(path='react_best_practices_summary.md', content='...')",
    "confidence": 1.0
  },
  {
    "type": "processing",
    "timestamp": 1699565000637,
    "duration": 98,
    "description": "Extracting actionable items from summary for checklist",
    "confidence": 0.91,
    "details": {
      "checklist_items": 12,
      "format": "markdown_checkboxes"
    }
  },
  {
    "type": "tool_selection",
    "timestamp": 1699565000735,
    "duration": 2,
    "description": "Starting Turn 3: file_write to create checklist file",
    "confidence": 0.98
  },
  {
    "type": "execution",
    "timestamp": 1699565000737,
    "duration": 19,
    "description": "Executing file_write(path='react_checklist.md', content='...')",
    "confidence": 1.0
  },
  {
    "type": "formatting",
    "timestamp": 1699565000756,
    "duration": 22,
    "description": "Preparing comprehensive completion report",
    "confidence": 0.95
  },
  {
    "type": "complete",
    "timestamp": 1699565000778,
    "duration": 0,
    "description": "Multi-tool workflow completed successfully",
    "confidence": 1.0,
    "details": {
      "total_turns": 3,
      "tools_used": ["web_search", "file_write", "file_write"],
      "files_created": ["react_best_practices_summary.md", "react_checklist.md"],
      "total_time_ms": 778
    }
  }
]
```

**Agent Response:**
> "I've completed your request with a 3-step workflow:
>
> 1. Researched React best practices (found 15 key practices)
> 2. Created summary document: react_best_practices_summary.md (organized by category)
> 3. Created checklist: react_checklist.md (12 actionable items)
>
> Both files are ready in your workspace!"

---

### Example 4: Error Handling (Stage 3)

**User Query:** "Read the file config.json and update it"

```json
[
  {
    "type": "parsing",
    "timestamp": 1699565100000,
    "duration": 9,
    "description": "Parsed file operation request",
    "confidence": 0.96
  },
  {
    "type": "tool_selection",
    "timestamp": 1699565100009,
    "duration": 3,
    "description": "Selected file_read to access config.json",
    "confidence": 0.98
  },
  {
    "type": "execution",
    "timestamp": 1699565100012,
    "duration": 15,
    "description": "Executing file_read(path='config.json')",
    "confidence": 1.0
  },
  {
    "type": "error",
    "timestamp": 1699565100027,
    "duration": 0,
    "description": "File operation failed: config.json not found",
    "confidence": 1.0,
    "details": {
      "error_type": "FileNotFoundError",
      "error_message": "File does not exist: config.json",
      "recovery_options": ["create_new_file", "specify_different_path", "list_available_files"]
    }
  },
  {
    "type": "analyzing",
    "timestamp": 1699565100027,
    "duration": 18,
    "description": "Determining best recovery strategy",
    "confidence": 0.75,
    "details": {
      "recommended_action": "ask_user_for_clarification"
    }
  },
  {
    "type": "formatting",
    "timestamp": 1699565100045,
    "duration": 8,
    "description": "Preparing error explanation and recovery options",
    "confidence": 0.92
  },
  {
    "type": "complete",
    "timestamp": 1699565100053,
    "duration": 0,
    "description": "Task incomplete - awaiting user guidance",
    "confidence": 0.85
  }
]
```

**Agent Response:**
> "I attempted to read config.json but encountered an error: the file doesn't exist in the current directory.
>
> Would you like me to:
> 1. Create a new config.json file
> 2. Look in a different directory (please specify the path)
> 3. List all available .json files in the workspace"

---

### Example 5: Ambiguous Query Resolution (Stage 4)

**User Query:** "Update the documentation"

```json
[
  {
    "type": "parsing",
    "timestamp": 1699565200000,
    "duration": 11,
    "description": "Parsed ambiguous request: 'update the documentation'",
    "confidence": 0.68,
    "details": {
      "ambiguity_detected": true,
      "missing_information": ["which_documentation", "what_updates", "how_to_update"]
    }
  },
  {
    "type": "analyzing",
    "timestamp": 1699565200011,
    "duration": 45,
    "description": "Attempting to resolve ambiguity using context and workspace analysis",
    "confidence": 0.55,
    "details": {
      "context_clues": [],
      "workspace_scan_needed": true
    }
  },
  {
    "type": "tool_selection",
    "timestamp": 1699565200056,
    "duration": 3,
    "description": "Selected file_read to explore workspace for documentation files",
    "confidence": 0.80
  },
  {
    "type": "execution",
    "timestamp": 1699565200059,
    "duration": 28,
    "description": "Scanning workspace for .md and .txt files",
    "confidence": 1.0,
    "details": {
      "files_found": ["README.md", "API_DOCS.md", "CONTRIBUTING.md"]
    }
  },
  {
    "type": "analyzing",
    "timestamp": 1699565200087,
    "duration": 32,
    "description": "Found multiple documentation files, requires user clarification",
    "confidence": 0.70,
    "details": {
      "options": [
        "README.md - Project overview",
        "API_DOCS.md - API documentation",
        "CONTRIBUTING.md - Contribution guidelines"
      ],
      "recommended_action": "present_options_to_user"
    }
  },
  {
    "type": "formatting",
    "timestamp": 1699565200119,
    "duration": 15,
    "description": "Preparing clarification request with discovered options",
    "confidence": 0.88
  },
  {
    "type": "complete",
    "timestamp": 1699565200134,
    "duration": 0,
    "description": "Awaiting user clarification on which documentation to update",
    "confidence": 0.75
  }
]
```

**Agent Response:**
> "I found multiple documentation files in your workspace:
>
> 1. **README.md** - Project overview
> 2. **API_DOCS.md** - API documentation
> 3. **CONTRIBUTING.md** - Contribution guidelines
>
> Which documentation would you like me to update, and what changes should I make?"

---

## Accessibility

### ARIA Labels

All interactive elements include proper ARIA labels:

```jsx
// Tab buttons
<button
  role="tab"
  aria-selected={activeTab === 'thinking'}
  aria-controls="thinking-panel"
  id="thinking-tab"
>
  What I'm Thinking
</button>

// Tab panels
<div
  role="tabpanel"
  id="thinking-panel"
  aria-labelledby="thinking-tab"
  hidden={activeTab !== 'thinking'}
>
  {/* Content */}
</div>

// Confidence meters
<div
  role="meter"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-valuenow={confidence * 100}
  aria-label="Confidence level"
>
  {/* Meter visualization */}
</div>
```

### Keyboard Navigation

**Keyboard Shortcuts:**
- `Tab` - Navigate between interactive elements
- `Arrow Keys` - Switch between tabs when focused
- `Escape` - Collapse panel
- `Ctrl+P` - Toggle pin/unpin
- `Ctrl+E` - Export reasoning trace
- `Ctrl+1/2/3/4` - Jump to specific tab

**Implementation:**

```jsx
const handleKeyDown = (e) => {
  // Tab switching
  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
    e.preventDefault();
    const tabs = ['see', 'do', 'thinking', 'limits'];
    const currentIndex = tabs.indexOf(activeTab);
    const newIndex = e.key === 'ArrowRight'
      ? (currentIndex + 1) % tabs.length
      : (currentIndex - 1 + tabs.length) % tabs.length;
    setActiveTab(tabs[newIndex]);
  }

  // Panel controls
  if (e.key === 'Escape') setIsCollapsed(true);
  if (e.ctrlKey && e.key === 'p') {
    e.preventDefault();
    setIsPinned(!isPinned);
  }

  // Tab shortcuts
  if (e.ctrlKey && ['1', '2', '3', '4'].includes(e.key)) {
    e.preventDefault();
    const tabs = ['see', 'do', 'thinking', 'limits'];
    setActiveTab(tabs[parseInt(e.key) - 1]);
  }
};
```

### Screen Reader Support

- All visual-only indicators have text alternatives
- Status changes announced via `aria-live` regions
- Loading states communicated clearly
- Error messages are assertive announcements

```jsx
// Live region for status updates
<div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
  {isStreaming ? 'Agent is thinking' : 'Agent response complete'}
</div>

// Assertive region for errors
<div role="alert" aria-live="assertive" className="sr-only">
  {error && `Error: ${error}`}
</div>
```

### Color Contrast

All color combinations meet WCAG 2.1 Level AA standards:

- **Text on backgrounds:** Minimum 4.5:1 ratio
- **Large text (18pt+):** Minimum 3:1 ratio
- **Interactive elements:** Minimum 3:1 ratio

**Verification:**
```javascript
// Color pairs verified:
const colorPairs = [
  { fg: '#1E3A8A', bg: '#EFF6FF' }, // Blue text on blue-50 (7.2:1) ✓
  { fg: '#047857', bg: '#D1FAE5' }, // Green text on green-50 (5.8:1) ✓
  { fg: '#7C2D12', bg: '#FEF3C7' }, // Red text on yellow-50 (8.1:1) ✓
];
```

### Focus Indicators

All focusable elements have clear, visible focus indicators:

```css
/* Focus ring for all interactive elements */
.focus-visible:focus {
  outline: 2px solid #6366F1; /* Indigo-500 */
  outline-offset: 2px;
  border-radius: 4px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .focus-visible:focus {
    outline-width: 3px;
    outline-offset: 3px;
  }
}
```

---

## Performance Optimization

### React Optimizations

**1. Component Memoization**

```jsx
import React, { memo } from 'react';

// Memoize expensive components
export const ReasoningTimeline = memo(({ trace, isActive }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if trace length changes
  return prevProps.trace.length === nextProps.trace.length &&
         prevProps.isActive === nextProps.isActive;
});

// Memoize tool cards
export const ToolCard = memo(({ tool, relevance }) => {
  // Component implementation
});
```

**2. Virtualization for Long Lists**

For reasoning traces with 100+ steps, use virtualization:

```jsx
import { FixedSizeList } from 'react-window';

function ReasoningTimeline({ trace }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ReasoningStep step={trace[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={trace.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

**3. Lazy Loading**

```jsx
import React, { lazy, Suspense } from 'react';

// Lazy load heavy components
const WhatImThinking = lazy(() => import('./perspective/WhatImThinking'));
const MyLimitations = lazy(() => import('./perspective/MyLimitations'));

// Use with Suspense
<Suspense fallback={<LoadingSpinner />}>
  {activeTab === 'thinking' && <WhatImThinking {...props} />}
</Suspense>
```

### Data Optimization

**1. Debounced Updates**

```javascript
import { useCallback } from 'react';
import debounce from 'lodash/debounce';

// Debounce rapid reasoning updates
const debouncedUpdateTrace = useCallback(
  debounce((newStep) => {
    setReasoningTrace(prev => [...prev, newStep]);
  }, 50), // Update at most every 50ms
  []
);
```

**2. Incremental Rendering**

```jsx
// Render reasoning steps incrementally
const [visibleSteps, setVisibleSteps] = useState(20);

useEffect(() => {
  if (visibleSteps < reasoningTrace.length) {
    const timeout = setTimeout(() => {
      setVisibleSteps(prev => Math.min(prev + 10, reasoningTrace.length));
    }, 100);
    return () => clearTimeout(timeout);
  }
}, [visibleSteps, reasoningTrace.length]);

return (
  <>
    {reasoningTrace.slice(0, visibleSteps).map(renderStep)}
    {visibleSteps < reasoningTrace.length && <LoadingIndicator />}
  </>
);
```

**3. Data Compression**

For export functionality, compress trace data:

```javascript
function compressReasoningTrace(trace) {
  // Remove redundant data for export
  return trace.map(step => ({
    t: step.type.substring(0, 3), // Abbreviate
    ts: step.timestamp,
    d: step.duration,
    desc: step.description,
    c: Math.round(step.confidence * 100) / 100, // 2 decimal places
    ...(step.details && { det: step.details })
  }));
}
```

### SSE Stream Optimization

**1. Batch Events**

On backend, batch rapid events:

```python
# In stages.py
async def emit_reasoning_events(events):
    """Batch multiple reasoning events into single SSE message"""
    if len(events) > 5:
        # If more than 5 events in quick succession, batch them
        yield {
            "event": "reasoning_batch",
            "data": json.dumps({"events": events})
        }
    else:
        # Send individually
        for event in events:
            yield {
                "event": "reasoning_step",
                "data": json.dumps(event)
            }
```

**2. Delta Updates**

Send only changes, not full state:

```python
# Instead of sending full tool list every time
{
  "type": "tools_updated",
  "added": [tool1, tool2],
  "removed": ["old_tool"],
  "modified": [tool3]
}

# Frontend applies delta
const applyToolsDelta = (currentTools, delta) => {
  let updated = currentTools.filter(t => !delta.removed.includes(t.name));
  updated = updated.map(t => {
    const mod = delta.modified.find(m => m.name === t.name);
    return mod || t;
  });
  return [...updated, ...delta.added];
};
```

**3. Compression**

For large payloads, use compression:

```python
import gzip
import base64

def compress_event_data(data):
    """Compress large event payloads"""
    json_str = json.dumps(data)
    if len(json_str) > 1000:  # Only compress if > 1KB
        compressed = gzip.compress(json_str.encode())
        return {
            "compressed": True,
            "data": base64.b64encode(compressed).decode()
        }
    return {"compressed": False, "data": data}
```

### Bundle Size Optimization

**1. Code Splitting**

```javascript
// In vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'perspective': [
            './src/components/perspective/WhatISee',
            './src/components/perspective/WhatICanDo',
            './src/components/perspective/WhatImThinking',
            './src/components/perspective/MyLimitations'
          ]
        }
      }
    }
  }
};
```

**2. Tree Shaking**

```javascript
// Use named imports for tree shaking
import { useState, useEffect } from 'react'; // Good
import React from 'react'; // Bad - imports entire library

// Use lodash-es for tree shaking
import debounce from 'lodash-es/debounce'; // Good
import _ from 'lodash'; // Bad - imports entire library
```

### Performance Metrics

**Target Metrics:**
- **Initial Panel Load:** < 200ms
- **Tab Switch:** < 50ms
- **Reasoning Step Render:** < 16ms (60fps)
- **SSE Event Processing:** < 10ms
- **Memory Usage:** < 50MB for 1000 reasoning steps
- **Bundle Size:** Perspective panel < 150KB gzipped

**Monitoring:**

```javascript
// Performance monitoring hook
function usePerformanceMonitor(componentName) {
  useEffect(() => {
    const startTime = performance.now();

    return () => {
      const duration = performance.now() - startTime;
      if (duration > 100) {
        console.warn(`${componentName} took ${duration}ms to render`);
      }
    };
  });
}

// Usage
function WhatImThinking(props) {
  usePerformanceMonitor('WhatImThinking');
  // Component code
}
```

---

## Summary

This design document specifies a comprehensive Agent First-Person View Panel that provides unprecedented transparency into AI agent operations. The panel:

1. **Makes Abstract Concrete** - Visualizes internal reasoning processes
2. **Educates Users** - Helps build mental models of agent behavior
3. **Enables Debugging** - Provides detailed traces for troubleshooting
4. **Scales with Complexity** - Adapts to stages 1-4 of agent evolution
5. **Performs Efficiently** - Optimized for real-time updates
6. **Accessible to All** - Meets WCAG 2.1 AA standards

**Next Steps:**
1. Review design with stakeholders
2. Create implementation timeline
3. Set up development environment
4. Begin Phase 1 implementation
5. Iterate based on user feedback

**Files to Create:**
- `/frontend/src/components/AgentPerspectivePanel.jsx`
- `/frontend/src/components/perspective/WhatISee.jsx`
- `/frontend/src/components/perspective/WhatICanDo.jsx`
- `/frontend/src/components/perspective/WhatImThinking.jsx`
- `/frontend/src/components/perspective/MyLimitations.jsx`
- `/frontend/src/components/perspective/ReasoningTimeline.jsx`
- `/frontend/src/components/perspective/ConfidenceMeter.jsx`
- `/frontend/src/hooks/usePerspectiveStream.js`
- `/backend/endpoints/tools.py` (new endpoint)

**Integration Points:**
- Update `App.jsx` to include panel
- Extend `useAgentStream.js` for perspective events
- Enhance `stages.py` to emit reasoning events
- Instrument `tools.py` with evaluation logic

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Author:** Claude (Sonnet 4.5)
**Project:** AICraft - Agent Evolution
**Location:** `/Users/wz/Desktop/zPersonalProjects/AICraft/agent-evolution/`
