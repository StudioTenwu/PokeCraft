import React, { useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

export default function AgentArchitectureDiagram({ config }) {
  const { systemPrompt, tools, maxTurns, chainingStrategy } = config;

  // Create nodes based on config
  const initialNodes = [
    {
      id: '1',
      type: 'input',
      data: { label: '📨 User Query' },
      position: { x: 250, y: 0 },
      style: { background: '#3B82F6', color: 'white', border: '2px solid #1D4ED8' }
    },
    {
      id: '2',
      data: {
        label: (
          <div className="p-2">
            <div className="font-bold">🧠 System Prompt</div>
            <div className="text-xs mt-1 max-w-xs truncate">
              {systemPrompt || 'Not configured'}
            </div>
          </div>
        )
      },
      position: { x: 200, y: 100 },
      style: { background: '#F3F4F6', border: '2px solid #9CA3AF', width: 250 }
    },
    {
      id: '3',
      data: {
        label: (
          <div className="p-2">
            <div className="font-bold">🔧 Tool Library</div>
            <div className="text-xs mt-1">
              {tools?.length || 0} tools available
            </div>
          </div>
        )
      },
      position: { x: 200, y: 220 },
      style: { background: '#FEF3C7', border: '2px solid #F59E0B', width: 250 }
    },
    {
      id: '4',
      data: {
        label: (
          <div className="p-2">
            <div className="font-bold">⚙️ Agent Engine</div>
            <div className="text-xs mt-1">
              Max turns: {maxTurns || 5}
            </div>
          </div>
        )
      },
      position: { x: 225, y: 340 },
      style: { background: '#DBEAFE', border: '2px solid #3B82F6', width: 200 }
    }
  ];

  // Add tool nodes if tools are configured
  if (tools && tools.length > 0) {
    tools.forEach((tool, idx) => {
      initialNodes.push({
        id: `tool-${idx}`,
        data: { label: `🛠️ ${tool}` },
        position: { x: 500 + (idx * 120), y: 220 },
        style: {
          background: '#D1FAE5',
          border: '2px solid #10B981',
          fontSize: '12px',
          padding: '8px'
        }
      });
    });
  }

  // Add response node
  initialNodes.push({
    id: '5',
    type: 'output',
    data: { label: '💬 Agent Response' },
    position: { x: 250, y: 480 },
    style: { background: '#34D399', color: 'white', border: '2px solid #059669' }
  });

  // Create edges
  const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#3B82F6' } },
    { id: 'e2-4', source: '2', target: '4', animated: true, style: { stroke: '#3B82F6' } },
    { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#F59E0B' } },
    { id: 'e4-5', source: '4', target: '5', animated: true, style: { stroke: '#10B981' } },
  ];

  // Add edges for tools
  if (tools && tools.length > 0) {
    tools.forEach((tool, idx) => {
      initialEdges.push({
        id: `e-tool-${idx}`,
        source: '3',
        target: `tool-${idx}`,
        style: { stroke: '#F59E0B', strokeDasharray: '5,5' }
      });
      initialEdges.push({
        id: `e-tool-${idx}-4`,
        source: `tool-${idx}`,
        target: '4',
        animated: true,
        style: { stroke: '#10B981' }
      });
    });
  }

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="h-96 bg-white rounded-lg border-2 border-gray-300">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-left"
      >
        <Background color="#aaa" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'input') return '#3B82F6';
            if (node.type === 'output') return '#34D399';
            if (node.id.startsWith('tool-')) return '#10B981';
            return '#9CA3AF';
          }}
        />
      </ReactFlow>
    </div>
  );
}
