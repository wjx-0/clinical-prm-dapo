"""Format reward utilities for reasoning responses."""

from __future__ import annotations

import re

FULL_FORMAT_RE = re.compile(
    r"^\s*<think>.+?</think>\s*<answer>\s*[A-D]\s*</answer>\s*$",
    re.IGNORECASE | re.DOTALL,
)
ANSWER_TAG_RE = re.compile(r"<answer>\s*[A-D]\s*</answer>", re.IGNORECASE | re.DOTALL)


def score_format(response: str) -> float:
    text = str(response)
    if FULL_FORMAT_RE.match(text):
        return 1.0

    # Partial credit keeps early GRPO from being too sparse while still
    # preferring the full reasoning + final-answer contract.
    score = 0.0
    if "<think>" in text and "</think>" in text:
        score += 0.4
    if ANSWER_TAG_RE.search(text):
        score += 0.6
    return min(score, 1.0)
