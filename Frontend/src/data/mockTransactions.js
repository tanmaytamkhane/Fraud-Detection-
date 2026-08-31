// mockTransactions.js — Master 7-Category Transaction Generator & Stream Engine

import { ATTACK_VECTORS } from "./attacksData";

const CATEGORIES = [
  "grocery", "restaurant", "utility", "online_retail", "digital_goods", 
  "wire_transfer", "bnpl", "p2p", "gas", "donation", "deepfake_voice_wire", 
  "qr_merchant_payment", "carding_micro_auth", "refund_credit"
];

const LEGIT_AMOUNTS = [
  12.50, 18.25, 24.50, 32.80, 45.00, 68.20, 89.99, 112.50, 145.00, 
  180.75, 220.00, 310.50, 450.00, 520.00, 750.00
];

const CATEGORY_SIGNALS = {
  ATO: ["device_risk", "address_mismatch", "amount_deviation", "velocity", "time_anomaly", "channel_risk"],
  SOC: ["social_urgency_score", "voice_jitter_anomaly", "beneficiary_account_mismatch", "amount_deviation", "channel_risk", "device_risk"],
  PM: ["qr_signature_mismatch", "payload_tampering_score", "merchant_geo_mismatch", "amount_deviation", "channel_risk", "device_risk"],
  TB: ["inter_arrival_velocity", "micro_amount_clustering", "bot_subnet_entropy", "amount_deviation", "channel_risk", "device_risk"],
  MRF: ["prompt_injection_score", "unverified_refund_ratio", "merchant_dispute_anomaly", "amount_deviation", "channel_risk", "device_risk"],
  MM: ["fan_out_degree", "fan_in_degree", "transit_velocity_sec", "amount_layering_ratio", "shared_device_cluster", "account_dormancy_score"],
  GENAI: ["llm_semantic_intent_score", "voice_biometric_jitter", "synthetic_face_embedding_dist", "adversarial_perturbation_index", "device_risk", "amount_deviation"],
};

export function generateRandomTransaction(index = 1, attackRatio = 25, evasion = 20) {
  const isAttack = Math.random() * 100 < attackRatio;
  const randHex = Math.random().toString(16).substring(2, 7).toUpperCase();

  if (!isAttack) {
    const category = CATEGORIES[Math.floor(Math.random() * 6)];
    let amount = LEGIT_AMOUNTS[Math.floor(Math.random() * LEGIT_AMOUNTS.length)];
    if (category === "wire_transfer") {
      amount = +(Math.random() * 3000 + 400).toFixed(2);
    }

    const fraudProb = +(Math.random() * 8.5 + 1.2).toFixed(1);
    return {
      id: `TXN-${randHex}`,
      index,
      amount,
      category,
      isAttack: false,
      attackVector: "LEGIT",
      attackName: "Normal Verified Activity",
      fraudProb: +fraudProb,
      decision: "APPROVE",
      matrixTag: "TN",
      timestamp: new Date().toISOString(),
      displayDate: new Date().toLocaleTimeString(),
      features: [
        { name: "device_risk", value: 0.08, contribution: -1.2 },
        { name: "amount_deviation", value: 0.10, contribution: -0.8 },
        { name: "velocity", value: 0.12, contribution: -0.6 },
        { name: "channel_risk", value: 0.05, contribution: -0.4 },
      ],
      explanation: "Transaction exhibits standard legitimate behavioral patterns. Multi-modal biometrics and velocity are consistent with historical baseline."
    };
  }

  // Attack transaction across 22 vectors
  const vector = ATTACK_VECTORS[Math.floor(Math.random() * ATTACK_VECTORS.length)];
  const catCode = vector.category || "ATO";
  const sigNames = CATEGORY_SIGNALS[catCode] || CATEGORY_SIGNALS.ATO;

  let amount = 0;
  if (catCode === "MM" || catCode === "SOC") {
    amount = +(Math.random() * 25000 + 5000).toFixed(2);
  } else if (catCode === "TB") {
    amount = +(Math.random() * 2.50 + 0.50).toFixed(2);
  } else if (catCode === "GENAI") {
    amount = +(Math.random() * 15000 + 3500).toFixed(2);
  } else {
    amount = +(Math.random() * 4500 + 600).toFixed(2);
  }

  const evasionFactor = evasion / 100;
  let baseScore = 0.94 - (evasionFactor * 0.15);
  const fraudProb = +(baseScore * 100).toFixed(1);

  const action = fraudProb >= 80 ? "BLOCK" : (fraudProb >= 50 ? "HOLD_AND_VERIFY" : "STEP_UP_AUTH");
  const matrixTag = fraudProb >= 50 ? "TP" : "FN";

  return {
    id: `${catCode}-${randHex}`,
    index,
    amount,
    category: catCode === "PM" ? "qr_merchant_payment" : (catCode === "TB" ? "carding_micro_auth" : (catCode === "MRF" ? "refund_credit" : (catCode === "MM" ? "mule_transfer" : "online_retail"))),
    isAttack: true,
    attackVector: vector.id,
    attackName: vector.name,
    fraudProb: +fraudProb,
    decision: action,
    matrixTag,
    timestamp: new Date().toISOString(),
    displayDate: new Date().toLocaleTimeString(),
    features: [
      { name: sigNames[0], value: 0.95, contribution: 3.85 },
      { name: sigNames[1], value: 0.90, contribution: 2.92 },
      { name: sigNames[2], value: 0.85, contribution: 2.45 },
      { name: sigNames[3], value: 0.70, contribution: 1.80 },
    ],
    explanation: `CRITICAL: ${vector.name} detected by 10,000-D ${catCode} HDC defense prototype.`
  };
}

export function generateInitialBatch(size = 15) {
  const batch = [];
  for (let i = 1; i <= size; i++) {
    batch.push(generateRandomTransaction(i, 40, 20));
  }
  return batch;
}
