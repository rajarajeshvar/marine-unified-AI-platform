'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useVessel } from '../../providers/vessel-provider';
import {
  LayoutDashboard,
  Cpu,
  Layers,
  Droplet,
  Compass,
  Wind,
  Wrench,
  Bell,
  Settings,
  ScanLine
} from 'lucide-react';

export function LeftSidebar() {
  const { activeTab, setActiveTab } = useVessel();
  const pathname = usePathname();
  const router = useRouter();

  const handleTabClick = (tabName: string) => {
    setActiveTab(tabName);
    if (pathname !== '/') {
      router.push('/');
    }
  };

  const menuItems = [
    { name: 'Overview', icon: LayoutDashboard },
    { name: 'Sensors', icon: Cpu },
  ];

  return (
    <aside className="w-48 border-r border-slate-800 bg-slate-900/40 backdrop-blur-md flex flex-col justify-between z-10 select-none">
      {/* Upper Navigation menus */}
      <nav className="flex-grow p-3 space-y-1">
        <span className="text-[9px] text-slate-600 font-mono uppercase tracking-wider block px-3.5 mb-3 select-none">
          Console Navigation
        </span>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = item.name === activeTab;
          return (
            <button
              key={item.name}
              onClick={() => handleTabClick(item.name)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg border text-xs font-mono transition-all duration-150 cursor-pointer text-left ${
                isActive && pathname === '/'
                  ? 'border-sky-950 bg-sky-950/20 text-sky-400 font-bold shadow-[inset_0_0_8px_rgba(56,189,248,0.05)]'
                  : 'border-transparent text-slate-500 hover:text-slate-350 hover:bg-slate-950/15'
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? 'text-sky-400 animate-pulse' : 'text-slate-500'}`} />
              <span className="tracking-wide uppercase text-[10px]">{item.name}</span>
            </button>
          );
        })}
        {/* Route Optimizer as a main menu button */}
        <Link
          href="/route-optimization"
          className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg border text-xs font-mono transition-all duration-150 cursor-pointer text-left ${
            pathname === '/route-optimization'
              ? 'border-sky-950 bg-sky-950/20 text-sky-400 font-bold shadow-[inset_0_0_8px_rgba(56,189,248,0.05)]'
              : 'border-transparent text-slate-500 hover:text-slate-350 hover:bg-slate-950/15'
          }`}
        >
          <Compass className={`h-4 w-4 ${pathname === '/route-optimization' ? 'text-sky-400 animate-pulse' : 'text-slate-500'}`} />
          <span className="tracking-wide uppercase text-[10px]">Route Optimizer</span>
        </Link>
      </nav>

      {/* Lower Actions */}
      <div className="p-3 border-t border-slate-800/40 space-y-2">
        <Link 
          href="/hull-crack-finder" 
          className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded border border-cyan-900 bg-cyan-950/30 text-cyan-400 hover:bg-cyan-900/50 transition-all font-bold shadow-[inset_0_0_8px_rgba(34,211,238,0.1)]"
        >
          <ScanLine className="h-4 w-4" />
          <span className="tracking-wider uppercase text-[10px]">Hull Crack AI</span>
        </Link>
      </div>

      {/* Footer console logo / collapse switch */}
      <div className="p-4 border-t border-slate-800/40 text-center font-mono text-[9px] text-slate-600">
        <span>SCADA CONSOLE v1.0.0</span>
      </div>
    </aside>
  );
}
