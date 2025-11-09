import { useState, useCallback } from 'react';

export function useAgentStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const [toolEvents, setToolEvents] = useState([]);

  const sendMessage = useCallback(async (messages, stage, onComplete, config = null) => {
    setIsStreaming(true);
    setCurrentMessage('');
    setToolEvents([]);

    try {
      const requestBody = {
        messages,
        stage
      };

      // Include config if provided
      if (config) {
        requestBody.config = config;
      }

      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            try {
              const event = JSON.parse(data);

              if (event.type === 'text') {
                setCurrentMessage(prev => prev + event.content);
              } else if (event.type === 'tool_use') {
                // Tool is being used - track it
                setToolEvents(prev => [...prev, {
                  type: 'use',
                  toolName: event.tool_name,
                  input: event.tool_input
                }]);
              } else if (event.type === 'tool_result') {
                // Tool execution result
                setToolEvents(prev => [...prev, {
                  type: 'result',
                  toolName: event.tool_name,
                  result: event
                }]);
              } else if (event.type === 'done') {
                // Stream complete
              } else if (event.type === 'error') {
                console.error('Stream error:', event.error);
              }
            } catch (e) {
              console.error('Failed to parse event:', e);
            }
          }
        }
      }

      setIsStreaming(false);
      if (onComplete) {
        onComplete(currentMessage);
      }
    } catch (error) {
      console.error('Error in sendMessage:', error);
      setIsStreaming(false);
      throw error;
    }
  }, [currentMessage]);

  return {
    isStreaming,
    currentMessage,
    toolEvents,
    sendMessage,
    setCurrentMessage,
    setToolEvents
  };
}
