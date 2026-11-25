"""Deterministic prototype decision engine. Risk indicators are demonstration-only, not validated agronomic models."""
from dataclasses import dataclass
from typing import List

GSM_BASIC = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
GSM_EXT = set("^{}\\[~]|€")

@dataclass
class RiskSignal:
    crop: str
    risk: str
    drivers: List[str]
    caveat: str = "Prototype indicator only; not a diagnosis or validated threshold model."


def gsm7_safe(text: str) -> bool:
    return all(ch in GSM_BASIC or ch in GSM_EXT for ch in text)


def sms_valid(text: str, max_chars: int = 160) -> tuple[bool, str]:
    if not text.strip(): return False, "Message is empty."
    if not gsm7_safe(text): return False, "Message includes characters outside GSM-7."
    septets = sum(2 if ch in GSM_EXT else 1 for ch in text)
    if septets > max_chars: return False, f"Message uses {septets} GSM-7 septets; limit is {max_chars}."
    return True, "OK"


def risk_signals(crop: str, stage: str, weather: dict, flags: dict) -> list[RiskSignal]:
    """Simple demo flags, deliberately not sourced threshold models."""
    signals = []
    if crop == "Maize" and stage.lower() in {"tasseling", "silking", "flowering"} and flags.get("water_stress", False):
        signals.append(RiskSignal(crop, "Water-stress monitoring near flowering", ["Farmer-selected flowering stage", "Farmer-reported water-stress concern"]))
    if crop == "Tomatoes" and flags.get("wet_conditions", False):
        signals.append(RiskSignal(crop, "Wet-weather disease monitoring", ["Farmer-selected wet conditions", "Potentially conducive weather; confirm with local guidance"]))
    if crop == "Onions" and flags.get("wet_conditions", False):
        signals.append(RiskSignal(crop, "Wet-weather disease monitoring", ["Farmer-selected wet conditions", "Potentially conducive weather; confirm with local guidance"]))
    if not signals:
        signals.append(RiskSignal(crop, "Routine monitoring", ["No prototype risk flag selected or activated"]))
    return signals


def template_advisory(crop: str, ward: str, stage: str, risk: str, language: str) -> str:
    if language == "Swahili":
        return f"{ward}: {crop}, hatua {stage}. {risk}. Kagua shamba na thibitisha ushauri kwa afisa ugani."
    return f"{ward}: {crop}, stage {stage}. {risk}. Check your plot and confirm guidance with an extension officer."
