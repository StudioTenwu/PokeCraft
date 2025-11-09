import React, { useState } from 'react';
import Editor from '@monaco-editor/react';

const EXAMPLE_PROMPTS = [
  {
    title: "Helpful Assistant",
    prompt: "You are a helpful assistant. You provide clear, concise answers to user questions and maintain a friendly, professional tone."
  },
  {
    title: "Creative Storyteller",
    prompt: "You are a creative storyteller. You weave engaging narratives and help users explore imaginative ideas with vivid descriptions and compelling plots."
  },
  {
    title: "Technical Expert",
    prompt: "You are a technical expert. You provide detailed technical explanations, code examples, and debugging assistance with precision and clarity."
  }
];

export default function SystemPromptEditor({ value, onChange, showExamples = true }) {
  const [selectedExample, setSelectedExample] = useState(null);

  const handleExampleSelect = (example) => {
    setSelectedExample(example);
    onChange(example.prompt);
  };

  return (
    <div className="space-y-4">
      {showExamples && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Example Prompts (Click to use)</h3>
          <div className="grid grid-cols-3 gap-3">
            {EXAMPLE_PROMPTS.map((example, idx) => (
              <button
                key={idx}
                onClick={() => handleExampleSelect(example)}
                className={`
                  p-3 rounded-lg border-2 text-left transition-all
                  ${selectedExample?.title === example.title
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 bg-white hover:border-blue-300'
                  }
                `}
              >
                <div className="font-semibold text-sm text-gray-900 mb-1">{example.title}</div>
                <div className="text-xs text-gray-600 line-clamp-2">{example.prompt}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-700">System Prompt</h3>
          <span className="text-xs text-gray-500">
            {value?.length || 0} characters
          </span>
        </div>

        <div className="border-2 border-gray-300 rounded-lg overflow-hidden">
          <Editor
            height="200px"
            defaultLanguage="text"
            value={value}
            onChange={onChange}
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'off',
              wordWrap: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              padding: { top: 12, bottom: 12 }
            }}
            theme="vs"
          />
        </div>

        <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
          <p className="text-xs text-blue-700">
            <strong>Pro Tip:</strong> The system prompt shapes your agent's personality and behavior.
            Try different prompts and see how the agent's responses change!
          </p>
        </div>
      </div>
    </div>
  );
}
