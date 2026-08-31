import React, { useState } from 'react';
import Navbar from './components/Navbar';
import OverviewPage from './pages/OverviewPage';
import TaxonomyPage from './pages/TaxonomyPage';
import GeneratorPage from './pages/GeneratorPage';
import DefenderPage from './pages/DefenderPage';
import StreamPage from './pages/StreamPage';
import InvestigatePage from './pages/InvestigatePage';
import { Shield } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTx, setSelectedTx] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [liveTransactions, setLiveTransactions] = useState([]);

  const handleSelectTransaction = (tx) => {
    setSelectedTx(tx);
    setActiveTab('investigate');
  };

  return (
    <div className="min-h-screen bg-[#050608] text-zinc-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isStreaming={isStreaming}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {activeTab === 'overview' && (
          <OverviewPage setActiveTab={setActiveTab} />
        )}
        {activeTab === 'taxonomy' && <TaxonomyPage />}
        {activeTab === 'generator' && <GeneratorPage />}
        {activeTab === 'defender' && <DefenderPage />}
        {activeTab === 'stream' && (
          <StreamPage
            onSelectTransaction={handleSelectTransaction}
            isStreaming={isStreaming}
            setIsStreaming={setIsStreaming}
            transactions={liveTransactions}
            setTransactions={setLiveTransactions}
          />
        )}
        {activeTab === 'investigate' && (
          <InvestigatePage
            selectedTx={selectedTx}
            setSelectedTx={setSelectedTx}
            liveTransactions={liveTransactions}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1a1f2c] bg-[#07090e] px-6 py-6 text-xs font-mono text-zinc-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-red-500" />
            <span className="text-zinc-300 font-semibold">REDTEAM-PAY</span>
            <span>·</span>
            <span>Mastercard 7-Category AI Fraud Intelligence System</span>
          </div>

          <div className="flex items-center gap-6">
            <span className="text-zinc-400">HDC 10,000-D Engine Online</span>
            <span className="text-zinc-400">Closed-Loop Generate → Detect → Investigate</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
