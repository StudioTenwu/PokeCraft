import React, { useState } from 'react';
import { useDrag } from 'react-dnd';

const TOOL_SCHEMAS = {
  web_search: {
    name: "web_search",
    description: "Search the web for information",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" }
      },
      required: ["query"]
    }
  },
  file_write: {
    name: "file_write",
    description: "Write content to a file",
    input_schema: {
      type: "object",
      properties: {
        filename: { type: "string", description: "Name of the file" },
        content: { type: "string", description: "Content to write" }
      },
      required: ["filename", "content"]
    }
  },
  file_read: {
    name: "file_read",
    description: "Read content from a file",
    input_schema: {
      type: "object",
      properties: {
        filename: { type: "string", description: "Name of the file to read" }
      },
      required: ["filename"]
    }
  },
  calculator: {
    name: "calculator",
    description: "Perform mathematical calculations",
    input_schema: {
      type: "object",
      properties: {
        expression: { type: "string", description: "Mathematical expression to evaluate" }
      },
      required: ["expression"]
    }
  },
  image_gen: {
    name: "image_gen",
    description: "Generate images from text descriptions",
    input_schema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "Image description" },
        size: { type: "string", enum: ["256x256", "512x512", "1024x1024"] }
      },
      required: ["prompt"]
    }
  },
  code_exec: {
    name: "code_exec",
    description: "Execute Python code safely",
    input_schema: {
      type: "object",
      properties: {
        code: { type: "string", description: "Python code to execute" }
      },
      required: ["code"]
    }
  }
};

const TOOL_ICONS = {
  web_search: "🔍",
  file_write: "📝",
  file_read: "📖",
  calculator: "🔢",
  image_gen: "🎨",
  code_exec: "⚙️"
};

export default function ToolCard({ tool, status = 'hidden', onToggle, draggable = false }) {
  const [showSchema, setShowSchema] = useState(false);

  const toolData = TOOL_SCHEMAS[tool];
  const icon = TOOL_ICONS[tool] || "🔧";

  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'TOOL',
    item: { tool },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
    canDrag: draggable
  }), [tool, draggable]);

  const getStatusColor = () => {
    switch (status) {
      case 'hidden': return 'bg-gray-100 border-gray-300';
      case 'visible': return 'bg-yellow-50 border-yellow-400';
      case 'executable': return 'bg-green-50 border-green-500';
      default: return 'bg-gray-100 border-gray-300';
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'hidden': return null;
      case 'visible': return <span className="px-2 py-1 text-xs font-semibold bg-yellow-200 text-yellow-800 rounded">VISIBLE</span>;
      case 'executable': return <span className="px-2 py-1 text-xs font-semibold bg-green-200 text-green-800 rounded">EXECUTABLE</span>;
      default: return null;
    }
  };

  return (
    <div
      ref={draggable ? drag : null}
      className={`
        rounded-lg border-2 p-4 transition-all
        ${getStatusColor()}
        ${isDragging ? 'opacity-50' : 'opacity-100'}
        ${draggable ? 'cursor-move hover:shadow-lg' : ''}
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <div>
            <h3 className="font-bold text-gray-900">{toolData.name}</h3>
            {getStatusBadge()}
          </div>
        </div>
        {onToggle && status !== 'hidden' && (
          <button
            onClick={() => onToggle(tool)}
            className={`
              px-3 py-1 rounded text-sm font-medium transition-colors
              ${status === 'visible'
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-yellow-500 text-white hover:bg-yellow-600'
              }
            `}
          >
            {status === 'visible' ? 'Enable' : 'Disable'}
          </button>
        )}
      </div>

      <p className="text-sm text-gray-700 mb-3">{toolData.description}</p>

      <button
        onClick={() => setShowSchema(!showSchema)}
        className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
      >
        <span>{showSchema ? '▼' : '▶'}</span>
        View Schema
      </button>

      {showSchema && (
        <div className="mt-3 p-3 bg-gray-50 rounded border border-gray-200 overflow-x-auto">
          <pre className="text-xs text-gray-800 font-mono">
            {JSON.stringify(toolData.input_schema, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
