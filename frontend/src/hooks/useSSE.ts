import { useState, useRef, useCallback } from 'react';

export interface ToolCall {
  name: string;
  input: Record<string, unknown>;
  result?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: ToolCall[];
  isStreaming?: boolean;
}

interface SSEEvent {
  event: string;
  data: string;
}

function parseSSELines(chunk: string): SSEEvent[] {
  const events: SSEEvent[] = [];
  const lines = chunk.split('\n');
  let currentEvent = '';
  let currentData = '';

  for (const line of lines) {
    if (line.startsWith('event: ')) {
      currentEvent = line.slice(7).trim();
    } else if (line.startsWith('data: ')) {
      currentData = line.slice(6);
    } else if (line === '' && (currentEvent || currentData)) {
      events.push({ event: currentEvent || 'message', data: currentData });
      currentEvent = '';
      currentData = '';
    }
  }

  return events;
}

export function useSSE() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sessionIdRef = useRef<string>(crypto.randomUUID());
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: '',
      toolCalls: [],
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMessage]);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionIdRef.current,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Chat error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedContent = '';
      const accumulatedToolCalls: ToolCall[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE events (separated by double newlines)
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          const events = parseSSELines(part + '\n');

          for (const sseEvent of events) {
            let parsed: Record<string, unknown>;
            try {
              parsed = JSON.parse(sseEvent.data);
            } catch {
              continue;
            }

            switch (sseEvent.event) {
              case 'thinking':
                // Optionally show thinking indicator; skip content accumulation
                break;

              case 'text':
                accumulatedContent += (parsed.content as string) || '';
                break;

              case 'tool_call':
                accumulatedToolCalls.push({
                  name: parsed.name as string,
                  input: (parsed.input as Record<string, unknown>) || {},
                });
                break;

              case 'tool_result': {
                const toolName = parsed.name as string;
                const existing = accumulatedToolCalls.find(
                  (tc) => tc.name === toolName && !tc.result
                );
                if (existing) {
                  existing.result = parsed.result as string;
                }
                break;
              }

              case 'error':
                accumulatedContent +=
                  `\n\n[Error: ${(parsed.message as string) || 'Unknown error'}]`;
                break;

              case 'done':
                // Stream complete
                break;
            }

            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === 'assistant') {
                updated[updated.length - 1] = {
                  ...last,
                  content: accumulatedContent,
                  toolCalls: [...accumulatedToolCalls],
                  isStreaming: sseEvent.event !== 'done',
                };
              }
              return updated;
            });
          }
        }
      }

      // Finalize the message
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          updated[updated.length - 1] = {
            ...last,
            content: accumulatedContent,
            toolCalls: accumulatedToolCalls.length > 0 ? accumulatedToolCalls : undefined,
            isStreaming: false,
          };
        }
        return updated;
      });
    } catch (err) {
      if ((err as Error).name === 'AbortError') return;

      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          updated[updated.length - 1] = {
            ...last,
            content: last.content || `Sorry, something went wrong: ${(err as Error).message}`,
            isStreaming: false,
          };
        }
        return updated;
      });
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [isLoading]);

  return {
    messages,
    isLoading,
    sendMessage,
    sessionId: sessionIdRef.current,
  };
}
