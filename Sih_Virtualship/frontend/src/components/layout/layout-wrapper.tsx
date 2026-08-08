'use client';

import React, { useState } from 'react';
import { VesselProvider } from '../../providers/vessel-provider';
import { TopHeader } from './top-header';
import { LeftSidebar } from './left-sidebar';
import { StatusBar } from './status-bar';
import { CopilotPanel } from '../copilot/CopilotPanel';
import { Bot } from 'lucide-react';

interface LayoutWrapperProps {
  children: React.ReactNode;
}

export function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);

  return (
    <VesselProvider>
      <div className="flex flex-col h-screen overflow-hidden relative">
        {/* Top Operations Header */}
        <TopHeader onToggleCopilot={() => setIsCopilotOpen(!isCopilotOpen)} />

        {/* Center Area: Left Navigation Menu + Main scrollable viewports */}
        <div className="flex flex-1 overflow-hidden relative">
          <LeftSidebar />
          <main className="flex-1 overflow-y-auto bg-slate-950/20 p-4 xl:p-6 scrollbar-thin">
            {children}
          </main>
          
          {/* Slide-out AI Copilot Panel */}
          <CopilotPanel isOpen={isCopilotOpen} onClose={() => setIsCopilotOpen(false)} />

          {/* Floating Action Button for Copilot */}
          <button
            onClick={() => setIsCopilotOpen(!isCopilotOpen)}
            className={`fixed bottom-6 right-6 z-50 flex items-center justify-center gap-2 bg-sky-600 hover:bg-sky-500 text-white rounded-full p-4 shadow-lg shadow-sky-900/50 transition-all hover:scale-105 border border-sky-400/30 ${isCopilotOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}
          >
            <Bot className="h-6 w-6" />
            <span className="font-semibold pr-1">AI Copilot</span>
          </button>
        </div>

        {/* Bottom Status bar logger */}
        <StatusBar />
      </div>
    </VesselProvider>
  );
}
