"""Final-answer reward utilities."""

from __future__ import annotations

import re
from typing import Any

ANSWER_TAG_RE = re.compile(r"<answer>\s*([A-D])\s*</answer>", re.IGNORECASE | re.DOTALL)
LOOSE_ANSWER_RE = re.compile(
    r"(?:final\s+answer|answer|答案|选项|选择)\s*(?:is|是|:|：)?\s*([A-D])\b",
    re.IGNORECASE,
)
STANDALONE_LETTER_RE = re.compile(r"\b([A-D])\b", re.IGNORECASE)


def normalize_gold(gold: Any) -> str:
    """Return the A-D gold label from verl reward payloads."""
    if isinstance(gold, dict):
        gold = gold.get("ground_truth") or gold.get("answer") or gold.get("label") or ""
    text = str(gold).strip().upper()
    match = STANDALONE_LETTER_RE.search(text)
    return match.group(1).upper() if match else ""


def extract_answer_letter(response: str, *, loose: bool = True) -> str:
    """Extract the final A-D answer from a model response.

    The strict path prefers the last explicit <answer>X</answer> tag. The loose
    fallback is intentionally conservative and exists mainly for early smoke
    tests before the policy fully obeys the format.
    """
    text = str(response)
    tagged = ANSWER_TAG_RE.findall(text)
    if tagged:
        return tagged[-1].upper()

    if not loose:
        return ""

    loose_matches = LOOSE_ANSWER_RE.findall(text)
    if loose_matches:
        return loose_matches[-1].upper()

    tail = text[-80:]
    standalone = STANDALONE_LETTER_RE.findall(tail)
    return standalone[-1].upper() if standalone else ""


def score_answer(prediction: str, gold: Any, *, loose: bool = False) -> float:
    pred = extract_answer_letter(prediction, loose=loose)
    gold_label = normalize_gold(gold)
    return 1.0 if pred and gold_label and pred == gold_label else 0.0
