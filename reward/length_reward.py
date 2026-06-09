"""Length and completion reward utilities."""

from __future__ import annotations

from typing import Any


def _length_config(config: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    section = config.get("length")
    return section if isinstance(section, dict) else {}


def _has_unclosed_tag(text: str, tag: str) -> bool:
    open_tag = f"<{tag}"
    close_tag = f"</{tag}>"
    lower = text.lower()
    return open_tag in lower and close_tag not in lower


def _looks_truncated(text: str) -> bool:
    stripped = text.strip()
    if stripped.endswith(("...", "<think>", "</think>", "<answer>")):
        return True
    return _has_unclosed_tag(stripped, "think") or _has_unclosed_tag(stripped, "answer")


def score_length(
    response: str,
    max_chars: int = 4096,
    *,
    min_chars: int = 80,
    target_chars: int = 160,
    soft_max_chars: int = 2200,
    config: dict[str, Any] | None = None,
) -> float:
    """Reward concise complete answers without giving a free constant bonus.

    The reward ramps up for very short outputs, stays high for normal medical
    reasoning, and decays once the response becomes verbose.
    """
    cfg = _length_config(config)
    max_chars = int(cfg.get("max_chars") or max_chars)
    min_chars = int(cfg.get("min_chars") or min_chars)
    target_chars = int(cfg.get("target_chars") or target_chars)
    soft_max_chars = int(cfg.get("soft_max_chars") or soft_max_chars)
    soft_max_chars = max(soft_max_chars, target_chars)

    text = str(response).strip()
    length = len(text)
    if length == 0 or length > max_chars or _looks_truncated(text):
        return 0.0
    if length < min_chars:
        return 0.2
    if length < target_chars:
        return max(0.2, length / max(target_chars, 1))
    if length <= soft_max_chars:
        return 1.0
    decay_span = max(max_chars - soft_max_chars, 1)
    return max(0.0, 1.0 - (length - soft_max_chars) / decay_span)
