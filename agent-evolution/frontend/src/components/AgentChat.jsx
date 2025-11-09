import React, { useState, useRef, useEffect } from 'react';
import { useAgentStream } from '../hooks/useAgentStream';
import ToolDisplay from './ToolDisplay';
import ExecutionVisualizer from './ExecutionVisualizer';

export default function AgentChat({ currentStage, currentStageInfo, config }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const { isStreaming, currentMessage, toolEvents, sendMessage, setCurrentMessage, setToolEvents } = useAgentStream();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentMessage, toolEvents]);

  const handleSendMessage = async (messageText = null) => {
    const text = messageText || inputValue.trim();
    if (!text || isStreaming) return;

    const newUserMessage = { role: 'user', content: text };
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    setInputValue('');

    try {
      await sendMessage(updatedMessages, currentStage, (finalMessage) => {
        if (finalMessage) {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: finalMessage
          }]);
          setCurrentMessage('');
          setToolEvents([]);
        }
      }, config);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`
      }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleTryKeyActivity = () => {
    if (currentStageInfo?.key_activity?.prompt) {
      handleSendMessage(currentStageInfo.key_activity.prompt);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-500 to-purple-500">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">
              Agent Chat - Stage {currentStage}
            </h2>
            <p className="text-sm text-blue-100 mt-1">
              {currentStageInfo?.description}
            </p>
          </div>
          {currentStageInfo?.key_activity && (
            <button
              onClick={handleTryKeyActivity}
              disabled={isStreaming}
              className="px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Try: {currentStageInfo.key_activity.title}
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-2">
              {currentStageInfo?.key_activity?.title && (
                <>Click "Try: {currentStageInfo.key_activity.title}" or type your own message</>
              )}
            </p>
          </div>
        )}

        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[80%] rounded-lg px-4 py-2
                ${message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'}
              `}
            >
              <div className="text-xs font-semibold mb-1 opacity-70">
                {message.role === 'user' ? 'You' : 'Agent'}
              </div>
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
          </div>
        ))}

        {/* Streaming message */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="max-w-[80%] bg-gray-100 text-gray-800 rounded-lg px-4 py-2">
              <div className="text-xs font-semibold mb-1 opacity-70">Agent</div>
              <div className="whitespace-pre-wrap">
                {currentMessage}
                <span className="inline-block w-2 h-4 ml-1 bg-gray-800 animate-pulse"></span>
              </div>

              {/* Tool events */}
              <ToolDisplay toolEvents={toolEvents} />
            </div>
          </div>
        )}

        {/* Execution Visualizer for Stage 3+ */}
        {currentStage >= 3 && isStreaming && (
          <ExecutionVisualizer toolEvents={toolEvents} isActive={true} />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Chat with Stage ${currentStage} agent...`}
            disabled={isStreaming}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={2}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isStreaming}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isStreaming ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
