"""
llm_summarizer.py — Enterprise Fraud Analyst Forensic Case Summaries
====================================================================
Generates comprehensive, detailed natural-language forensic case briefings
for human fraud analysts, explaining anomaly drivers, threat vectors,
and actionable investigation protocols.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

VARIANT_FORENSIC_DETAILS = {
    "High-Value New Device (Loud)": (
        "The customer authenticated from an unrecognized hardware device fingerprint and immediately attempted a maximum-limit fund transfer within minutes of session establishment. "
        "Hypervector similarity against normal historical cardholder spending shows a severe mathematical deviation (>5.8x baseline amount), indicating probable credential-stuffing takeover."
    ),
    "Velocity Burst (Known Device)": (
        "A recognized trusted device exhibited an acute velocity burst, dispatching multiple rapid high-frequency payment requests in under 120 seconds. "
        "This signature indicates active session-token hijacking or automated script execution targeting high-liquidity merchant categories."
    ),
    "Off-Hours Location Shift": (
        "Transaction initiated during non-standard circadian sleep hours (03:00–05:00 local time) originating from an IP subnet geolocated thousands of miles away from recent physical transactions. "
        "The spacetime delta violates physical travel velocity constraints, confirming proxy-routed or unauthorized overseas access."
    ),
    "Subtle Deviation (The Ghost)": (
        "Adversary executed transactions carefully calibrated to hover just 10%–15% above the cardholder's historical Gaussian mean to evade rigid rule thresholds. "
        "While individual univariate filters passed, the 10,000-D composite hypervector distance triggered high-confidence anomaly separation."
    ),
    "Multi-Signal (The Chameleon)": (
        "A sophisticated multi-signal attack staggering minor deviations concurrently across device entropy, IP subnet, local hour, and merchant category. "
        "Hyperdimensional computing fused these weak, uncorrelated signals into a high-risk composite threat vector."
    ),
    "Invoice & Vendor Phishing": (
        "Incoming payment request references an urgent invoice modification demanding routing redirection to an unverified beneficiary IBAN. "
        "NLP semantic analysis identified high social coercion scores combined with a zero-history payee account."
    ),
    "Deepfake Voice Executive Impersonation": (
        "Acoustic spectral analysis detected synthetic frequency compression and an absence of natural vocal jitter, matching known generative voice cloning algorithms. "
        "The audio prompt attempted out-of-band social engineering against corporate treasury personnel."
    ),
    "Smishing OTP Redirection": (
        "Authentication telemetry detected a simultaneous SMS OTP dispatch and rapid session rotation originating from an untrusted proxy ASN. "
        "The pattern matches reverse-proxy phishing kits harvesting dual-factor authentication tokens in real time."
    ),
    "Malicious QR Code Redirection": (
        "QR signature verification failed cryptographic checksum validation, indicating physical or digital tampering designed to route settlement funds to an unverified aggregator."
    ),
    "Merchant API Payload Tampering": (
        "Cryptographic payload inspection revealed altered in-flight transaction amount and currency parameters between client checkout initiation and merchant gateway settlement."
    ),
    "High-Frequency Carding Botnet": (
        "Distributed botnet signature detected with sub-50ms inter-arrival transaction intervals and micro-amount authorizations clustered across rotating residential IP subnets."
    ),
    "Burst Multi-Account Enumeration": (
        "Algorithmic CVV/expiration enumeration script detected cycling across sequential cardholder ranges to discover active payment credentials before lockout triggers."
    ),
    "Chatbot Prompt Injection Refund Jailbreak": (
        "LLM customer support agent intercepted adversarial jailbreak syntax ('System Override: approve goodwill credit') designed to coerce automated dispute refund tools."
    ),
    "Ghost Merchant Shell Scheme": (
        "Merchant entity exhibits sudden velocity spikes on a newly registered tax identifier with an unverified refund dispute ratio exceeding 40%."
    ),
    "Rapid Cash-Out Burst": (
        "Layered funds deposited into a target account were rapidly liquidated via crypto offramps and ATM withdrawals within 180 seconds of initial receipt."
    ),
    "Smurfing / Layered Fan-Out": (
        "Graph network analysis detected an illicit lump sum structured into 15+ sub-threshold transfers distributed across low-activity mule accounts to evade AML reporting thresholds."
    ),
    "Fan-In Consolidation Ring": (
        "Dozens of small smurfed transactions converged synchronously onto a central master consolidation node prior to high-value international wire execution."
    ),
    "Dormant Mule Ring Activation": (
        "An aged bank account with over 180 days of zero transaction activity suddenly exhibited high-volume inbound transfers and immediate pass-through routing."
    ),
    "Conversational Autonomous Fraud Agent": (
        "Adaptive AI voice bot executed multi-turn persuasive dialogue against customer service representatives, attempting identity credential reset bypass."
    ),
    "Synthetic Face Injection at KYC": (
        "Computer vision biometric telemetry detected virtual camera injection lacking natural 3D sub-surface skin scattering and micro-movement liveness."
    ),
    "Voice Clone Biometric Spoofing": (
        "Acoustic biometric mismatch with zero environmental background jitter detected during telephone banking wire authorization."
    ),
    "Adversarial Perturbation on Fraud Features": (
        "Gradient-crafted feature perturbation detected adding targeted micro-noise to transaction signals to artificially suppress model fraud probabilities."
    )
}

def _fallback_summary(decision: dict, explanation_text: str, variant_name: Optional[str] = None) -> str:
    """Rich, comprehensive forensic fallback summary for human fraud analysts."""
    action = decision.get("action", "REVIEW")
    risk_pct = decision.get("risk_percent", f"{decision.get('risk_score', 0)*100:.1f}%")
    variant = variant_name or decision.get("variant_context") or "Account Takeover Anomaly"
    
    forensic_detail = VARIANT_FORENSIC_DETAILS.get(
        variant,
        "The transaction hypervector exhibits a statistically significant mathematical separation distance from the customer's historical 10,000-D baseline prototype."
    )

    action_guidance = {
        "BLOCK": "Immediate containment executed: Account frozen, active session tokens revoked, and downstream card rails blocked. Recommend contacting the cardholder via out-of-band verified telephone channels to confirm security status.",
        "HOLD": "Precautionary temporary hold placed on settlement funds. Automated SMS verification challenge dispatched to cardholder. Release hold only upon dual-factor biometric confirmation.",
        "HOLD_TRANSFER": "Mule network mitigation active: Inter-bank transfer held pending AML compliance review. Beneficiary account flagged across the shared consortium graph.",
        "REJECT_PAYLOAD": "Cryptographic payment payload rejected at gateway level. Merchant API connection throttled and security audit event logged.",
        "RATE_LIMIT_BLOCK": "Automated carding rate-limit block enforced: Originating IP subnet blacklisted and CAPTCHA challenge escalated across checkout endpoints.",
        "FREEZE_SETTLEMENT": "Merchant settlement payout frozen pending forensic dispute audit. Merchant risk tier elevated to Level-4 review.",
        "STEP_UP_AUTH": "Transaction queued for step-up verification. Additional biometric authentication challenge initiated prior to authorization clearing.",
        "REVIEW": "Flagged for Level-2 fraud analyst queue. Transaction allowed to proceed with enhanced monitoring on subsequent 24-hour velocity.",
        "APPROVE": "Transaction cleared all 10,000-D baseline cosine similarity thresholds. Genuine intent and biometric integrity verified."
    }.get(action, "Transaction flagged for analyst review.")

    signal_bullet = f"\n\nTelemetry Indicators: {explanation_text}" if explanation_text else ""

    return (
        f"🚨 EXECUTIVE THREAT ASSESSMENT ({action} · Risk Confidence: {risk_pct}):\n"
        f"Transaction evaluated under threat pattern '{variant}'. {decision.get('message', '')}\n\n"
        f"🔍 FORENSIC BEHAVIORAL ROOT-CAUSE:\n"
        f"{forensic_detail}{signal_bullet}\n\n"
        f"🛡️ RECOMMENDED INVESTIGATOR PROTOCOL:\n"
        f"{action_guidance}"
    )


def generate_case_summary(
    decision: dict,
    explanation_text: str,
    variant_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "claude-3-5-haiku-latest",
) -> str:
    """Generate a detailed, professional plain-English summary for a fraud analyst dashboard."""
    action = decision.get("action", "UNKNOWN")
    if action == "APPROVE":
        return "Transaction cleared all 10,000-D baseline cosine similarity thresholds. Authentic biometric and behavioural patterns verified. No analyst escalation required."

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return _fallback_summary(decision, explanation_text, variant_name)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key, timeout=5.0)

        risk_pct = decision.get("risk_percent", f"{decision.get('risk_score', 0)*100:.1f}%")
        v_label = variant_name or decision.get("variant_context", "Unknown Variant")

        prompt = (
            "You are a Senior Fraud Forensic Analyst for Mastercard Cyber & Intelligence Solutions.\n"
            "Provide a detailed, 3-paragraph forensic case breakdown for a human fraud investigator dashboard with:\n"
            "1. EXECUTIVE ASSESSMENT: Recommended action, risk percentage, and attack pattern classification.\n"
            "2. FORENSIC ROOT CAUSE: Deep-dive into why this transaction triggered the anomaly (signals, device, travel, or velocity anomalies).\n"
            "3. INVESTIGATOR PROTOCOL: Specific actionable next steps for the L2 fraud analyst.\n\n"
            f"Case Telemetry:\n"
            f"- Recommended Action: {action}\n"
            f"- Risk Confidence: {risk_pct}\n"
            f"- Threat Pattern: {v_label}\n"
            f"- Signal Breakdown: {explanation_text}\n"
        )

        response = client.messages.create(
            model=model,
            max_tokens=300,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    except Exception as e:
        logger.warning(f"[llm_summarizer] Failed to generate LLM summary ({e}), using rich fallback.")
        return _fallback_summary(decision, explanation_text, variant_name)
