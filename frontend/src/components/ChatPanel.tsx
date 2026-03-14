import { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Mic, ThumbsUp, ThumbsDown, Wrench } from 'lucide-react';
import { useSSE } from '../hooks/useSSE';
import { submitFeedback } from '../api/client';

interface SpeechRecognitionEvent {
  results: { [index: number]: { [index: number]: { transcript: string } } };
}

interface SpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognitionInstance;
    webkitSpeechRecognition: new () => SpeechRecognitionInstance;
  }
}

function toolCallLabel(name: string): string {
  const labels: Record<string, string> = {
    search_emails: 'Searching emails...',
    send_email: 'Sending email...',
    check_calendar: 'Checking calendar...',
    create_event: 'Creating event...',
    search_web: 'Searching the web...',
    draft_email: 'Drafting email...',
  };
  return labels[name] ?? `Running ${name.replace(/_/g, ' ')}...`;
}

export default function ChatPanel() {
  const { messages, isLoading, sendMessage } = useSSE();
  const [input, setInput] = useState('');
  const [listening, setListening] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<Record<number, string>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text) return;
    setInput('');
    sendMessage(text);
  }, [input, sendMessage]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleMicrophone = () => {
    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => (prev ? prev + ' ' + transcript : transcript));
    };

    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    recognition.onerror = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  };

  const handleFeedback = async (messageIndex: number, type: 'thumbs_up' | 'thumbs_down') => {
    setFeedbackGiven((prev) => ({ ...prev, [messageIndex]: type }));
    try {
      await submitFeedback(String(messageIndex), type);
    } catch {
      // silently fail
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-900">
      {/* Chat messages */}
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <p className="text-slate-400">Start a conversation with Cass...</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx}>
            <div
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-200'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
              </div>
            </div>

            {/* Tool calls */}
            {msg.toolCalls && msg.toolCalls.length > 0 && (
              <div className={`mt-1 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className="flex flex-wrap gap-1">
                  {msg.toolCalls.map((tc, tcIdx) => (
                    <span
                      key={tcIdx}
                      className="inline-flex items-center gap-1 rounded-full bg-slate-700 px-2 py-0.5 text-xs text-slate-300"
                    >
                      <Wrench className="h-3 w-3" />
                      {toolCallLabel(tc.name)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Streaming tool call indicator */}
            {msg.role === 'assistant' && msg.isStreaming && msg.toolCalls && msg.toolCalls.length > 0 && (
              <div className="mt-1 flex justify-start">
                <span className="inline-flex items-center gap-1 rounded-full bg-indigo-600/20 px-2 py-0.5 text-xs text-indigo-400 animate-pulse">
                  <Wrench className="h-3 w-3" />
                  {toolCallLabel(msg.toolCalls[msg.toolCalls.length - 1].name)}
                </span>
              </div>
            )}

            {/* Feedback buttons for assistant messages */}
            {msg.role === 'assistant' && !msg.isStreaming && (
              <div className="mt-1 flex justify-start gap-1">
                <button
                  onClick={() => handleFeedback(idx, 'thumbs_up')}
                  className={`rounded p-1 transition-colors ${
                    feedbackGiven[idx] === 'thumbs_up'
                      ? 'text-green-400'
                      : 'text-slate-500 hover:text-slate-300'
                  }`}
                  title="Good response"
                >
                  <ThumbsUp className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => handleFeedback(idx, 'thumbs_down')}
                  className={`rounded p-1 transition-colors ${
                    feedbackGiven[idx] === 'thumbs_down'
                      ? 'text-red-400'
                      : 'text-slate-500 hover:text-slate-300'
                  }`}
                  title="Bad response"
                >
                  <ThumbsDown className="h-3.5 w-3.5" />
                </button>
              </div>
            )}
          </div>
        ))}

        {/* Streaming / typing indicator */}
        {isLoading && messages.length > 0 && messages[messages.length - 1]?.isStreaming && !messages[messages.length - 1]?.content && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-slate-800 px-4 py-3">
              <div className="flex items-center gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '0ms' }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '150ms' }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-slate-700 bg-slate-800 p-4">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-sm text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:outline-none"
          />
          <button
            onClick={toggleMicrophone}
            className={`rounded-xl p-3 transition-colors ${
              listening
                ? 'bg-red-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
            title={listening ? 'Stop listening' : 'Start voice input'}
          >
            {listening ? (
              <span className="relative flex h-5 w-5 items-center justify-center">
                <Mic className="h-5 w-5" />
                <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 animate-ping rounded-full bg-red-300" />
                <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-red-400" />
              </span>
            ) : (
              <Mic className="h-5 w-5" />
            )}
          </button>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="rounded-xl bg-indigo-600 p-3 text-white transition-colors hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600"
            title="Send message"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
