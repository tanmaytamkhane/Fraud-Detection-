import React, { useState, useEffect } from 'react';
import { ATTACK_VECTORS as FALLBACK_VECTORS } from '../data/attacksData';
import { getAllCategories, scanCategoryPreset } from '../api/client';
import { Zap, CheckSquare, Square, CheckCircle2, Sliders, BarChart2, Shield, Eye, Info, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function getCategoryCode(variantId) {
  if (variantId.startsWith('ATO')) return 'ATO';
  if (variantId.startsWith('SOC')) return 'SOC';
  if (variantId.startsWith('PM')) return 'PM';
  if (variantId.startsWith('TB')) return 'TB';
  if (variantId.startsWith('MRF')) return 'MRF';
  if (variantId.startsWith('MM')) return 'MM';
  if (variantId.startsWith('GENAI')) return 'GENAI';
  return 'ATO';
}

const COLOR_MAP = {
  'ATO-V1': '#ff334b', 'ATO-V2': '#f59e0b', 'ATO-V3': '#00e5ff', 'ATO-V4': '#b388ff', 'ATO-V5': '#00e676',
  'SOC-V1': '#ff5252', 'SOC-V2': '#ff7043', 'SOC-V3': '#ffa726',
  'PM-V1': '#26c6da', 'PM-V2': '#29b6f6',
  'TB-V1': '#ab47bc', 'TB-V2': '#7e57c2',
  'MRF-V1': '#ec407a', 'MRF-V2': '#f06292',
  'MM-V1': '#ff1744', 'MM-V2': '#ff9100', 'MM-V3': '#00e5ff', 'MM-V4': '#d500f9',
  'GENAI-V1': '#ff007f', 'GENAI-V2': '#7928ca', 'GENAI-V3': '#0070f3', 'GENAI-V4': '#50e3c2',
};

export default function GeneratorPage() {
  const [transactionCount, setTransactionCount] = useState(10000);
  const [fraudRatio, setFraudRatio] = useState(8.0);
  const [evasionLevel, setEvasionLevel] = useState(30);
  const [attackVectors, setAttackVectors] = useState(FALLBACK_VECTORS);
  const [selectedVectors, setSelectedVectors] = useState(FALLBACK_VECTORS.map((v) => v.id));
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('ALL');
  const [hasGenerated, setHasGenerated] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showToast, setShowToast] = useState(true);
  const [samplePayloads, setSamplePayloads] = useState([]);

  useEffect(() => {
    let isMounted = true;
    async function fetchCategoriesAndVariants() {
      try {
        const catRes = await getAllCategories();
        if (catRes && catRes.categories) {
          const list = [];
          catRes.categories.forEach((cat) => {
            const catPrefix = cat.id.replace('CAT-', '');
            const code = cat.code || (cat.id === 'CAT-001' ? 'ATO' : cat.id === 'CAT-006' ? 'MM' : cat.id === 'CAT-007' ? 'GENAI' : catPrefix);
            (cat.variants || []).forEach((v) => {
              list.push({
                id: v.variant_id,
                name: v.name,
                domain: code,
                category_name: cat.name,
                color: COLOR_MAP[v.variant_id] || '#00e5ff',
                risk_score: v.risk_score || 0.85,
              });
            });
          });
          if (isMounted && list.length > 0) {
            setAttackVectors(list);
            setSelectedVectors(list.map((v) => v.id));
          }
        }
      } catch (err) {
        console.warn('[GeneratorPage] Using fallback attack vectors:', err.message);
        if (isMounted) {
          setAttackVectors(FALLBACK_VECTORS);
          setSelectedVectors(FALLBACK_VECTORS.map((v) => v.id));
        }
      }
    }
    fetchCategoriesAndVariants();
    return () => {
      isMounted = false;
    };
  }, []);

  const fraudCount = Math.round((transactionCount * fraudRatio) / 100);

  const toggleVector = (id) => {
    if (selectedVectors.includes(id)) {
      if (selectedVectors.length > 1) {
        setSelectedVectors(selectedVectors.filter((v) => v !== id));
      }
    } else {
      setSelectedVectors([...selectedVectors, id]);
    }
  };

  const handleSelectAll = () => {
    setSelectedVectors(attackVectors.map((v) => v.id));
  };

  const handleDeselectAll = () => {
    if (attackVectors.length > 0) {
      setSelectedVectors([attackVectors[0].id]);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setShowToast(false);
    try {
      const sampleList = [];
      const testSubset = selectedVectors.slice(0, 6);
      for (const vid of testSubset) {
        const catCode = getCategoryCode(vid);
        try {
          const res = await scanCategoryPreset(catCode, vid);
          if (res) {
            sampleList.push({
              id: `GEN-${Math.random().toString(16).substring(2, 7).toUpperCase()}`,
              category_code: catCode,
              variant_id: vid,
              variant_name: res.variant_name || vid,
              risk_score: res.risk_score,
              risk_percent: res.risk_percent || `${(res.risk_score * 100).toFixed(1)}%`,
              action: res.action,
              signals: res.signals || {},
              explanation: res.action_message,
              analyst_summary: res.analyst_summary || '',
            });
          }
        } catch (err) {
          console.warn(`[GeneratorPage] Preset error for ${vid}:`, err.message);
        }
      }
      setSamplePayloads(sampleList);
    } catch (err) {
      console.warn('[GeneratorPage] Campaign run error:', err.message);
    } finally {
      setIsGenerating(false);
      setHasGenerated(true);
      setShowToast(true);
    }
  };

  useEffect(() => {
    handleGenerate();
  }, []);

  const displayedVectors = selectedCategoryFilter === 'ALL'
    ? attackVectors
    : attackVectors.filter((v) => v.domain === selectedCategoryFilter);

  const vectorChartData = attackVectors
    .filter((v) => selectedVectors.includes(v.id))
    .map((v) => {
      const baseCount = Math.round(fraudCount / Math.max(1, selectedVectors.length));
      const variation = Math.sin(v.name.length) * 0.2;
      const count = Math.max(10, Math.round(baseCount * (1 + variation)));
      return {
        id: v.id,
        name: v.id.length > 12 ? v.id.substring(0, 12) + '..' : v.id,
        fullName: v.name,
        count: count,
        color: v.color,
      };
    });

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="border border-border/80 bg-card/60 backdrop-blur rounded-lg p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Zap className="h-5 w-5 text-primary animate-pulse" />
              <span className="text-xs font-mono font-semibold tracking-wider text-primary uppercase">
                Enterprise Adversarial Engine
              </span>
            </div>
            <h1 className="text-2xl font-semibold text-foreground">7-Category Synthetic Campaign Generator</h1>
            <p className="text-sm text-muted-foreground mt-1 max-w-2xl">
              Simulate realistic adversarial transactions and emerging threats across all 7 Mastercard fraud taxonomy categories, parameterized with multi-vector evasion noise.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground font-semibold rounded-md hover:bg-primary/90 transition shadow-lg shadow-primary/20 disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Synthesizing Campaign...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  Run Attack Campaign
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Parameter Controls */}
        <div className="border border-border/80 bg-card/60 backdrop-blur rounded-lg p-5 space-y-6">
          <div className="flex items-center justify-between border-b border-border/60 pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">Campaign Parameters</h2>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-muted-foreground">BATCH TRANSACTION VOLUME</span>
                <span className="text-primary font-bold">{transactionCount.toLocaleString()} txns</span>
              </div>
              <input
                type="range"
                min="1000"
                max="50000"
                step="1000"
                value={transactionCount}
                onChange={(e) => setTransactionCount(Number(e.target.value))}
                className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-muted-foreground">ADVERSARIAL ATTACK RATIO</span>
                <span className="text-destructive font-bold">{fraudRatio.toFixed(1)}% ({fraudCount.toLocaleString()} fraud txns)</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="25.0"
                step="0.5"
                value={fraudRatio}
                onChange={(e) => setFraudRatio(Number(e.target.value))}
                className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-destructive"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-muted-foreground">EVASION / PERTURBATION NOISE</span>
                <span className="text-amber-400 font-bold">{evasionLevel}% Stealth Intensity</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={evasionLevel}
                onChange={(e) => setEvasionLevel(Number(e.target.value))}
                className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-amber-400"
              />
            </div>
          </div>

          {/* Category Filter Tabs */}
          <div className="pt-2 border-t border-border/60">
            <label className="text-xs font-mono text-muted-foreground uppercase tracking-wider block mb-2">Filter Category</label>
            <div className="grid grid-cols-4 gap-1">
              {['ALL', 'ATO', 'SOC', 'PM', 'TB', 'MRF', 'MM', 'GENAI'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategoryFilter(cat)}
                  className={`px-2 py-1 text-xs font-mono rounded text-center transition ${
                    selectedCategoryFilter === cat
                      ? 'bg-primary text-primary-foreground font-bold'
                      : 'bg-secondary/40 text-muted-foreground hover:bg-secondary/80'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Middle Column: 22 Attack Vectors Selection */}
        <div className="lg:col-span-2 border border-border/80 bg-card/60 backdrop-blur rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-border/60 pb-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">
                Active Attack Vectors ({selectedVectors.length} of {attackVectors.length} Selected)
              </h2>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSelectAll}
                className="text-xs text-primary hover:underline font-mono"
              >
                Select All
              </button>
              <span className="text-xs text-muted-foreground">|</span>
              <button
                onClick={handleDeselectAll}
                className="text-xs text-muted-foreground hover:text-foreground font-mono"
              >
                Reset
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-80 overflow-y-auto pr-1">
            {displayedVectors.map((v) => {
              const isSelected = selectedVectors.includes(v.id);
              return (
                <div
                  key={v.id}
                  onClick={() => toggleVector(v.id)}
                  className={`flex items-center justify-between p-2.5 rounded border cursor-pointer transition ${
                    isSelected
                      ? 'border-primary/50 bg-primary/10 text-foreground'
                      : 'border-border/40 bg-secondary/20 text-muted-foreground opacity-60 hover:opacity-100'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {isSelected ? (
                      <CheckSquare className="h-4 w-4 text-primary flex-shrink-0" />
                    ) : (
                      <Square className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    )}
                    <div className="min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-mono font-bold" style={{ color: v.color }}>
                          {v.id}
                        </span>
                        <span className="text-xs truncate font-medium">{v.name}</span>
                      </div>
                      <span className="text-[10px] text-muted-foreground font-mono">{v.domain} Category</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-secondary/60 text-foreground">
                    {(v.risk_score * 100).toFixed(0)}% Risk
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Vector Distribution Chart */}
      <div className="border border-border/80 bg-card/60 backdrop-blur rounded-lg p-5">
        <div className="flex items-center justify-between border-b border-border/60 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <BarChart2 className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">
              Synthetic Distribution by Attack Vector
            </h2>
          </div>
          <span className="text-xs font-mono text-muted-foreground">
            Target Batch: {fraudCount.toLocaleString()} Fraud Cases
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={vectorChartData} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
              <XAxis dataKey="id" tick={{ fill: '#888', fontSize: 11 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fill: '#888', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#111', borderColor: '#333', borderRadius: '6px', fontSize: '12px' }}
                formatter={(value, name, props) => [`${value} txns`, props.payload.fullName]}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {vectorChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || '#00e5ff'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Live Generated Payloads & LLM Summaries Table */}
      {samplePayloads.length > 0 && (
        <div className="border border-border/80 bg-card/60 backdrop-blur rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-border/60 pb-3">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">
                Live Synthetic Payloads & HDC Scan Verdicts ({samplePayloads.length} Sample Vectors)
              </h2>
            </div>
            <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" /> 10,000-D Prototypes Active
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {samplePayloads.map((payload) => (
              <div
                key={payload.id}
                className="border border-border/60 bg-secondary/20 rounded-lg p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-primary/20 text-primary">
                      {payload.variant_id}
                    </span>
                    <span className="text-sm font-semibold text-foreground">{payload.variant_name}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                    payload.action === 'BLOCK' || payload.action === 'REJECT_PAYLOAD' || payload.action === 'RATE_LIMIT_BLOCK' || payload.action === 'FREEZE_SETTLEMENT'
                      ? 'bg-destructive/20 text-destructive'
                      : 'bg-amber-400/20 text-amber-400'
                  }`}>
                    {payload.action} ({payload.risk_percent})
                  </span>
                </div>

                <div className="text-xs font-mono bg-black/40 p-2.5 rounded border border-border/40 text-muted-foreground space-y-1">
                  <div className="text-foreground font-semibold flex items-center gap-1">
                    <Info className="h-3.5 w-3.5 text-primary" /> Real-Time Decision:
                  </div>
                  <p className="text-xs text-foreground/90 font-sans">{payload.explanation}</p>
                </div>

                {payload.analyst_summary && (
                  <div className="text-xs bg-primary/5 p-2.5 rounded border border-primary/20 space-y-1">
                    <span className="text-primary font-mono font-bold text-[11px] block uppercase tracking-wider">
                      GenAI Analyst Narrative:
                    </span>
                    <p className="text-xs text-muted-foreground font-sans leading-relaxed">{payload.analyst_summary}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
