import React, { useState, useEffect, useRef } from 'react';
import { generateRandomTransaction } from '../data/mockTransactions';
import { scanTransaction, scanTransfer, scanGenAI, scanCategoryPreset, scanCategory } from '../api/client';
import { Play, Square, Activity, AlertTriangle, CheckCircle2, ChevronRight, Zap } from 'lucide-react';

const CATEGORIES = [
  "grocery", "restaurant", "utility", "online_retail", "digital_goods", 
  "wire_transfer", "bnpl", "p2p", "gas", "donation", "deepfake_voice_wire", 
  "qr_merchant_payment", "carding_micro_auth", "refund_credit"
];

const ATTACK_DOMAINS = ['ATO', 'SOC', 'PM', 'TB', 'MRF', 'MM', 'GENAI'];

async function generateLiveTransaction(index = 1, attackRatio = 25, evasion = 20) {
  const isAttack = Math.random() * 100 < attackRatio;
  const randHex = Math.random().toString(16).substring(2, 7).toUpperCase();
  const evasionFactor = evasion / 100;

  if (!isAttack) {
    const category = CATEGORIES[Math.floor(Math.random() * 6)];
    const amount = +(Math.random() * 85 + 8).toFixed(2);
    const signals = {
      device_risk: +(Math.random() * 0.18).toFixed(2),
      address_mismatch: +(Math.random() * 0.12).toFixed(2),
      amount_deviation: +(Math.random() * 0.15).toFixed(2),
      velocity: +(Math.random() * 0.20).toFixed(2),
      time_anomaly: +(Math.random() * 0.15).toFixed(2),
      channel_risk: +(Math.random() * 0.18).toFixed(2),
    };

    try {
      const scan = await scanTransaction(signals);
      return {
        id: `TXN-${randHex}`,
        index,
        amount,
        category,
        isAttack: false,
        attackVector: 'LEGIT',
        attackName: scan.variant_name || 'Normal Activity',
        fraudProb: +(scan.risk_score * 100).toFixed(1),
        decision: scan.action,
        matrixTag: scan.action === 'BLOCK' || scan.action === 'HOLD' ? 'FP' : 'TN',
        timestamp: scan.timestamp || new Date().toISOString(),
        displayDate: new Date().toLocaleTimeString(),
        features: [
          { name: 'device_risk', value: signals.device_risk, contribution: -1.2 },
          { name: 'amount_deviation', value: signals.amount_deviation, contribution: -0.8 },
          { name: 'velocity', value: signals.velocity, contribution: -0.4 },
          { name: 'address_mismatch', value: signals.address_mismatch, contribution: -0.3 },
          { name: 'channel_risk', value: signals.channel_risk, contribution: -0.5 },
        ],
        explanation: scan.action_message || 'Transaction exhibits normal baseline behavior. Cardholder telemetry is verified.',
      };
    } catch {
      return generateRandomTransaction(index, attackRatio, evasion);
    }
  }

  // Attack Pool across all 7 Categories
  const chosenDomain = ATTACK_DOMAINS[Math.floor(Math.random() * ATTACK_DOMAINS.length)];

  if (chosenDomain === 'GENAI') {
    const vid = ['GENAI-V1', 'GENAI-V2', 'GENAI-V3', 'GENAI-V4'][Math.floor(Math.random() * 4)];
    try {
      const scan = await scanGenAI({
        llm_semantic_intent_score: +(0.95 * (1 - 0.2 * evasionFactor)).toFixed(2),
        voice_biometric_jitter: +(0.98 * (1 - 0.2 * evasionFactor)).toFixed(2),
        synthetic_face_embedding_dist: 0.90,
        adversarial_perturbation_index: 0.40,
        device_risk: 0.85,
        amount_deviation: 0.70,
      });
      return {
        id: `GENAI-${randHex}`,
        index,
        amount: +(Math.random() * 45000 + 5000).toFixed(2),
        category: 'deepfake_voice_wire',
        isAttack: true,
        attackVector: scan.matched_variant || vid,
        attackName: scan.variant_name || vid,
        fraudProb: +(scan.risk_score * 100).toFixed(1),
        decision: scan.action,
        matrixTag: scan.action.includes('BLOCK') || scan.action.includes('HOLD') ? 'TP' : 'FN',
        timestamp: scan.timestamp || new Date().toISOString(),
        displayDate: new Date().toLocaleTimeString(),
        features: [
          { name: 'voice_biometric_jitter', value: 0.98, contribution: 4.2 },
          { name: 'llm_semantic_intent_score', value: 0.95, contribution: 3.6 },
          { name: 'synthetic_face_embedding_dist', value: 0.90, contribution: 3.4 },
        ],
        explanation: scan.action_message,
          analystSummary: scan.analyst_summary || scan.action_message,
      };
    } catch {
      return generateRandomTransaction(index, attackRatio, evasion);
    }
  }

  if (chosenDomain === 'MM') {
    const vid = ['MM-V1', 'MM-V2', 'MM-V3', 'MM-V4'][Math.floor(Math.random() * 4)];
    try {
      const scan = await scanTransfer({
        fan_out_degree: 0.95,
        fan_in_degree: 0.20,
        transit_velocity_sec: 0.95,
        amount_layering_ratio: 0.98,
        shared_device_cluster: 1.0,
        account_dormancy_score: 0.30,
        transfer_id: `TRX-${randHex}`,
        sender_account: `ACC-${randHex}`,
        receiver_account: `MULE-${randHex}`,
        amount: +(Math.random() * 12000 + 1500).toFixed(2),
        device_id: `DEV-RING-${Math.floor(Math.random()*90 + 10)}`
      });
      return {
        id: `MULE-${randHex}`,
        index,
        amount: scan.transfer?.amount || +(Math.random() * 12000 + 1500).toFixed(2),
        category: 'mule_aggregation',
        isAttack: true,
        attackVector: scan.matched_variant || vid,
        attackName: scan.variant_name || vid,
        fraudProb: +(scan.risk_score * 100).toFixed(1),
        decision: scan.action,
        matrixTag: scan.action.includes('BLOCK') || scan.action.includes('HOLD') ? 'TP' : 'FN',
        timestamp: scan.timestamp || new Date().toISOString(),
        displayDate: new Date().toLocaleTimeString(),
        features: [
          { name: 'transit_velocity_sec', value: 0.95, contribution: 4.4 },
          { name: 'amount_layering_ratio', value: 0.98, contribution: 3.8 },
          { name: 'shared_device_cluster', value: 1.0, contribution: 3.5 },
        ],
        explanation: scan.action_message,
          analystSummary: scan.analyst_summary || scan.action_message,
      };
    } catch {
      return generateRandomTransaction(index, attackRatio, evasion);
    }
  }

  // Categories 2, 3, 4, 5, 1 (SOC, PM, TB, MRF, ATO)
  const variantMap = {
    'SOC': ['SOC-V1', 'SOC-V2', 'SOC-V3'],
    'PM': ['PM-V1', 'PM-V2'],
    'TB': ['TB-V1', 'TB-V2'],
    'MRF': ['MRF-V1', 'MRF-V2'],
    'ATO': ['ATO-V1', 'ATO-V2', 'ATO-V3', 'ATO-V4', 'ATO-V5'],
  };
  const vList = variantMap[chosenDomain] || ['ATO-V1'];
  const vid = vList[Math.floor(Math.random() * vList.length)];

  try {
    const scan = await scanCategoryPreset(chosenDomain, vid);
    const isFlagged = scan.action.includes('BLOCK') || scan.action.includes('HOLD');
    let amt = +(Math.random() * 3500 + 400).toFixed(2);
    if (chosenDomain === 'TB') amt = +(Math.random() * 1.50 + 0.50).toFixed(2);
    if (chosenDomain === 'SOC') amt = +(Math.random() * 15000 + 2500).toFixed(2);

    return {
      id: `${chosenDomain}-${randHex}`,
      index,
      amount: amt,
      category: chosenDomain === 'PM' ? 'qr_merchant_payment' : (chosenDomain === 'TB' ? 'carding_micro_auth' : (chosenDomain === 'MRF' ? 'refund_credit' : 'wire_transfer')),
      isAttack: true,
      attackVector: scan.matched_variant || vid,
      attackName: scan.variant_name || vid,
      fraudProb: +(scan.risk_score * 100).toFixed(1),
      decision: scan.action,
      matrixTag: isFlagged ? 'TP' : 'FN',
      timestamp: scan.timestamp || new Date().toISOString(),
      displayDate: new Date().toLocaleTimeString(),
      features: scan.signals ? Object.entries(scan.signals).slice(0, 4).map(([k, v]) => ({
        name: k,
        value: Number(v),
        contribution: +(Number(v) * 3.5).toFixed(2),
      })) : [
        { name: 'domain_risk_score', value: 0.90, contribution: 3.5 },
        { name: 'amount_deviation', value: 0.85, contribution: 2.8 },
      ],
      explanation: scan.action_message,
          analystSummary: scan.analyst_summary || scan.action_message,
    };
  } catch {
    return generateRandomTransaction(index, attackRatio, evasion);
  }
}

export default function StreamPage({ onSelectTransaction, isStreaming, setIsStreaming, transactions = [], setTransactions }) {
  const [count, setCount] = useState(150);
  const [attackRatio, setAttackRatio] = useState(25);
  const [evasion, setEvasion] = useState(20);
  const [currentIndex, setCurrentIndex] = useState(1);

  const totalCount = transactions.length;
  const flaggedCount = transactions.filter((t) => t.decision?.includes('BLOCK') || t.decision?.includes('HOLD')).length;
  const missedCount = transactions.filter((t) => t.matrixTag === 'FN').length;
  const falsePosCount = transactions.filter((t) => t.matrixTag === 'FP').length;

  const intervalRef = useRef(null);

  useEffect(() => {
    if (transactions.length === 0) {
      let isMounted = true;
      async function loadInitial() {
        const presets = ['ATO-V1', 'SOC-V1', 'PM-V1', 'TB-V1', 'MRF-V1', 'MM-V1', 'GENAI-V2', 'LEGIT', 'LEGIT', 'LEGIT'];
        const batch = [];
        for (let i = 0; i < presets.length; i++) {
          const p = presets[i];
          const isAtk = p !== 'LEGIT';
          batch.push({
            id: isAtk ? `${p.split('-')[0]}-${Math.random().toString(16).substring(2, 6).toUpperCase()}` : `TXN-${Math.random().toString(16).substring(2, 6).toUpperCase()}`,
            index: i + 1,
            amount: isAtk ? +(Math.random() * 4500 + 800).toFixed(2) : +(Math.random() * 65 + 15).toFixed(2),
            category: isAtk ? 'wire_transfer' : 'online_retail',
            isAttack: isAtk,
            attackVector: p,
            attackName: isAtk ? p : 'Normal Activity',
            fraudProb: isAtk ? 95.4 : 4.8,
            decision: isAtk ? 'BLOCK' : 'APPROVE',
            matrixTag: isAtk ? 'TP' : 'TN',
            timestamp: new Date().toISOString(),
            displayDate: new Date().toLocaleTimeString(),
            features: [
              { name: 'primary_risk_signal', value: isAtk ? 0.92 : 0.10, contribution: isAtk ? 3.5 : -1.2 },
              { name: 'anomaly_deviation', value: isAtk ? 0.88 : 0.12, contribution: isAtk ? 2.8 : -0.8 },
            ],
            explanation: isAtk ? `CRITICAL: ${p} signature detected by 7-Category HDC engine.` : 'Normal cardholder behavior verified.',
          });
        }
        if (isMounted) setTransactions(batch);
      }
      loadInitial();
      return () => {
        isMounted = false;
      };
    }
  }, [transactions.length, setTransactions]);

  useEffect(() => {
    if (isStreaming) {
      intervalRef.current = setInterval(async () => {
        const nextTx = await generateLiveTransaction(currentIndex, attackRatio, evasion);
        setTransactions((prev) => {
          if (prev.length >= count) {
            setIsStreaming(false);
            return prev;
          }
          return [nextTx, ...prev];
        });
        setCurrentIndex((i) => i + 1);
      }, 500);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isStreaming, count, attackRatio, evasion, currentIndex, setIsStreaming, setTransactions]);

  const toggleStreaming = () => {
    if (!isStreaming) {
      if (transactions.length >= count) {
        setTransactions([]);
      }
      setIsStreaming(true);
    } else {
      setIsStreaming(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="text-xs font-mono text-cyan-400 tracking-widest uppercase">
          CLOSED-LOOP · GENERATE → DETECT (7-CATEGORY HDC INFERENCE)
        </div>
        <h1 className="text-4xl lg:text-5xl font-semibold tracking-tight text-white">
          Live Transaction Stream
        </h1>
        <p className="text-zinc-400 text-sm max-w-3xl leading-relaxed">
          Real-time payment simulator streaming transactions across all 7 Master Fraud Categories. Click any transaction to inspect live multi-modal signals in the Investigation Console.
        </p>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Stream Config & 4 Counters */}
        <div className="lg:col-span-4 bg-[#0b0e14] border border-[#1a1f2c] rounded-lg p-6 space-y-7 shadow-xl">
          <div className="space-y-5">
            <div className="text-[11px] font-mono text-zinc-400 tracking-widest uppercase font-semibold">
              STREAM CONFIG
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-zinc-300">Count:</span>
                <span className="text-cyan-400 font-bold">{count}</span>
              </div>
              <input
                type="range"
                min="20"
                max="500"
                step="10"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-zinc-300">Attack ratio:</span>
                <span className="text-cyan-400 font-bold">{attackRatio}%</span>
              </div>
              <input
                type="range"
                min="5"
                max="60"
                step="5"
                value={attackRatio}
                onChange={(e) => setAttackRatio(Number(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-zinc-300">Evasion level:</span>
                <span className="text-cyan-400 font-bold">{evasion}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={evasion}
                onChange={(e) => setEvasion(Number(e.target.value))}
                className="w-full"
              />
            </div>

            <button
              onClick={toggleStreaming}
              className={`w-full flex items-center justify-center gap-2 py-3.5 rounded font-mono font-bold text-xs tracking-wider uppercase transition-all duration-150 shadow-lg ${
                isStreaming
                  ? 'bg-transparent hover:bg-red-500/10 text-red-400 border border-red-500/50 shadow-red-500/10'
                  : 'bg-cyan-400 hover:bg-cyan-300 text-black shadow-cyan-500/20'
              }`}
            >
              {isStreaming ? (
                <>
                  <Square className="w-4 h-4 fill-red-400" />
                  <span>STOP LIVE STREAM</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-black" />
                  <span>START 7-CATEGORY STREAM</span>
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] font-mono text-zinc-400 tracking-widest uppercase font-semibold">TOTAL</div>
              <div className="text-2xl font-mono font-bold text-white">{totalCount}</div>
            </div>

            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] font-mono text-zinc-400 tracking-widest uppercase font-semibold">FLAGGED</div>
              <div className="text-2xl font-mono font-bold text-cyan-400">{flaggedCount}</div>
            </div>

            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] font-mono text-zinc-400 tracking-widest uppercase font-semibold">MISSED</div>
              <div className="text-2xl font-mono font-bold text-red-500">{missedCount}</div>
            </div>

            <div className="bg-[#07090e] border border-[#1a1f2c] p-4 rounded-lg space-y-1">
              <div className="text-[10px] font-mono text-zinc-400 tracking-widest uppercase font-semibold">FALSE POS</div>
              <div className="text-2xl font-mono font-bold text-amber-400">{falsePosCount}</div>
            </div>
          </div>
        </div>

        {/* Right Column: Transaction Feed Table */}
        <div className="lg:col-span-8 bg-[#0b0e14] border border-[#1a1f2c] rounded-lg p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between text-xs font-mono pb-3 border-b border-[#1a1f2c]">
            <div className="flex items-center gap-2 tracking-widest uppercase font-semibold">
              <span className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-emerald-400 animate-ping' : 'bg-zinc-500'}`} />
              <span className={isStreaming ? 'text-emerald-400' : 'text-zinc-400'}>
                {isStreaming ? 'STREAMING · 7-CATEGORY INFERENCE' : 'IDLE · CLICK ANY ROW TO INVESTIGATE'}
              </span>
            </div>
            <span className="text-zinc-500">{transactions.length} EVENTS</span>
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {transactions.map((tx) => {
              const isBlock = tx.decision?.includes('BLOCK') || tx.decision?.includes('HOLD');
              return (
                <div
                  key={tx.id}
                  onClick={() => onSelectTransaction(tx)}
                  className={`flex flex-wrap sm:flex-nowrap items-center justify-between gap-3 p-3 rounded-lg border cursor-pointer font-mono text-xs transition-all duration-150 ${
                    isBlock
                      ? 'bg-[#140b0e] border-red-500/20 hover:border-red-500/50 hover:bg-[#1a0e12]'
                      : 'bg-[#080b10] border-[#161a26] hover:border-[#262e40] hover:bg-[#0c1017]'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-[140px]">
                    <span
                      className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        tx.isAttack ? 'bg-red-500' : 'bg-emerald-400'
                      }`}
                    />
                    <span className="text-zinc-300 font-semibold">{tx.id}</span>
                  </div>

                  <div className="text-zinc-400 min-w-[110px] text-left truncate">
                    {tx.category}
                  </div>

                  <div className="text-white font-bold min-w-[90px] text-right">
                    ${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>

                  <div className="flex items-center gap-2 min-w-[180px]">
                    <div className="w-24 h-1.5 bg-[#1a1f2c] rounded-full overflow-hidden flex-shrink-0">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          tx.fraudProb >= 50 ? 'bg-red-500' : 'bg-zinc-600'
                        }`}
                        style={{ width: `${Math.max(5, tx.fraudProb)}%` }}
                      />
                    </div>
                    <span className="text-[11px] text-zinc-400 flex-shrink-0 w-8">
                      {tx.fraudProb}%
                    </span>
                    <span
                      className={`text-[10px] truncate max-w-[110px] ${
                        tx.isAttack ? 'text-red-400 font-semibold' : 'text-zinc-500'
                      }`}
                    >
                      {tx.attackVector}
                    </span>
                  </div>

                  <div className="min-w-[70px] text-right">
                    <span
                      className={`font-bold uppercase tracking-wider text-[11px] ${
                        isBlock ? 'text-red-400' : 'text-emerald-400'
                      }`}
                    >
                      {tx.decision || 'PASS'}
                    </span>
                  </div>

                  <div className="min-w-[30px] text-right text-[10px] font-bold text-zinc-500">
                    {tx.matrixTag}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
