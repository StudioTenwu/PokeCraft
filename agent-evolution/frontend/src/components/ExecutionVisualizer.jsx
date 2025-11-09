import React, { useEffect, useState } from 'react';

export default function ExecutionVisualizer({ toolEvents, isActive }) {
  const [steps, setSteps] = useState([]);

  useEffect(() => {
    if (!isActive) {
      setSteps([]);
      return;
    }

    const newSteps = [
      { id: 1, label: 'Receive query', status: 'completed', color: 'bg-blue-500' },
      { id: 2, label: 'Plan approach', status: 'completed', color: 'bg-purple-500' }
    ];

    toolEvents.forEach((event, idx) => {
      if (event.type === 'executing' || event.type === 'start') {
        newSteps.push({
          id: newSteps.length + 1,
          label: `Use tool: ${event.toolName}`,
          status: 'active',
          color: 'bg-yellow-500',
          icon: '⚡'
        });
      } else if (event.type === 'result') {
        newSteps.push({
          id: newSteps.length + 1,
          label: `Process results from ${event.toolName}`,
          status: 'completed',
          color: 'bg-green-500',
          icon: '✓'
        });
      }
    });

    if (toolEvents.length > 0 && toolEvents[toolEvents.length - 1].type === 'result') {
      newSteps.push({
        id: newSteps.length + 1,
        label: 'Respond',
        status: 'active',
        color: 'bg-blue-500'
      });
    }

    setSteps(newSteps);
  }, [toolEvents, isActive]);

  if (!isActive || steps.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 p-4 bg-white rounded-lg border-2 border-purple-200">
      <h3 className="text-lg font-bold text-purple-900 mb-4 flex items-center gap-2">
        <span className="animate-pulse">🔄</span>
        Execution Flow
      </h3>

      <div className="space-y-3">
        {steps.map((step, idx) => (
          <div key={step.id} className="flex items-center gap-3">
            {/* Step number */}
            <div className={`
              flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
              text-white font-bold text-sm
              ${step.status === 'active' ? step.color + ' animate-pulse' : step.color}
            `}>
              {step.icon || step.id}
            </div>

            {/* Step label */}
            <div className="flex-1">
              <div className={`
                px-4 py-2 rounded-lg border-2
                ${step.status === 'active'
                  ? 'border-purple-400 bg-purple-50 animate-pulse'
                  : 'border-gray-200 bg-gray-50'
                }
              `}>
                <span className={`
                  font-medium
                  ${step.status === 'active' ? 'text-purple-900' : 'text-gray-700'}
                `}>
                  {step.label}
                </span>
              </div>
            </div>

            {/* Connection line to next step */}
            {idx < steps.length - 1 && (
              <div className="absolute left-7 w-0.5 h-6 bg-gray-300 mt-12" />
            )}
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-purple-50 rounded border border-purple-200">
        <p className="text-xs text-purple-700">
          <strong>Interactive Learning:</strong> Watch how the agent breaks down your request into discrete steps,
          executes tools in sequence, and synthesizes results into a coherent response.
        </p>
      </div>
    </div>
  );
}
