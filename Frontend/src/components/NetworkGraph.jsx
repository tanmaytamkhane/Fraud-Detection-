import React, { useState } from 'react';
import { Shield, AlertTriangle, ArrowRight, Activity, Layers, Server } from 'lucide-react';

export default function NetworkGraph({ graphData, onSelectNode }) {
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [hoveredNodeId, setHoveredNodeId] = useState(null);

  const defaultNodes = [
    { id: 'VICTIM-ORIGIN', label: 'Victim Account (Compromised)', type: 'origin', risk: 'HIGH', x: 80, y: 180, amount: '$14,500', out_deg: 2, in_deg: 0, device: 'DEV-ORIGIN-01' },
    { id: 'MULE-WRK-104', label: 'Mule Intermediary A', type: 'mule', risk: 'MEDIUM', x: 300, y: 100, amount: '$7,200', out_deg: 1, in_deg: 1, device: 'DEV-RING-77' },
    { id: 'MULE-WRK-208', label: 'Mule Intermediary B', type: 'mule', risk: 'MEDIUM', x: 300, y: 260, amount: '$7,300', out_deg: 1, in_deg: 1, device: 'DEV-RING-77' },
    { id: 'MULE-MSTR-99', label: 'Master Cashout Node', type: 'cashout', risk: 'CRITICAL', x: 520, y: 180, amount: '$14,100', out_deg: 0, in_deg: 2, device: 'OFFSHORE-GATEWAY' },
  ];

  const defaultEdges = [
    { source: 'VICTIM-ORIGIN', target: 'MULE-WRK-104', amount: '$7,200', status: 'HOLD', velocity: '12s' },
    { source: 'VICTIM-ORIGIN', target: 'MULE-WRK-208', amount: '$7,300', status: 'HOLD', velocity: '18s' },
    { source: 'MULE-WRK-104', target: 'MULE-MSTR-99', amount: '$7,050', status: 'BLOCK', velocity: '4s' },
    { source: 'MULE-WRK-208', target: 'MULE-MSTR-99', amount: '$7,050', status: 'BLOCK', velocity: '6s' },
  ];

  const nodes = (graphData && graphData.nodes && graphData.nodes.length > 0)
    ? graphData.nodes.map((n, i) => ({
        ...n,
        x: n.x || (n.type === 'origin' ? 80 : n.type === 'cashout' ? 520 : 300),
        y: n.y || (n.type === 'origin' ? 180 : n.type === 'cashout' ? 180 : i % 2 === 0 ? 100 : 260),
        amount: n.amount || (n.type === 'origin' ? '$14,500' : n.type === 'cashout' ? '$14,100' : '$7,250'),
        device: n.device || 'DEV-RING-77'
      }))
    : defaultNodes;

  const edges = (graphData && (graphData.links || graphData.edges) && (graphData.links || graphData.edges).length > 0)
    ? (graphData.links || graphData.edges).map(e => ({
        ...e,
        amount: typeof e.amount === 'number' ? `$${e.amount.toLocaleString()}` : e.amount || '$1,200',
        velocity: e.velocity || `${e.velocity_sec || 8}s`
      }))
    : defaultEdges;

  const selectedNode = nodes.find(n => n.id === (selectedNodeId || 'MULE-MSTR-99')) || nodes[0];

  const getNodeColor = (type, risk) => {
    if (risk === 'CRITICAL' || type === 'cashout') return '#ff1744';
    if (risk === 'HIGH' || type === 'origin') return '#f59e0b';
    if (type === 'mule') return '#00e5ff';
    return '#00e676';
  };

  return (
    <div className="border border-border/80 bg-card/60 backdrop-blur rounded-lg p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/60 pb-3">
        <div className="flex items-center gap-2">
          <Layers className="h-5 w-5 text-primary animate-pulse" />
          <div>
            <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">
              NetworkX Multi-Hop Mule Ring Topology
            </h2>
            <p className="text-xs text-muted-foreground">
              Dynamic entity relationship graph tracking smurfing fan-out, shared device clusters, and cashout nodes.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="flex items-center gap-1 text-amber-400">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span> Origin Node
          </span>
          <span className="flex items-center gap-1 text-cyan-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span> Mule Workers
          </span>
          <span className="flex items-center gap-1 text-red-500">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span> Cashout Core
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* SVG Interactive Canvas */}
        <div className="lg:col-span-2 relative bg-black/40 rounded-lg border border-border/40 p-4 overflow-hidden min-h-[340px] flex items-center justify-center">
          <svg viewBox="0 0 600 360" className="w-full h-full max-h-[320px] select-none">
            <defs>
              <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#00e5ff" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#ff1744" stopOpacity="0.9" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="28" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#00e5ff" />
              </marker>
              <marker id="arrowhead-red" markerWidth="8" markerHeight="6" refX="28" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#ff1744" />
              </marker>
            </defs>

            {/* Background Grid Pattern */}
            <g opacity="0.08">
              {[...Array(12)].map((_, i) => (
                <line key={`vg-${i}`} x1={i * 50} y1="0" x2={i * 50} y2="360" stroke="#fff" strokeDasharray="3 3" />
              ))}
              {[...Array(8)].map((_, i) => (
                <line key={`hg-${i}`} x1="0" y1={i * 45} x2="600" y2={i * 45} stroke="#fff" strokeDasharray="3 3" />
              ))}
            </g>

            {/* Edge Lines with Transfer Amounts */}
            {edges.map((edge, idx) => {
              const srcNode = nodes.find(n => n.id === edge.source) || nodes[0];
              const tgtNode = nodes.find(n => n.id === edge.target) || nodes[nodes.length - 1];
              const midX = (srcNode.x + tgtNode.x) / 2;
              const midY = (srcNode.y + tgtNode.y) / 2;
              const isBlock = edge.status === 'BLOCK' || edge.status === 'FREEZE_ACCOUNT';

              return (
                <g key={`edge-${idx}`}>
                  <line
                    x1={srcNode.x}
                    y1={srcNode.y}
                    x2={tgtNode.x}
                    y2={tgtNode.y}
                    stroke={isBlock ? '#ff1744' : '#00e5ff'}
                    strokeWidth="2.5"
                    strokeDasharray={isBlock ? '6 4' : 'none'}
                    markerEnd={isBlock ? 'url(#arrowhead-red)' : 'url(#arrowhead)'}
                    className="opacity-70 transition-all hover:opacity-100"
                  />
                  {/* Directional Velocity Tag */}
                  <rect
                    x={midX - 32}
                    y={midY - 10}
                    width="64"
                    height="20"
                    rx="4"
                    fill="#050608"
                    stroke={isBlock ? '#ff1744' : '#1e293b'}
                    strokeWidth="1"
                  />
                  <text
                    x={midX}
                    y={midY + 4}
                    fill={isBlock ? '#ff5252' : '#38bdf8'}
                    fontSize="10"
                    fontFamily="monospace"
                    textAnchor="middle"
                    fontWeight="bold"
                  >
                    {edge.amount}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
              const isSelected = (selectedNodeId === node.id) || (!selectedNodeId && node.type === 'cashout');
              const isHovered = hoveredNodeId === node.id;
              const color = getNodeColor(node.type, node.risk);

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer transition-all"
                  onClick={() => {
                    setSelectedNodeId(node.id);
                    if (onSelectNode) onSelectNode(node);
                  }}
                  onMouseEnter={() => setHoveredNodeId(node.id)}
                  onMouseLeave={() => setHoveredNodeId(null)}
                >
                  {/* Outer Risk Halo */}
                  {(node.risk === 'CRITICAL' || isSelected) && (
                    <circle
                      r="32"
                      fill={color}
                      opacity={isSelected ? "0.35" : "0.2"}
                      className="animate-pulse"
                    />
                  )}
                  {/* Middle Disc */}
                  <circle
                    r="22"
                    fill="#0f172a"
                    stroke={color}
                    strokeWidth={isSelected ? "3" : "2"}
                    filter="url(#glow)"
                  />
                  {/* Node Icon / Initial */}
                  <text
                    y="4"
                    fill={color}
                    fontSize="11"
                    fontFamily="monospace"
                    textAnchor="middle"
                    fontWeight="bold"
                  >
                    {node.type === 'origin' ? 'ORG' : node.type === 'cashout' ? 'CSH' : 'MUL'}
                  </text>
                  {/* Node Label Below */}
                  <text
                    y="36"
                    fill="#e2e8f0"
                    fontSize="10"
                    fontFamily="sans-serif"
                    textAnchor="middle"
                    fontWeight="500"
                  >
                    {node.id}
                  </text>
                </g>
              );
            })}
          </svg>

          <div className="absolute bottom-2 left-2 text-[10px] font-mono text-zinc-400 bg-black/60 px-2 py-1 rounded border border-border/40">
            Topology: Directed Acyclic Sub-Cluster · Max Centrality: 0.98
          </div>
        </div>

        {/* Node Forensic Dossier Panel */}
        <div className="border border-border/80 bg-secondary/20 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-border/60 pb-2">
            <span className="text-xs font-mono uppercase tracking-wider text-muted-foreground">Entity Dossier</span>
            <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
              selectedNode.risk === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
              selectedNode.risk === 'HIGH' ? 'bg-amber-400/20 text-amber-300 border border-amber-400/40' :
              'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
            }`}>
              {selectedNode.risk} RISK NODE
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between font-mono">
              <span className="text-muted-foreground">Account ID:</span>
              <span className="text-foreground font-semibold">{selectedNode.id}</span>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-muted-foreground">Role:</span>
              <span className="text-primary font-medium capitalize">{selectedNode.type} Node</span>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-muted-foreground">Balance Transit:</span>
              <span className="text-emerald-400 font-bold">{selectedNode.amount}</span>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-muted-foreground">Linked Device:</span>
              <span className="text-zinc-300">{selectedNode.device}</span>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-muted-foreground">Degree Centrality:</span>
              <span className="text-cyan-400">{selectedNode.type === 'cashout' ? '0.98 (CRITICAL CONSOLIDATION)' : '0.65 (LAYER 1 HOP)'}</span>
            </div>
          </div>

          <div className="pt-2 border-t border-border/60">
            <div className="text-[11px] font-mono text-muted-foreground mb-1">AUTOMATED GRAPH MITIGATION:</div>
            <div className={`p-2 rounded text-xs font-sans font-medium ${
              selectedNode.type === 'cashout'
                ? 'bg-red-500/10 text-red-300 border border-red-500/20'
                : 'bg-amber-400/10 text-amber-300 border border-amber-400/20'
            }`}>
              {selectedNode.type === 'cashout'
                ? '🛑 FREEZE_SETTLEMENT & BLOCK_CHAIN: Inbound liquidity frozen. Suspicious offshore gateway alerted.'
                : '⚠️ HOLD_TRANSFER: Transit velocity <15s triggered automated 2-hop quarantine.'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
