// attacksData.js — Master 7-Category Attack Taxonomy (22 Variants)
// Generated directly from tanishq/identify/attacks.json

export const ATTACK_CATEGORIES = [
  "ALL",
  "ATO",
  "MM",
  "GENAI",
  "SOC",
  "PM",
  "TB",
  "MRF"
];

export const ATTACK_VECTORS = [
  {
    "id": "ATO-V1",
    "name": "High-Value New Device Takeover",
    "category": "ATO",
    "category_name": "Account Takeover",
    "severity": "CRITICAL",
    "color": "#ff334b",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Classic high-risk ATO: attacker logs in from an unknown device, sends a large payment to a new beneficiary. Easiest to detect but also the most damaging if missed.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 High-Value New Device Takeover.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary ATO telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "ATO-V2",
    "name": "Velocity Burst from Known Device",
    "category": "ATO",
    "category_name": "Account Takeover",
    "severity": "HIGH",
    "color": "#f59e0b",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Attacker uses a device the victim has used before (e.g., compromised via malware). Sends multiple rapid payments to new beneficiaries. The known device makes it trickier.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Velocity Burst from Known Device.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary ATO telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "ATO-V3",
    "name": "Off-Hours Location Shift",
    "category": "ATO",
    "category_name": "Account Takeover",
    "severity": "HIGH",
    "color": "#00e5ff",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Attacker logs in from a new location at an unusual time but keeps transaction amounts normal. Tries to fly under the radar by not being greedy.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Off-Hours Location Shift.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary ATO telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "ATO-V4",
    "name": "Subtle Amount Deviation (Stealth Mode)",
    "category": "ATO",
    "category_name": "Account Takeover",
    "severity": "HIGH",
    "color": "#b388ff",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "The sneakiest variant. Attacker uses a known device, pays a known beneficiary, but slightly increases the amount. Almost indistinguishable from legitimate activity.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Subtle Amount Deviation (Stealth Mode).",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary ATO telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "ATO-V5",
    "name": "Multi-Signal Low-Intensity",
    "category": "ATO",
    "category_name": "Account Takeover",
    "severity": "HIGH",
    "color": "#00e676",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Multiple signals fire but all at low intensity. No single signal is alarming on its own, but the combination should raise suspicion. Tests the system's ability to correlate weak signals.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Multi-Signal Low-Intensity.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary ATO telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "MM-V1",
    "name": "Rapid Cash-Out Burst",
    "category": "MM",
    "category_name": "Money Movement & Mule Networks",
    "severity": "CRITICAL",
    "color": "#ff1744",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Immediate high-velocity outflow: stolen funds are wired or cashed out within seconds of arriving at destination.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Rapid Cash-Out Burst.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary MM telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "MM-V2",
    "name": "Smurfing / Layered Fan-Out",
    "category": "MM",
    "category_name": "Money Movement & Mule Networks",
    "severity": "HIGH",
    "color": "#ff9100",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Attacker splits $10,000+ stolen lump sums into 10-15 micro-transfers to distinct mule accounts to bypass single-transaction AML limits.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Smurfing / Layered Fan-Out.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary MM telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "MM-V3",
    "name": "Fan-In Consolidation Ring",
    "category": "MM",
    "category_name": "Money Movement & Mule Networks",
    "severity": "HIGH",
    "color": "#00e5ff",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Multiple intermediate mule accounts funnel their micro-balances into a single aggregator wallet or crypto off-ramp.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Fan-In Consolidation Ring.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary MM telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "MM-V4",
    "name": "Dormant Mule Ring Activation",
    "category": "MM",
    "category_name": "Money Movement & Mule Networks",
    "severity": "HIGH",
    "color": "#d500f9",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Aged bank accounts that sat dormant for 6+ months suddenly wake up and route high-value layered transfers.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Dormant Mule Ring Activation.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary MM telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "GENAI-V1",
    "name": "Conversational Fraud Agent",
    "category": "GENAI",
    "category_name": "GenAI-Native & Emerging Fraud",
    "severity": "CRITICAL",
    "color": "#ff007f",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Autonomous LLM bot ingesting victim social feeds to execute real-time conversational social engineering on support channels.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Conversational Fraud Agent.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary GENAI telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "GENAI-V2",
    "name": "Deepfake Voice / Video Authorization",
    "category": "GENAI",
    "category_name": "GenAI-Native & Emerging Fraud",
    "severity": "CRITICAL",
    "color": "#7928ca",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Attacker clones CFO/vendor voice to call treasury and push an urgent high-value wire authorization.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Deepfake Voice / Video Authorization.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary GENAI telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "GENAI-V3",
    "name": "Synthetic Identity (GenAI KYC Bypass)",
    "category": "GENAI",
    "category_name": "GenAI-Native & Emerging Fraud",
    "severity": "HIGH",
    "color": "#0070f3",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "AI combines real SSN fragments with diffusion-generated portraits and synthetic credit histories.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Synthetic Identity (GenAI KYC Bypass).",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary GENAI telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "GENAI-V4",
    "name": "Adaptive Adversarial Feature Evasion",
    "category": "GENAI",
    "category_name": "GenAI-Native & Emerging Fraud",
    "severity": "HIGH",
    "color": "#50e3c2",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Black-box optimizer tweaks payment features (amounts just below threshold, off-hour timing) to evade fraud detectors.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Adaptive Adversarial Feature Evasion.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary GENAI telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "SOC-V1",
    "name": "AI Spear-Phishing Invoice Fraud",
    "category": "SOC",
    "category_name": "Social Engineering & AI Impersonation",
    "severity": "CRITICAL",
    "color": "#ff5252",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Hyper-personalized email matching vendor templates urging immediate wire payment.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 AI Spear-Phishing Invoice Fraud.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary SOC telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "SOC-V2",
    "name": "Deepfake Voice Pretexting (Vishing)",
    "category": "SOC",
    "category_name": "Social Engineering & AI Impersonation",
    "severity": "CRITICAL",
    "color": "#ff7043",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Cloned executive voice calling accountant to authorize emergency supplier payment.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Deepfake Voice Pretexting (Vishing).",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary SOC telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "SOC-V3",
    "name": "Smishing / OTP Interception Pretexting",
    "category": "SOC",
    "category_name": "Social Engineering & AI Impersonation",
    "severity": "HIGH",
    "color": "#ffa726",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "SMS alert claiming card compromised, tricking user into providing one-time passcode.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Smishing / OTP Interception Pretexting.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary SOC telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "PM-V1",
    "name": "Dynamic QR Code Redirection",
    "category": "PM",
    "category_name": "Payment Manipulation & QR Tampering",
    "severity": "CRITICAL",
    "color": "#26c6da",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Overlaid malicious QR code pointing to attacker crypto/P2P account instead of merchant.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Dynamic QR Code Redirection.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary PM telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "PM-V2",
    "name": "API Amount & Currency Parameter Tampering",
    "category": "PM",
    "category_name": "Payment Manipulation & QR Tampering",
    "severity": "HIGH",
    "color": "#29b6f6",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Manipulating client-side HTTP request to change currency from USD to JPY while keeping amount number.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 API Amount & Currency Parameter Tampering.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary PM telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "TB-V1",
    "name": "High-Frequency Carding Botnet",
    "category": "TB",
    "category_name": "Transaction Behaviour & Velocity Abuse",
    "severity": "CRITICAL",
    "color": "#ab47bc",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Automated script running 500 card validations per minute with $1.00 donation charges.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 High-Frequency Carding Botnet.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary TB telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "TB-V2",
    "name": "Coordinated Multi-Account Burst",
    "category": "TB",
    "category_name": "Transaction Behaviour & Velocity Abuse",
    "severity": "HIGH",
    "color": "#7e57c2",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Simultaneous withdrawals across 20 accounts from the same ATM geolocation cluster.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Coordinated Multi-Account Burst.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary TB telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  },
  {
    "id": "MRF-V1",
    "name": "Support Chatbot Refund Jailbreak",
    "category": "MRF",
    "category_name": "Merchant & Refund Manipulation",
    "severity": "CRITICAL",
    "color": "#ec407a",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Injecting prompt overrides into e-commerce chat agent to trigger automatic $500 refund credit.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Support Chatbot Refund Jailbreak.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary MRF telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.92
  },
  {
    "id": "MRF-V2",
    "name": "Ghost Merchant Transaction Laundering",
    "category": "MRF",
    "category_name": "Merchant & Refund Manipulation",
    "severity": "HIGH",
    "color": "#f06292",
    "channels": [
      "mobile_app",
      "web_portal",
      "api_gateway",
      "wire_rail"
    ],
    "rails": [
      "card_not_present",
      "instant_p2p",
      "ach_wire",
      "sepa_rtp"
    ],
    "signals": 6,
    "description": "Setting up fake online storefront to process stolen card payments under guise of retail sales.",
    "novelty": "Emerging 2026 adversarial variant with multi-signal evasion patterns.",
    "realWorldRef": "Mastercard Threat Taxonomy 2026 \u2014 Ghost Merchant Transaction Laundering.",
    "defensiveSignatures": [
      "Multi-signal anomaly on primary MRF telemetry",
      "HDC 10,000-D prototype cosine margin excursion",
      "Automated policy intervention threshold triggered"
    ],
    "defaultSelected": true,
    "risk_score": 0.85
  }
];

export const BENCHMARK_METRICS = {
  totalRows: 175392,
  categories: 7,
  variants: 22,
  inferenceLatencyMs: 0.84,
  modelSizeMB: 1.2
};
