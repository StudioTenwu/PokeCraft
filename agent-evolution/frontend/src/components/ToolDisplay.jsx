import React from 'react';

export default function ToolDisplay({ toolEvents }) {
  if (toolEvents.length === 0) return null;

  return (
    <div className="mt-4 space-y-2">
      {toolEvents.map((event, idx) => {
        if (event.type === 'recognition') {
          return (
            <div key={idx} className="p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded">
              <div className="flex items-center">
                <span className="text-yellow-700 font-medium">🔍 Tool Recognized:</span>
                <span className="ml-2 font-mono text-sm text-yellow-900">{event.toolName}</span>
              </div>
              {event.input && (
                <div className="mt-1 text-xs text-yellow-800">
                  Input: {JSON.stringify(event.input, null, 2)}
                </div>
              )}
            </div>
          );
        }

        if (event.type === 'start') {
          return (
            <div key={idx} className="p-3 bg-blue-50 border-l-4 border-blue-400 rounded">
              <div className="flex items-center">
                <span className="text-blue-700 font-medium">⚙️ Tool Starting:</span>
                <span className="ml-2 font-mono text-sm text-blue-900">{event.toolName}</span>
              </div>
            </div>
          );
        }

        if (event.type === 'executing') {
          return (
            <div key={idx} className="p-3 bg-purple-50 border-l-4 border-purple-400 rounded">
              <div className="flex items-center">
                <span className="text-purple-700 font-medium">⚡ Executing:</span>
                <span className="ml-2 font-mono text-sm text-purple-900">{event.toolName}</span>
              </div>
              {event.input && (
                <div className="mt-2 text-xs bg-purple-100 p-2 rounded font-mono text-purple-900 overflow-x-auto">
                  {JSON.stringify(event.input, null, 2)}
                </div>
              )}
            </div>
          );
        }

        if (event.type === 'result') {
          return (
            <div key={idx} className="p-3 bg-green-50 border-l-4 border-green-400 rounded">
              <div className="flex items-center">
                <span className="text-green-700 font-medium">✅ Result from:</span>
                <span className="ml-2 font-mono text-sm text-green-900">{event.toolName}</span>
              </div>
              {event.result && (
                <div className="mt-2 text-xs bg-green-100 p-2 rounded font-mono text-green-900 overflow-x-auto max-h-40 overflow-y-auto">
                  {JSON.stringify(event.result, null, 2)}
                </div>
              )}
            </div>
          );
        }

        return null;
      })}
    </div>
  );
}
