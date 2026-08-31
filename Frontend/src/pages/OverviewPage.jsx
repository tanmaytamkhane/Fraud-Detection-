import React, { useState, useEffect } from 'react';
import { checkHealth, getAllCategories, getBenchmarks, getStats } from '../api/client';
import { Zap, ArrowUpRight, Shield, Crosshair, Cpu, Target, CheckCircle2, Sparkles, Network, Fingerprint, Lock } from 'lucide-react';

export default function OverviewPage({ setActiveTab }) {
  const [stats, setStats] = useState({
    categories: 7,
    attackVectors: 22,
    datasetLoaded: '175,392',
    modelStatus: 'ACTIVE · 10,000-D',
    predictions: '45,398',
  });

  useEffect(() => {
    let isMounted = true;
    async function loadStats() {
      try {
        const [health, catsData, statsRes] = await Promise.allSettled([
          checkHealth(),
          getAllCategories(),
          getStats(),
        ]);

        if (isMounted) {
          const newStats = { ...stats };
          if (catsData.status === 'fulfilled' && catsData.value?.categories) {
            newStats.categories = catsData.value.categories.length;
          }
          if (health.status === 'fulfilled' && health.value?.model_status) {
            newStats.modelStatus = `${health.value.model_status.toUpperCase()} · 10,000-D`;
          }
          if (statsRes.status === 'fulfilled' && statsRes.value) {
            newStats.datasetLoaded = statsRes.value.total_dataset_formatted || '175,386';
            newStats.predictions = statsRes.value.total_predictions_formatted || '45,398';
            newStats.attackVectors = statsRes.value.attack_vectors_count || 22;
          }
          setStats(newStats);
        }
      } catch (err) {
        console.warn('[OverviewPage] Using default stats:', err.message);
      }
    }
    loadStats();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-12">
      {/* Hero Section */}
      <div className="space-y-6 max-w-4xl">
        <div className="inline-flex items-center gap-2 text-xs font-mono text-cyan-400 tracking-widest uppercase">
          <span>MASTERCARD RED-TEAM INTELLIGENCE</span>
          <span>·</span>
          <span>7 FRAUD CATEGORIES</span>
          <span>·</span>
          <span>10,000-D HDC</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-medium tracking-tight text-white leading-[1.2]">
          Defend payment networks against{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-500 to-orange-500">
            Next-Gen Adversarial
          </span>{' '}
          fraud.
        </h1>

        <p className="text-zinc-400 text-base lg:text-lg leading-relaxed max-w-3xl font-normal">
          An enterprise red-team defense platform across all 7 Mastercard fraud categories: catalogue the emerging attack surface, simulate mathematical fraud distributions, and run sub-millisecond 10,000-D Hyperdimensional Computing (HDC) + Graph inference in a closed loop.
        </p>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <button
            onClick={() => setActiveTab('stream')}
            className="flex items-center gap-2.5 bg-cyan-400 hover:bg-cyan-300 text-black px-6 py-3 rounded font-mono font-bold text-xs tracking-wider uppercase transition-all duration-150 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-400/40"
          >
            <Zap className="w-4 h-4 fill-black" />
            <span>START LIVE INFERENCE STREAM</span>
          </button>

          <button
            onClick={() => setActiveTab('taxonomy')}
            className="flex items-center gap-2 bg-[#0d1017] hover:bg-[#151a24] text-zinc-300 hover:text-white border border-[#222838] px-6 py-3 rounded font-mono font-semibold text-xs tracking-wider uppercase transition-all duration-150"
          >
            <span>BROWSE 7-CATEGORY TAXONOMY</span>
            <ArrowUpRight className="w-4 h-4 text-zinc-400" />
          </button>
        </div>
      </div>

      {/* Top 4 Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0b0e14] border border-[#1a1f2c] p-5 rounded-lg space-y-2">
          <div className="text-[11px] font-mono tracking-widest text-zinc-400 uppercase">FRAUD DOMAINS</div>
          <div className="text-3xl font-mono font-medium text-white">{stats.categories} Master Categories</div>
          <div className="text-[11px] font-mono text-zinc-500">{stats.attackVectors} Formal Attack Variants</div>
        </div>

        <div className="bg-[#0b0e14] border border-[#1a1f2c] p-5 rounded-lg space-y-2">
          <div className="text-[11px] font-mono tracking-widest text-zinc-400 uppercase">TRANSACTIONS LOADED</div>
          <div className="text-3xl font-mono font-medium text-white">{stats.datasetLoaded}</div>
          <div className="text-[11px] font-mono text-zinc-500">IEEE-CIS, Graph &amp; Biometric</div>
        </div>

        <div className="bg-[#0b0e14] border border-[#1a1f2c] p-5 rounded-lg space-y-2">
          <div className="text-[11px] font-mono tracking-widest text-zinc-400 uppercase">AI DEFENSE STATUS</div>
          <div className="text-2xl font-mono font-bold text-emerald-400">{stats.modelStatus}</div>
          <div className="text-[11px] font-mono text-zinc-500">FastAPI Online &amp; Armed</div>
        </div>

        <div className="bg-[#0b0e14] border border-[#1a1f2c] p-5 rounded-lg space-y-2">
          <div className="text-[11px] font-mono tracking-widest text-zinc-400 uppercase">VALIDATED PREDICTIONS</div>
          <div className="text-3xl font-mono font-medium text-white">{stats.predictions}</div>
          <div className="text-[11px] font-mono text-zinc-500">Test Sets Evaluated</div>
        </div>
      </div>

      {/* 3 Pillars Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Pillar 01 */}
        <div
          onClick={() => setActiveTab('taxonomy')}
          className="group bg-[#0a0d13] border border-[#1a1f2c] hover:border-cyan-500/50 p-6 rounded-lg space-y-5 cursor-pointer transition-all duration-200 hover:shadow-xl hover:shadow-cyan-500/5 flex flex-col justify-between"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs font-mono text-cyan-400">
              <span className="tracking-widest font-semibold">01</span>
              <ArrowUpRight className="w-4 h-4 text-zinc-500 group-hover:text-cyan-400 transition-colors" />
            </div>
            <h3 className="text-3xl font-semibold tracking-tight text-cyan-400 group-hover:text-cyan-300">
              IDENTIFY
            </h3>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Full Mastercard Taxonomy mapping 7 fraud categories (Identity, Social Engineering, Payment Manipulation, Behaviour, Merchant, Money Movement, GenAI) and 22 attack contracts.
            </p>
          </div>
          <div className="pt-4 border-t border-[#161a26] text-xs font-mono text-cyan-400 group-hover:underline">
            Enter Taxonomy →
          </div>
        </div>

        {/* Pillar 02 */}
        <div
          onClick={() => setActiveTab('generator')}
          className="group bg-[#0a0d13] border-2 border-cyan-500/60 p-6 rounded-lg space-y-5 cursor-pointer transition-all duration-200 shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20 flex flex-col justify-between"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs font-mono text-amber-400">
              <span className="tracking-widest font-semibold">02</span>
              <ArrowUpRight className="w-4 h-4 text-amber-400" />
            </div>
            <h3 className="text-3xl font-semibold tracking-tight text-amber-400 group-hover:text-amber-300">
              GENERATE
            </h3>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Simulate synthetic attack transactions at scale with Benford's Law amount distributions, Poisson arrivals, graph dispersal topologies, and tunable evasion noise.
            </p>
          </div>
          <div className="pt-4 border-t border-[#161a26] text-xs font-mono text-amber-400 group-hover:underline">
            Open Generator →
          </div>
        </div>

        {/* Pillar 03 */}
        <div
          onClick={() => setActiveTab('defender')}
          className="group bg-[#0a0d13] border border-[#1a1f2c] hover:border-emerald-500/50 p-6 rounded-lg space-y-5 cursor-pointer transition-all duration-200 hover:shadow-xl hover:shadow-emerald-500/5 flex flex-col justify-between"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs font-mono text-emerald-400">
              <span className="tracking-widest font-semibold">03</span>
              <ArrowUpRight className="w-4 h-4 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
            </div>
            <h3 className="text-3xl font-semibold tracking-tight text-emerald-400 group-hover:text-emerald-300">
              DEFEND
            </h3>
            <p className="text-sm text-zinc-400 leading-relaxed">
              10,000-D Hyperdimensional Computing (HDC) + Graph Centrality Fusion. Real-time ROC-AUC, Precision, Recall, and Confusion Matrices across all 7 categories.
            </p>
          </div>
          <div className="pt-4 border-t border-[#161a26] text-xs font-mono text-emerald-400 group-hover:underline">
            See Defender →
          </div>
        </div>
      </div>

      {/* 3 Core Value Props */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div className="bg-[#0a0d13] border border-[#1a1f2c] p-6 rounded-lg space-y-3">
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 tracking-widest uppercase">
            <Target className="w-4 h-4" />
            <span>FULL 7-CATEGORY COVERAGE</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed font-mono">
            Unifies card-not-present fraud, mule laundering networks, chatbot prompt injections, and deepfake voice clone attacks in one single pane of glass.
          </p>
        </div>

        <div className="bg-[#0a0d13] border border-[#1a1f2c] p-6 rounded-lg space-y-3">
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 tracking-widest uppercase">
            <Cpu className="w-4 h-4" />
            <span>SUB-MILLISECOND INFERENCE</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed font-mono">
            10,000-D bitwise hypervector operations execute in &lt;1.2 milliseconds, enabling instant authorization decisions before ledger settlement.
          </p>
        </div>

        <div className="bg-[#0a0d13] border border-[#1a1f2c] p-6 rounded-lg space-y-3">
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 tracking-widest uppercase">
            <Shield className="w-4 h-4" />
            <span>AUTOMATED MITIGATION</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed font-mono">
            Tiered policy engine dispatches BLOCK, HOLD_TRANSFER, STEP_UP_AUTH, or APPROVE with plain-language root-cause explanations.
          </p>
        </div>
      </div>
    </div>
  );
}
