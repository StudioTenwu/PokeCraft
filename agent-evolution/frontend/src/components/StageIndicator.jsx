import React from 'react';

export default function StageIndicator({ stages, currentStage, onStageChange }) {
  const getStageColor = (stageId) => {
    if (stageId < currentStage) return 'bg-green-500';
    if (stageId === currentStage) return 'bg-blue-500 ring-4 ring-blue-200';
    return 'bg-gray-300';
  };

  const getLineColor = (stageId) => {
    return stageId < currentStage ? 'bg-green-500' : 'bg-gray-300';
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-8 text-center text-gray-800">
        Agent Evolution Path
      </h2>

      <div className="relative">
        {/* Connection lines */}
        <div className="absolute top-8 left-0 right-0 flex justify-between px-12">
          {stages.slice(0, -1).map((stage, idx) => (
            <div
              key={`line-${stage.id}`}
              className={`h-1 flex-1 mx-4 transition-colors duration-500 ${getLineColor(stage.id)}`}
            />
          ))}
        </div>

        {/* Stage nodes */}
        <div className="relative flex justify-between">
          {stages.map((stage) => (
            <div
              key={stage.id}
              className="flex flex-col items-center"
              style={{ width: '200px' }}
            >
              {/* Circle */}
              <button
                onClick={() => onStageChange(stage.id)}
                disabled={stage.id > currentStage}
                className={`
                  w-16 h-16 rounded-full flex items-center justify-center
                  font-bold text-white text-xl transition-all duration-300
                  ${getStageColor(stage.id)}
                  ${stage.id <= currentStage ? 'cursor-pointer hover:scale-110' : 'cursor-not-allowed opacity-50'}
                `}
              >
                {stage.id}
              </button>

              {/* Stage info */}
              <div className="mt-4 text-center">
                <h3 className="font-semibold text-gray-800 mb-1">
                  {stage.name}
                </h3>
                <p className="text-xs text-gray-600 mb-2">
                  {stage.description}
                </p>

                {/* Capabilities */}
                <div className="flex flex-wrap gap-1 justify-center">
                  {stage.capabilities.map((cap, idx) => (
                    <span
                      key={idx}
                      className={`
                        text-xs px-2 py-1 rounded-full
                        ${stage.id <= currentStage
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-500'}
                      `}
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Current stage info */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-blue-900">
              Current Stage: {stages.find(s => s.id === currentStage)?.name}
            </h3>
            <p className="text-sm text-blue-700 mt-1">
              {stages.find(s => s.id === currentStage)?.description}
            </p>
          </div>
          {currentStage < 4 && (
            <button
              onClick={() => onStageChange(currentStage + 1)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
            >
              Unlock Stage {currentStage + 1}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
