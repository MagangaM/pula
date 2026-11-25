"""Groq chat-completions adapter with cautious deterministic fallback."""
from .engine import template_advisory, sms_valid
from .config import get_secret


def generate(crop, ward, stage, risk, language, evidence_note="No verified crop-specific source is attached. Monitoring-only guidance.", weather=None):
    """Generate a short advisory with Groq; safely fall back to a template."""
    fallback = template_advisory(crop, ward, stage, risk, language)
    key = get_secret("GROQ_API_KEY")
    model = get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")
    if not key:
        return {"text": fallback, "mode": "template-fallback", "model": None, "grounding": evidence_note}

    weather = weather or {}
    prompt = (
        f"Write one cautious farmer advisory in {language}. Crop={crop}; ward={ward}; "
        f"growth stage={stage}; monitoring signal={risk}. Weather data: {weather}. "
        f"Evidence note: {evidence_note}. Use only supplied facts. Do not invent thresholds, "
        "diagnoses, pesticide/fertilizer doses, citations, or guarantees. If evidence is "
        "insufficient, advise observation and contacting a local agricultural extension officer. "
        "Keep it short, plain and suitable for an SMS. Return only the message."
    )
    try:
        from groq import Groq
        client = Groq(api_key=key, timeout=12, max_retries=1)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You provide cautious, evidence-grounded agricultural information. Never invent facts."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=120,
        )
        text = (response.choices[0].message.content or "").strip()
        ok, reason = sms_valid(text)
        if not ok:
            return {"text": fallback, "mode": "fallback-validation", "model": model, "grounding": evidence_note, "reason": reason}
        return {"text": text, "mode": "groq-chat-completions", "model": model, "grounding": evidence_note}
    except Exception as exc:
        return {"text": fallback, "mode": "fallback-provider-error", "model": model, "grounding": evidence_note, "reason": type(exc).__name__}
