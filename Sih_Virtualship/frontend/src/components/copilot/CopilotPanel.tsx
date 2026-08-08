'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { X, Bot, Send, Search } from 'lucide-react';

interface Source {
  source_file: string;
  document_type: string;
  page: string;
  equipment_hint: string;
}

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  sources?: Source[];
}

interface CopilotPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CopilotPanel({ isOpen, onClose }: CopilotPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Math.random().toString(36).substr(2, 9)}`);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  useEffect(() => {
    // Poll for automated alerts from other services
    const pollAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8005/poll-alerts');
        if (!res.ok) return;
        const data = await res.json();
        if (data.alerts && data.alerts.length > 0) {
          data.alerts.forEach((alert: any) => {
            setMessages(prev => [...prev, {
              id: Date.now().toString() + Math.random(),
              role: 'ai',
              content: `🚨 **AUTOMATED ALERT: ${alert.title}**\n\n${alert.message}\n\n*Source: ${alert.source}*`,
            }]);
          });
        }
      } catch (e) {
        // Silent fail for polling
      }
    };

    const interval = setInterval(pollAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  const sendMessage = async (text: string) => {
    const userMsg = text.trim();
    if (!userMsg || isLoading) return;

    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8005/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: data.response,
        sources: data.sources,
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: '⚠ Unable to connect to the Copilot AI backend on port 8005.',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const autoResizeTextarea = () => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
    }
  };

  const getUniqueSources = (sources: Source[]) => {
    if (!sources) return [];
    const unique = new Map<string, Source>();
    sources.forEach(src => {
      if (!unique.has(src.source_file)) unique.set(src.source_file, src);
    });
    return Array.from(unique.values());
  };

  const renderSources = (sources: Source[]) => {
    const uniqueSources = getUniqueSources(sources);
    if (uniqueSources.length === 0) return null;

    return (
      <div className="mt-2 bg-slate-950/50 border border-slate-800 rounded p-2 text-xs">
        <div className="text-slate-500 font-semibold mb-1 flex items-center gap-1 uppercase tracking-wider text-[9px]">
          <Search className="h-3 w-3" /> Sources used
        </div>
        <div className="space-y-1">
          {uniqueSources.map((s, i) => (
            <div key={i} className="flex flex-col gap-0.5 text-slate-300">
              <span className="font-medium text-slate-200">{s.source_file}</span>
              {s.page && s.page !== 'N/A' && <span className="text-slate-500 text-[10px]">Page {s.page}</span>}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div 
      className={`fixed top-16 right-0 bottom-8 w-[400px] bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col transition-transform duration-300 ease-in-out z-40 ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {/* Header */}
      <div className="h-14 border-b border-slate-800 flex items-center justify-between px-4 bg-slate-950/30">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-sky-400" />
          <h2 className="font-semibold text-slate-200 tracking-tight text-sm">Marine Engineering Copilot</h2>
        </div>
        <button 
          onClick={onClose}
          className="text-slate-500 hover:text-slate-300 hover:bg-slate-800 p-1.5 rounded-md transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center opacity-60">
            <Bot className="h-12 w-12 text-slate-600 mb-3" />
            <h3 className="text-sm font-semibold text-slate-400">Ask the Copilot</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-[250px]">
              Query maintenance procedures, active alarms, and historical records.
            </p>
          </div>
        ) : (
          messages.map(msg => (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div 
                className={`max-w-[85%] rounded-lg p-3 text-sm ${
                  msg.role === 'user' 
                    ? 'bg-sky-600 text-white rounded-br-none' 
                    : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700'
                }`}
              >
                {msg.role === 'ai' && (
                  <div className="flex items-center gap-1.5 text-sky-400 font-semibold text-[10px] uppercase tracking-wider mb-2">
                    <Bot className="h-3.5 w-3.5" /> AI Response
                  </div>
                )}
                
                <div className="prose prose-invert prose-sm max-w-none">
                  {msg.role === 'ai' ? (
                    <ReactMarkdown 
                      components={{
                        p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2 last:mb-0" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2 last:mb-0" {...props} />,
                        li: ({node, ...props}) => <li className="mb-1" {...props} />,
                        h1: ({node, ...props}) => <h1 className="text-base font-bold text-sky-300 mt-3 mb-2" {...props} />,
                        h2: ({node, ...props}) => <h2 className="text-sm font-bold text-sky-300 mt-2 mb-1" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-sm font-bold text-slate-300 mt-2 mb-1" {...props} />,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>

                {msg.role === 'ai' && msg.sources && renderSources(msg.sources)}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex flex-col items-start">
            <div className="max-w-[85%] rounded-lg p-3 text-sm bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700">
              <div className="flex items-center gap-2">
                <div className="animate-spin h-3 w-3 border-2 border-sky-400 border-t-transparent rounded-full" />
                <span className="text-xs text-slate-400 animate-pulse">Analyzing logs & telemetry...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <div className="p-3 bg-slate-950/50 border-t border-slate-800">
        <form 
          className="relative bg-slate-900 border border-slate-700 rounded-md focus-within:border-sky-500 transition-colors flex items-end"
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
        >
          <textarea
            ref={textareaRef}
            className="flex-1 bg-transparent text-sm text-slate-200 p-2.5 resize-none max-h-32 focus:outline-none placeholder:text-slate-500"
            rows={1}
            value={input}
            onChange={e => { setInput(e.target.value); autoResizeTextarea(); }}
            onKeyDown={handleKeyDown}
            placeholder="Ask about engines or alarms..."
            disabled={isLoading}
          />
          <button 
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-2.5 text-sky-500 hover:text-sky-400 disabled:text-slate-600 transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
