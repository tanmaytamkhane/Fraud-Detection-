// mockTransactions.js — Transaction Stream & Simulation Engine

import { ATTACK_VECTORS } from "./attacksData";

const CATEGORIES = [
  "grocery", "restaurant", "utility", "online_retail", "digital_goods", 
  "wire_transfer", "bnpl", "p2p", "gas", "donation"
];

const LEGIT_AMOUNTS = [
  8.50, 13.58, 15.85, 17.25, 19.48, 22.05, 23.60, 27.43, 30.92, 
  31.56, 40.93, 41.86, 61.53, 65.81, 66.64, 94.74, 104.11
];

export function generateRandomTransaction(index = 1, attackRatio = 20, evasion = 30) {
  const isAttack = Math.random() * 100 < attackRatio;
  const idPrefix = Math.random().toString(16).substring(2, 10);
  const idSuffix = Math.random().toString(16).substring(2, 5);
  const id = `${idPrefix}-${idSuffix}`;

  if (!isAttack) {
    // Legit transaction
    const category = CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)];
    let amount = LEGIT_AMOUNTS[Math.floor(Math.random() * LEGIT_AMOUNTS.length)];
    if (category === "wire_transfer") {
      amount = +(Math.random() * 5000 + 1000).toFixed(2);
    }

    // Legit scores are near 0%
    const fraudProb = Math.random() < 0.98 ? 0.0 : +(Math.random() * 0.15).toFixed(2);
    const isFlagged = fraudProb >= 0.50;

    return {
      id,
      index,
      amount,
      category,
      isAttack: false,
      attackVector: "legit",
      attackName: "Normal Activity",
      fraudProb: +(fraudProb * 100).toFixed(1),
      decision: isFlagged ? "REVIEW" : "PASS",
      matrixTag: isFlagged ? "FP" : "TN",
      timestamp: new Date().toISOString(),
      displayDate: new Date().toLocaleTimeString(),
      features: [
        { name: "device_reuse_count", value: 1.0, contribution: -1.2 },
        { name: "amount_deviation", value: 0.05, contribution: -0.8 },
        { name: "new_device", value: 0.0, contribution: -0.5 },
        { name: "velocity_24h", value: 1.0, contribution: -0.4 },
        { name: "location_change", value: 0.0, contribution: -0.3 }
      ],
      explanation: "Transaction exhibits standard user behavioral patterns. Cardholder device fingerprint, location, and velocity are strictly consistent with historic baseline parameters."
    };
  }

  // Attack transaction
  const activeVectors = ATTACK_VECTORS;
  const vector = activeVectors[Math.floor(Math.random() * activeVectors.length)];
  
  // High value for wire/BEC/Deepfake, moderate for others
  let amount = 0;
  if (vector.id === "deepfake_voice_socialeng" || vector.id === "bec_invoice_fraud") {
    amount = +(Math.random() * 25000 + 15000).toFixed(2);
  } else if (vector.id === "cnp_bot_carding") {
    amount = +(Math.random() * 5 + 0.5).toFixed(2);
  } else if (vector.id === "synthetic_identity" || vector.id === "prompt_injection_chatbot") {
    amount = +(Math.random() * 800 + 100).toFixed(2);
  } else {
    amount = +(Math.random() * 1500 + 200).toFixed(2);
  }

  const categoryMap = {
    deepfake_voice_socialeng: "wire_transfer",
    bec_invoice_fraud: "wire_transfer",
    synthetic_identity: "bnpl",
    prompt_injection_chatbot: "online_retail",
    ai_phishing_smishing: "p2p",
    adversarial_evasion: "digital_goods",
    mule_network_coord: "p2p",
    cnp_bot_carding: "digital_goods"
  };
  const category = categoryMap[vector.id] || "online_retail";

  // Evasion factor affects fraud probability detection
  const evasionFactor = evasion / 100;
  let fraudProb = 1.0;
  if (Math.random() < evasionFactor * 0.35) {
    // Evasive attack caught with lower confidence or stealth
    fraudProb = +(0.35 + Math.random() * 0.40).toFixed(2);
  }

  const isFlagged = fraudProb >= 0.50;
  const decision = isFlagged ? "BLOCK" : "PASS";
  const matrixTag = isFlagged ? "TP" : "FN";

  const featurePool = [
    { name: "device_reuse_count", value: 4.0, contribution: +3.85 },
    { name: "face_embedding_dup", value: 0.62, contribution: +2.67 },
    { name: "new_device", value: 1.0, contribution: +1.76 },
    { name: "new_payee", value: 1.0, contribution: +1.42 },
    { name: "graph_fanout", value: 4.0, contribution: +0.91 },
    { name: "amt_zscore", value: 4.5, contribution: +2.89 },
    { name: "velocity_burst", value: 0.95, contribution: +2.15 },
    { name: "time_anomaly", value: 0.85, contribution: +1.64 }
  ];

  return {
    id,
    index,
    amount,
    category,
    isAttack: true,
    attackVector: vector.id,
    attackName: vector.name,
    fraudProb: +(fraudProb * 100).toFixed(1),
    decision,
    matrixTag,
    timestamp: new Date().toISOString(),
    displayDate: new Date().toLocaleTimeString(),
    features: featurePool.slice(0, 5),
    explanation: `CRITICAL ALERT: Transaction triggered high-confidence ${vector.name} signatures. Multiple anomalous telemetry signals detected including sudden payee deviation, elevated velocity spikes, and unrecognized device fingerprint.`
  };
}

export function generateInitialBatch(count = 50) {
  const batch = [];
  for (let i = 1; i <= count; i++) {
    batch.push(generateRandomTransaction(i, 20, 30));
  }
  return batch;
}
