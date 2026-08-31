import React, { useState, useEffect } from 'react';
import { getAttacks } from '../api/client';
import { AlertTriangle, ChevronRight, Layers, ShieldCheck, Sparkles, Crosshair, RefreshCw } from 'lucide-react';

export default function TaxonomyPage() {
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [activeVectorId, setActiveVectorId] = useState(null);
  const [attackVectors, setAttackVectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadAttacks() {
      try {
        setLoading(true);
        setError(null);
        const data = await getAttacks();
        if (data && data.attacks) {
          const list = [];
          data.attacks.forEach((att) => {
            const catPrefix = att.attack_id || att.id;
            const categoryName = att.category || att.name;
            const colorMap = {
              'ATO-001': '#ff334b', 'SOC-001': '#f59e0b', 'PM-001': '#00e5ff',
              'TB-001': '#b388ff', 'MRF-001': '#ff007f', 'MM-001': '#00e676', 'GENAI-001': '#7928ca'
            };
            const catColor = colorMap[catPrefix] || '#00e5ff';
            
            (att.variants || []).forEach((v) => {
              list.push({
                id: v.variant_id || v.id,
                name: v.name || att.name,
                category: categoryName,
                catId: catPrefix,
                severity: v.severity || (v.risk_score > 0.85 ? 'CRITICAL' : 'HIGH'),
                color: catColor,
                channels: att.channels || ['e-commerce', 'mobile banking', 'API gateway'],
                rails: att.rails || ['credit card', 'debit card', 'account transfer'],
                signals: att.signals ? att.signals.length : 6,
                description: v.description || att.attack_objective || '',
                novelty: att.genai_enhancement || att.observable_behaviour || 'Adversarial evasion bypass.',
                realWorldRef: `Mastercard ${catPrefix} Contract`,
                defensiveSignatures: (att.signals || []).map((s) => typeof s === 'string' ? s : `${s.name}: ${s.description || s.weight || 0.85}`)
              });
            });
          });
          setAttackVectors(list);
          if (list.length > 0) setActiveVectorId(list[0].id);
        }
      } catch (err) {
        console.error('[TaxonomyPage] Failed to load live attack catalog:', err);
        setError(`Failed to fetch live attack catalog from API: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }
    loadAttacks();
  }, []);

  const masterCategories = [
    { id: 'ALL', label: `ALL CATEGORIES (${attackVectors.length} VECTORS)` },
    { id: 'ATO-001', label: '1. IDENTITY & ACCOUNT' },
    { id: 'SOC-001', label: '2. SOCIAL ENGINEERING' },
    { id: 'PM-001', label: '3. PAYMENT MANIPULATION' },
    { id: 'TB-001', label: '4. TRANSACTION BEHAVIOUR' },
    { id: 'MRF-001', label: '5. MERCHANT & REFUND' },
    { id: 'MM-001', label: '6. MONEY MOVEMENT' },
    { id: 'GENAI-001', label: '7. GENAI-NATIVE' },
  ];

  const filteredVectors = selectedCategory === 'ALL'
    ? attackVectors
    : attackVectors.filter((v) => v.catId === selectedCategory);

  const activeVector = attackVectors.find((v) => v.id === activeVectorId) || attackVectors[0] || null;

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-4 max-w-4xl">
        <div className="inline-flex items-center gap-2 text-xs font-mono text-cyan-400 tracking-widest uppercase">
          <span>IDENTIFY PILLAR</span>
          <span>·</span>
          <span>7 CATEGORIES</span>
          <span>·</span>
          <span>{attackVectors.length} LIVE VECTORS</span>
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-white">
          Mastercard 7-Category Threat Taxonomy
        </h1>

        <p className="text-zinc-400 text-sm lg:text-base leading-relaxed max-w-3xl">
          Comprehensive threat intelligence encyclopedia defining operational vectors, mathematical signals, and automated defense signatures across all Mastercard fraud contracts.
        </p>
      </div>

      {/* Error / Loading */}
      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-lg flex items-center gap-3 text-destructive text-sm font-mono">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading && attackVectors.length === 0 && (
        <div className="p-12 text-center text-muted-foreground font-mono text-sm animate-pulse">
          Loading live 7-category taxonomy catalog from /attacks API...
        </div>
      )}

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2 pt-2 border-b border-[#1a1f2c] pb-4">
        {masterCategories.map((c) => {
          const isSelected = selectedCategory === c.id;
          return (
            <button
              key={c.id}
              onClick={() => setSelectedCategory(c.id)}
              className={`px-3 py-1.5 rounded text-xs font-mono tracking-wider transition-all duration-150 ${
                isSelected
                  ? 'bg-cyan-500 text-black font-bold shadow-md shadow-cyan-500/20'
                  : 'bg-[#0d1017] text-zinc-400 hover:text-zinc-200 border border-[#1a1f2c]'
              }`}
            >
              {c.label}
            </button>
          );
        })}
      </div>

      {/* Master 2-Column Layout */}
      {attackVectors.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: List of Vectors */}
          <div className="lg:col-span-5 space-y-2.5 max-h-[750px] overflow-y-auto pr-2">
            {filteredVectors.map((v) => {
              const isSelected = activeVectorId === v.id;
              return (
                <div
                  key={v.id}
                  onClick={() => setActiveVectorId(v.id)}
                  className={`p-4 rounded-lg border transition-all duration-150 cursor-pointer ${
                    isSelected
                      ? 'bg-[#111622] border-cyan-500/80 shadow-lg shadow-cyan-500/10'
                      : 'bg-[#0b0e14] border-[#1a1f2c] hover:border-[#2a324b]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold" style={{ color: v.color }}>
                        {v.id}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">
                        {v.catId}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                        v.severity === 'CRITICAL'
                          ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                          : v.severity === 'HIGH'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                      }`}
                    >
                      {v.severity}
                    </span>
                  </div>

                  <div className="text-sm font-semibold text-zinc-100 mb-1">{v.name}</div>
                  <div className="text-xs text-zinc-400 line-clamp-2">{v.description}</div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Detailed Vector Dossier */}
          {activeVector && (
            <div className="lg:col-span-7 bg-[#0b0e14] border border-[#1a1f2c] rounded-xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-[#1a1f2c] pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono font-bold" style={{ color: activeVector.color }}>
                      {activeVector.id}
                    </span>
                    <span className="text-xs font-mono text-zinc-400">· {activeVector.category}</span>
                  </div>
                  <h2 className="text-2xl font-semibold text-white">{activeVector.name}</h2>
                </div>
                <span
                  className={`text-xs font-mono px-2.5 py-1 rounded font-bold ${
                    activeVector.severity === 'CRITICAL'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {activeVector.severity}
                </span>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <div className="text-xs font-mono text-zinc-400 uppercase tracking-wider">THREAT VECTOR OVERVIEW</div>
                <p className="text-sm text-zinc-200 leading-relaxed bg-[#0e121a] p-4 rounded-lg border border-[#1f2536]">
                  {activeVector.description}
                </p>
              </div>

              {/* Novelty & Evasion Signature */}
              <div className="space-y-2">
                <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Adversarial Novelty & Evasion Strategy</span>
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed bg-cyan-950/20 p-3.5 rounded-lg border border-cyan-500/20">
                  {activeVector.novelty}
                </p>
              </div>

              {/* Channels & Payment Rails */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="text-xs font-mono text-zinc-400 uppercase">Target Channels</div>
                  <div className="flex flex-wrap gap-1.5">
                    {activeVector.channels.map((ch, idx) => (
                      <span key={idx} className="text-xs font-mono px-2 py-1 rounded bg-[#131824] border border-[#222a3d] text-zinc-300">
                        {ch}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs font-mono text-zinc-400 uppercase">Affected Payment Rails</div>
                  <div className="flex flex-wrap gap-1.5">
                    {activeVector.rails.map((rail, idx) => (
                      <span key={idx} className="text-xs font-mono px-2 py-1 rounded bg-[#131824] border border-[#222a3d] text-zinc-300">
                        {rail}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Defensive Signatures */}
              <div className="space-y-2 pt-2 border-t border-[#1a1f2c]">
                <div className="text-xs font-mono text-emerald-400 uppercase flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>10,000-D Mathematical Detection Signatures</span>
                </div>
                <div className="space-y-1.5">
                  {activeVector.defensiveSignatures.map((sig, idx) => (
                    <div key={idx} className="text-xs font-mono p-2 rounded bg-[#0e121a] border border-[#1a1f2c] text-zinc-300">
                      • {sig}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
