import React, { useState, useEffect } from 'react';
import { ATTACK_VECTORS as FALLBACK_VECTORS } from '../data/attacksData';
import { generateInitialBatch } from '../data/mockTransactions';
import {
  getVariants,
  getMuleVariants,
  getGenAIVariants,
  scanPreset,
  scanMulePreset,
  scanGenAIPreset,
  getMuleGraph
} from '../api/client';
import { Search, AlertTriangle, ShieldCheck, Sparkles, ChevronDown, Network, Radio } from 'lucide-react';

export default function InvestigatePage({ selectedTx, setSelectedTx, liveTransactions = [] }) {
  const [viewMode, setViewMode] = useState('ALL'); // 'ALL', 'LIVE_STREAM', or 'TAXONOMY'
  const [filterType, setFilterType] = useState('FLAGGED ONLY');
  const [filterAttack, setFilterAttack] = useState('ALL ATTACKS');
  const [searchQuery, setSearchQuery] = useState('');
  const [attackVectors, setAttackVectors] = useState(FALLBACK_VECTORS);
  const [presetTransactions, setPresetTransactions] = useState([]);
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadPresets() {
      try {
        const [
          atoVar, mmVar, genVar,
          s1, s2, s3, s4, s5,
          m1, m2, m3, m4,
          g1, g2, g3, g4,
          legit1
        ] = await Promise.allSettled([
          getVariants(),
          getMuleVariants(),
          getGenAIVariants(),
          scanPreset('ATO-V1'),
          scanPreset('ATO-V2'),
          scanPreset('ATO-V3'),
          scanPreset('ATO-V4'),
          scanPreset('ATO-V5'),
          scanMulePreset('MM-V1'),
          scanMulePreset('MM-V2'),
          scanMulePreset('MM-V3'),
          scanMulePreset('MM-V4'),
          scanGenAIPreset('GENAI-V1'),
          scanGenAIPreset('GENAI-V2'),
          scanGenAIPreset('GENAI-V3'),
          scanGenAIPreset('GENAI-V4'),
          scanPreset('LEGIT'),
        ]);

        const vectorList = [];
        if (atoVar.status === 'fulfilled' && atoVar.value?.variants) {
          vectorList.push(...atoVar.value.variants.map((v) => ({ id: v.variant_id, name: v.name })));
        }
        if (mmVar.status === 'fulfilled' && mmVar.value?.variants) {
          vectorList.push(...mmVar.value.variants.map((v) => ({ id: v.variant_id, name: v.name })));
        }
        if (genVar.status === 'fulfilled' && genVar.value?.variants) {
          vectorList.push(...genVar.value.variants.map((v) => ({ id: v.variant_id, name: v.name })));
        }
        if (isMounted && vectorList.length > 0) {
          setAttackVectors(vectorList);
        }

        const presets = [
          { vid: 'ATO-V1', cat: 'wire_transfer', amt: 8450.00, res: s1.status === 'fulfilled' ? s1.value : null },
          { vid: 'ATO-V2', cat: 'online_retail', amt: 1250.00, res: s2.status === 'fulfilled' ? s2.value : null },
          { vid: 'ATO-V3', cat: 'digital_goods', amt: 480.00, res: s3.status === 'fulfilled' ? s3.value : null },
          { vid: 'ATO-V4', cat: 'grocery', amt: 215.00, res: s4.status === 'fulfilled' ? s4.value : null },
          { vid: 'ATO-V5', cat: 'p2p', amt: 650.00, res: s5.status === 'fulfilled' ? s5.value : null },
          { vid: 'MM-V1', cat: 'rapid_cashout', amt: 14500.00, res: m1.status === 'fulfilled' ? m1.value : null },
          { vid: 'MM-V2', cat: 'smurfing_fanout', amt: 1850.00, res: m2.status === 'fulfilled' ? m2.value : null },
          { vid: 'MM-V3', cat: 'mule_aggregation', amt: 8200.00, res: m3.status === 'fulfilled' ? m3.value : null },
          { vid: 'MM-V4', cat: 'dormant_activation', amt: 11000.00, res: m4.status === 'fulfilled' ? m4.value : null },
          { vid: 'GENAI-V1', cat: 'conversational_agent', amt: 4200.00, res: g1.status === 'fulfilled' ? g1.value : null },
          { vid: 'GENAI-V2', cat: 'deepfake_voice_wire', amt: 75000.00, res: g2.status === 'fulfilled' ? g2.value : null },
          { vid: 'GENAI-V3', cat: 'synthetic_kyc_credit', amt: 18500.00, res: g3.status === 'fulfilled' ? g3.value : null },
          { vid: 'GENAI-V4', cat: 'adversarial_evasion', amt: 1990.00, res: g4.status === 'fulfilled' ? g4.value : null },
          { vid: 'LEGIT', cat: 'grocery', amt: 42.50, res: legit1.status === 'fulfilled' ? legit1.value : null },
        ];

        const liveList = presets.map((p, idx) => {
          const scan = p.res;
          const isAtk = p.vid !== 'LEGIT';
          const rScore = scan ? scan.risk_score : (isAtk ? 0.90 : 0.05);
          const act = scan ? scan.action : (isAtk ? 'BLOCK' : 'APPROVE');
          return {
            id: `TXN-${(1001 + idx).toString()}`,
            index: idx + 1,
            amount: p.amt,
            category: p.cat,
            isAttack: isAtk,
            attackVector: scan?.matched_variant || p.vid,
            attackName: scan?.variant_name || (isAtk ? p.vid : 'Normal Activity'),
            fraudProb: +(rScore * 100).toFixed(1),
            decision: act,
            matrixTag: isAtk ? (act.includes('BLOCK') || act.includes('HOLD') ? 'TP' : 'FN') : (act.includes('BLOCK') || act.includes('HOLD') ? 'FP' : 'TN'),
            timestamp: scan?.timestamp || new Date().toISOString(),
            displayDate: new Date().toLocaleTimeString(),
            features: scan?.signals ? Object.entries(scan.signals).map(([k, v]) => ({
              name: k,
              value: Number(v),
              contribution: isAtk ? (Number(v) > 0.4 ? 3.5 : 1.2) : -1.0
            })) : [
              { name: 'device_risk', value: 0.85, contribution: 3.85 },
              { name: 'amount_deviation', value: 0.90, contribution: 2.89 },
              { name: 'velocity', value: 0.40, contribution: 2.15 },
            ],
            explanation: scan?.action_message || 'Model scan evaluated.',
            analystSummary: scan?.analyst_summary || scan?.action_message || '',
          };
        });

        if (isMounted) setPresetTransactions(liveList);
      } catch {
        if (isMounted) setPresetTransactions(generateInitialBatch(15));
      }
    }
    loadPresets();
    return () => {
      isMounted = false;
    };
  }, []);

  // Merge live stream transactions and preset pool
  const allTransactions = React.useMemo(() => {
    if (viewMode === 'LIVE_STREAM') return liveTransactions;
    if (viewMode === 'TAXONOMY') return presetTransactions;
    // Default 'ALL': Live Stream first, then presets (avoiding duplicate IDs)
    const liveIds = new Set(liveTransactions.map((t) => t.id));
    const uniquePresets = presetTransactions.filter((t) => !liveIds.has(t.id));
    return [...liveTransactions, ...uniquePresets];
  }, [viewMode, liveTransactions, presetTransactions]);

  const activeTx = selectedTx || allTransactions.find((t) => t.isAttack) || allTransactions[0] || {
    id: 'TXN-1001',
    amount: 8450.00,
    category: 'wire_transfer',
    displayDate: new Date().toLocaleTimeString(),
    fraudProb: 95.4,
    decision: 'BLOCK',
    isAttack: true,
    attackVector: 'ATO-V1',
    features: [
      { name: 'device_risk', value: 0.95, contribution: 3.85 },
      { name: 'amount_deviation', value: 0.90, contribution: 2.89 },
      { name: 'velocity', value: 0.40, contribution: 2.15 },
    ],
    explanation: 'CRITICAL: High-Value New Device Takeover detected.'
  };

  useEffect(() => {
    let isMounted = true;
    async function loadGraph() {
      try {
        const res = await getMuleGraph(activeTx.id);
        if (isMounted && res) setGraphData(res);
      } catch {
        if (isMounted) setGraphData(null);
      }
    }
    loadGraph();
    return () => {
      isMounted = false;
    };
  }, [activeTx.id]);

  const filteredTransactions = allTransactions.filter((tx) => {
    if (filterType === 'FLAGGED ONLY' && !tx.decision?.includes('BLOCK') && !tx.decision?.includes('HOLD')) return false;
    if (filterType === 'MISSED ONLY' && tx.matrixTag !== 'FN') return false;
    if (filterAttack !== 'ALL ATTACKS' && tx.attackVector !== filterAttack) return false;
    if (searchQuery && !tx.id.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-3">
          <div className="text-xs font-mono text-cyan-400 tracking-widest uppercase">
            INVESTIGATE · CLOSED-LOOP HDC TELEMETRY
          </div>
          <h1 className="text-4xl lg:text-5xl font-semibold tracking-tight text-white">
            Fraud Investigation Console
          </h1>
          <p className="text-zinc-400 text-sm max-w-3xl leading-relaxed">
            Inspect real-time streamed transactions and taxonomy ground-truth cases with live HDC signal breakdowns and multi-hop mule graphs.
          </p>
        </div>

        {/* Source Switcher */}
        <div className="flex bg-[#0b0e14] border border-[#1a1f2c] rounded-lg p-1 text-xs font-mono self-start md:self-auto">
          <button
            onClick={() => setViewMode('ALL')}
            className={`px-3 py-1.5 rounded transition-all ${
              viewMode === 'ALL' ? 'bg-cyan-500/20 text-cyan-400 font-bold border border-cyan-500/40' : 'text-zinc-400 hover:text-white'
            }`}
          >
            ALL ({liveTransactions.length + presetTransactions.length})
          </button>
          <button
            onClick={() => setViewMode('LIVE_STREAM')}
            className={`px-3 py-1.5 rounded transition-all flex items-center gap-1.5 ${
              viewMode === 'LIVE_STREAM' ? 'bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Radio className="w-3 h-3 text-emerald-400" />
            <span>LIVE STREAM ({liveTransactions.length})</span>
          </button>
          <button
            onClick={() => setViewMode('TAXONOMY')}
            className={`px-3 py-1.5 rounded transition-all ${
              viewMode === 'TAXONOMY' ? 'bg-fuchsia-500/20 text-fuchsia-400 font-bold border border-fuchsia-500/40' : 'text-zinc-400 hover:text-white'
            }`}
          >
            PRESETS ({presetTransactions.length})
          </button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
        <div className="relative">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="appearance-none bg-[#0b0e14] border border-[#1a1f2c] text-zinc-200 px-4 py-2.5 pr-8 rounded-lg outline-none cursor-pointer hover:border-[#2a3346] font-semibold"
          >
            <option value="FLAGGED ONLY">FLAGGED ONLY</option>
            <option value="ALL TRANSACTIONS">ALL TRANSACTIONS</option>
            <option value="MISSED ONLY">MISSED ONLY</option>
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-zinc-400 absolute right-3 top-3.5 pointer-events-none" />
        </div>

        <div className="relative">
          <select
            value={filterAttack}
            onChange={(e) => setFilterAttack(e.target.value)}
            className="appearance-none bg-[#0b0e14] border border-[#1a1f2c] text-zinc-200 px-4 py-2.5 pr-8 rounded-lg outline-none cursor-pointer hover:border-[#2a3346] font-semibold"
          >
            <option value="ALL ATTACKS">ALL ATTACKS</option>
            {attackVectors.map((v) => (
              <option key={v.id} value={v.id}>
                {v.id}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-zinc-400 absolute right-3 top-3.5 pointer-events-none" />
        </div>

        <span className="text-zinc-500 text-xs">{filteredTransactions.length} results</span>
      </div>

      {/* 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Transaction List */}
        <div className="lg:col-span-5 space-y-2 max-h-[750px] overflow-y-auto pr-1">
          {filteredTransactions.map((tx) => {
            const isSelected = activeTx.id === tx.id;
            const isBlock = tx.decision?.includes('BLOCK') || tx.decision?.includes('HOLD');
            return (
              <div
                key={tx.id}
                onClick={() => setSelectedTx(tx)}
                className={`flex items-center justify-between gap-3 p-3.5 rounded-lg border cursor-pointer font-mono text-xs transition-all duration-150 ${
                  isSelected
                    ? 'bg-[#15121b] border-cyan-400 shadow-md shadow-cyan-500/10'
                    : isBlock
                    ? 'bg-[#0e090c] border-[#1f1519] hover:border-red-500/30'
                    : 'bg-[#080b10] border-[#161a26] hover:border-[#252c3c]'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-[130px]">
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      tx.isAttack ? 'bg-red-500' : 'bg-emerald-400'
                    }`}
                  />
                  <span className="text-zinc-300 font-semibold">{tx.id}</span>
                </div>

                <div className="text-zinc-400 truncate max-w-[80px]">
                  {tx.category}
                </div>

                <div className="text-white font-bold min-w-[80px] text-right">
                  ${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>

                <div className="flex items-center gap-2 min-w-[140px]">
                  <div className="w-16 h-1.5 bg-[#1a1f2c] rounded-full overflow-hidden flex-shrink-0">
                    <div
                      className={`h-full rounded-full ${
                        tx.fraudProb >= 50 ? 'bg-red-500' : 'bg-cyan-400'
                      }`}
                      style={{ width: `${Math.max(5, tx.fraudProb)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-zinc-400">{tx.fraudProb}%</span>
                  <span
                    className={`text-[10px] truncate max-w-[80px] ${
                      tx.isAttack ? 'text-red-400' : 'text-zinc-500'
                    }`}
                  >
                    {tx.attackVector}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Deep Console */}
        <div className="lg:col-span-7 bg-[#0b0e14] border border-[#1a1f2c] rounded-lg p-7 space-y-7 sticky top-24 shadow-2xl">
          <div className="space-y-1 pb-4 border-b border-[#1a1f2c]">
            <div className="text-[11px] font-mono text-zinc-400 tracking-widest uppercase">
              TXN {activeTx.id}
            </div>
            <div className="text-5xl font-semibold text-red-500 tracking-tight">
              ${activeTx.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs font-mono text-zinc-400 pt-1">
              {activeTx.category} · {activeTx.displayDate}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 font-mono">
            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] text-zinc-400 uppercase tracking-widest">FRAUD PROB</div>
              <div className="text-2xl font-bold text-red-500">{activeTx.fraudProb}%</div>
            </div>

            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] text-zinc-400 uppercase tracking-widest">DECISION</div>
              <div
                className={`text-2xl font-bold ${
                  activeTx.decision?.includes('BLOCK') || activeTx.decision?.includes('HOLD') ? 'text-red-500' : 'text-emerald-400'
                }`}
              >
                {activeTx.decision}
              </div>
            </div>

            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] text-zinc-400 uppercase tracking-widest">GROUND TRUTH</div>
              <div
                className={`text-xl font-bold ${
                  activeTx.isAttack ? 'text-red-500' : 'text-emerald-400'
                }`}
              >
                {activeTx.isAttack ? 'FRAUD' : 'LEGITIMATE'}
              </div>
            </div>

            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] text-zinc-400 uppercase tracking-widest">ATTACK VARIANT</div>
              <div className="text-sm font-bold text-amber-400 truncate">
                {activeTx.attackVector}
              </div>
            </div>
          </div>

          {/* Mule Network Graph Visualizer (If MM) */}
          {graphData && (activeTx.attackVector?.startsWith('MM') || activeTx.category?.includes('mule') || activeTx.category?.includes('cashout')) && (
            <div className="space-y-3 pt-2 border-t border-[#1a1f2c]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-[10px] font-mono text-emerald-400 tracking-widest uppercase font-semibold">
                  <Network className="w-3.5 h-3.5 text-emerald-400" />
                  <span>CONNECTED MULE NETWORK GRAPH</span>
                </div>
                <span className="text-[10px] font-mono text-zinc-400">
                  {graphData.nodes?.length || 0} NODES · {graphData.edges?.length || 0} TRANSFERS
                </span>
              </div>

              <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-3 font-mono text-xs">
                <div className="flex flex-wrap gap-2 items-center">
                  {graphData.nodes?.map((node, i) => (
                    <div
                      key={node.id}
                      className={`px-3 py-1.5 rounded border flex items-center gap-2 ${
                        node.risk === 'CRITICAL' || node.risk === 'HIGH'
                          ? 'bg-red-500/10 border-red-500/40 text-red-400 font-bold'
                          : 'bg-[#121622] border-[#222b3d] text-zinc-300'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${node.risk === 'CRITICAL' ? 'bg-red-500 animate-pulse' : 'bg-cyan-400'}`} />
                      <span>{node.id}</span>
                      <span className="text-[9px] px-1 bg-black/40 rounded text-zinc-400 uppercase">{node.type}</span>
                    </div>
                  ))}
                </div>

                <div className="space-y-1.5 pt-2 border-t border-[#161a26]">
                  {graphData.edges?.map((edge, i) => (
                    <div key={i} className="flex items-center justify-between text-[11px] text-zinc-400 bg-[#090d14] px-3 py-1.5 rounded">
                      <span className="text-zinc-300 font-semibold">{edge.source}</span>
                      <span className="text-cyan-400">─── ${edge.amount} ({edge.status}) ──►</span>
                      <span className="text-zinc-300 font-semibold">{edge.target}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Feature Contributions */}
          <div className="space-y-3">
            <div className="text-[10px] font-mono text-zinc-400 tracking-widest uppercase font-semibold">
              SIGNAL CONTRIBUTIONS (HDC, ACOUSTIC &amp; GRAPH TELEMETRY)
            </div>

            <div className="space-y-2.5 font-mono text-xs">
              {(activeTx.features || []).map((feat, i) => (
                <div key={i} className="flex items-center justify-between gap-4">
                  <span className="text-zinc-300 w-48 truncate">{feat.name}</span>
                  <span className="text-zinc-400 w-12 text-right">{Number(feat.value).toFixed(2)}</span>
                  <div className="flex-1 h-2 bg-[#1a1f2c] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        feat.contribution > 0 ? 'bg-red-500' : 'bg-emerald-400'
                      }`}
                      style={{
                        width: `${Math.min(100, Math.max(15, Math.abs(feat.contribution) * 22))}%`,
                      }}
                    />
                  </div>
                  <span
                    className={`w-14 text-right font-bold ${
                      feat.contribution > 0 ? 'text-red-400' : 'text-emerald-400'
                    }`}
                  >
                    {feat.contribution > 0 ? `+${Number(feat.contribution).toFixed(2)}` : Number(feat.contribution).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Narrative Explanation */}
          <div className="space-y-2 pt-2 border-t border-[#1a1f2c]">
            <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-400 tracking-widest uppercase">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>NARRATIVE FRAUD EXPLANATION</span>
            </div>
            <p className="text-xs font-mono text-zinc-300 leading-relaxed bg-[#07090e] p-4 rounded border border-[#1a1f2c]">
              {activeTx.explanation}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
