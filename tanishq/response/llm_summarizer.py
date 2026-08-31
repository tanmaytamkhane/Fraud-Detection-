"""
llm_summarizer.py — LLM-Generated Fraud Analyst Case Summaries
==============================================================
Person 4 module for generating concise natural-language case summaries
for human fraud analysts on actionable decision tiers (REVIEW, STEP_UP_AUTH, HOLD, BLOCK).

Uses the Anthropic Python SDK with automatic fallback if the API key is not set
or if network/API errors occur.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _fallback_summary(decision: dict, explanation_text: str, variant_name: Optional[str] = None) -> str:
    """Deterministic, template-based fallback summary when LLM is unavailable."""
    action = decision.get("action", "REVIEW")
    risk_pct = decision.get("risk_percent", f"{decision.get('risk_score', 0)*100:.1f}%")
    variant = variant_name or decision.get("variant_context") or "suspected ATO anomaly"
    
    # Extract top reason lines from explanation if available
    reason_snippet = ""
    if explanation_text:
        bullet_lines = [
            line.strip().lstrip("•-* ").strip()
            for line in explanation_text.splitlines()
            if line.strip().startswith(("•", "-", "*")) or "unusual" in line.lower() or "new" in line.lower()
        ]
        if bullet_lines:
            reason_snippet = f" Key driver: {bullet_lines[0]}."

    return (
        f"Analyst Alert ({action}, Risk: {risk_pct}): Transaction flagged under pattern {variant}. "
        f"{decision.get('message', '')}{reason_snippet}"
    )


def generate_case_summary(
    decision: dict,
    explanation_text: str,
    variant_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "claude-3-5-haiku-latest",
) -> str:
    """
    Generate a 1-2 sentence plain-English summary for a fraud analyst dashboard.

    Args:
        decision: Decision dictionary from ResponseEngine.decide_action().
        explanation_text: Human-readable explanation text from ExplanationEngine.generate_text().
        variant_name: Optional descriptive variant name (e.g. "High-Value New Device (Loud)").
        api_key: Optional API key override; defaults to ANTHROPIC_API_KEY env var.
        model: Model identifier for Anthropic API.

    Returns:
        1-2 sentence case summary.
    """
    action = decision.get("action", "UNKNOWN")
    # Skip generation for APPROVE
    if action == "APPROVE":
        return "Transaction approved. No analyst escalation required."

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return _fallback_summary(decision, explanation_text, variant_name)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key, timeout=5.0)

        risk_pct = decision.get("risk_percent", f"{decision.get('risk_score', 0)*100:.1f}%")
        v_label = variant_name or decision.get("variant_context", "Unknown Variant")

        prompt = (
            "You are an expert fraud analyst system. Provide a concise 1-2 sentence summary of this transaction case for a fraud analyst dashboard.\n\n"
            f"Case details:\n"
            f"- Transaction ID: {decision.get('transaction_id', 'N/A')}\n"
            f"- Recommended Action: {action}\n"
            f"- Risk Score: {risk_pct}\n"
            f"- Suspected Attack Variant: {v_label}\n"
            f"- Signal Breakdown / Reasons:\n{explanation_text}\n\n"
            "Summary requirement: Exactly 1 to 2 clear, professional sentences explaining why the action was recommended and what the primary anomaly is."
        )

        response = client.messages.create(
            model=model,
            max_tokens=150,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text.strip()
        return content

    except Exception as e:
        logger.warning(f"[llm_summarizer] Failed to generate LLM summary ({e}), using fallback.")
        return _fallback_summary(decision, explanation_text, variant_name)
