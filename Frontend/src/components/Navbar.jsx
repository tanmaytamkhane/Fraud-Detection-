import React, { useState, useEffect } from 'react';
import { Shield, Activity, Zap, Crosshair, Search, Layers, Radio } from 'lucide-react';
import { checkHealth } from '../api/client';

export default function Navbar({ activeTab, setActiveTab, isStreaming }) {
  const [backendStatus, setBackendStatus] = useState({ online: false, checking: true });

  useEffect(() => {
    let isMounted = true;
    async function pingBackend() {
      try {
        const res = await checkHealth();
        if (isMounted && res && res.status === 'online') {
          setBackendStatus({ online: true, checking: false, service: res.service, dim: res.hdc_dimensions });
        }
      } catch {
        if (isMounted) setBackendStatus({ online: false, checking: false });
      }
    }
    pingBackend();
    const interval = setInterval(pingBackend, 4000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: 'overview', label: 'OVERVIEW', icon: Layers },
    { id: 'taxonomy', label: '01 IDENTIFY', icon: Crosshair },
    { id: 'generator', label: '02 GENERATE', icon: Zap },
    { id: 'defender', label: '03 DEFEND', icon: Shield },
    { id: 'stream', label: 'LIVE STREAM', icon: Activity, badge: isStreaming ? 'LIVE' : null },
    { id: 'investigate', label: 'INVESTIGATE', icon: Search },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#07090e]/95 backdrop-blur-md border-b border-[#1a1f2c] px-6 py-3.5 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
        <div className="w-8 h-8 rounded bg-gradient-to-tr from-red-600 via-orange-500 to-amber-400 p-[1px] flex items-center justify-center shadow-lg shadow-red-500/20">
          <div className="w-full h-full bg-[#090b10] rounded flex items-center justify-center">
            <Shield className="w-4 h-4 text-red-500 fill-red-500/20" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold tracking-wider text-lg tracking-wider text-white">REDTEAM<span className="text-red-500">-PAY</span></span>
            <span className="text-[10px] font-mono uppercase bg-red-500/10 text-red-400 border border-red-500/20 px-1.5 py-0.5 rounded tracking-widest font-semibold">MASTERCARD 7-CATEGORY AI</span>
          </div>
        </div>
      </div>

      {/* Nav Tabs */}
      <nav className="flex items-center gap-1 bg-[#0b0e14] p-1 rounded-lg border border-[#1a1f2c]">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded text-xs font-mono tracking-wider transition-all duration-150 relative ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold shadow-sm shadow-cyan-500/20'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-[#121622] border border-transparent'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-zinc-500'}`} />
              <span>{item.label}</span>
              {item.badge && (
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status Pill */}
      <div className="flex items-center gap-3">
        <div className="hidden lg:flex items-center gap-2 text-xs font-mono bg-[#0c1017] border border-[#1e2536] px-3.5 py-1.5 rounded-full text-zinc-300">
          <span className={`w-2 h-2 rounded-full ${backendStatus.online ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
          <span className="text-zinc-400">FASTAPI BACKEND:</span>
          <span className={`font-semibold ${backendStatus.online ? 'text-emerald-400' : 'text-amber-400'}`}>
            {backendStatus.online ? 'ONLINE · HDC 10,000-D' : 'CONNECTING...'}
          </span>
        </div>
      </div>
    </header>
  );
}
