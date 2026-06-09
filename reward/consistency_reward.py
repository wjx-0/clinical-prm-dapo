"""Reasoning-answer consistency reward utilities."""

from __future__ import annotations

import re
from typing import Any

try:
    from reward.answer_reward import extract_answer_letter
except ImportError:
    from answer_reward import extract_answer_letter


THINK_RE = re.compile(r"<think>(.*?)</think>", re.IGNORECASE | re.DOTALL)
ANSWER_TAG_RE = re.compile(r"<answer>\s*([A-D])\s*</answer>", re.IGNORECASE | re.DOTALL)
EXPLICIT_ANSWER_PATTERNS = (
    r"(?:best|final|correct)\s+(?:answer|choice)\s+(?:is|:)\s*([A-D])\b",
    r"(?:answer|choice)\s+(?:is|:)\s*([A-D])\b",
    r"\boption\s+([A-D])\s+(?:is|as)\s+(?:the\s+)?(?:best|correct|final)\b",
    r"\b([A-D])\s+is\s+(?:the\s+)?(?:best|correct|final)\s+(?:answer|choice)\b",
)
STOPWORDS = {
    "about",
    "after",
    "also",
    "answer",
    "because",
    "best",
    "choice",
    "clinical",
    "following",
    "from",
    "given",
    "most",
    "option",
    "patient",
    "question",
    "that",
    "the",
    "this",
    "with",
}


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def think_content(response: str) -> str:
    match = THINK_RE.search(str(response))
    return match.group(1).strip() if match else ""


def explicit_answer_mentions(text: str) -> list[str]:
    mentions: list[str] = []
    for pattern in EXPLICIT_ANSWER_PATTERNS:
        mentions.extend(
            match.upper() for match in re.findall(pattern, text, flags=re.IGNORECASE)
        )
    return mentions


def extract_keywords(text: Any, *, min_len: int = 4) -> set[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+-]*", clean_text(text).lower())
    return {word for word in words if len(word) >= min_len and word not in STOPWORDS}


def final_answer_text(final_answer: str, extra_info: Any) -> str:
    if not isinstance(extra_info, dict) or final_answer not in {"A", "B", "C", "D"}:
        return ""
    options = extra_info.get("options")
    if isinstance(options, dict):
        return clean_text(options.get(final_answer))
    return clean_text(extra_info.get("answer_text"))


def answer_text_supported(response: str, answer_text: str) -> bool | None:
    keywords = extract_keywords(answer_text, min_len=3)
    if not keywords:
        return None
    text = clean_text(response).lower()
    normalized_answer = clean_text(answer_text).lower()
    if normalized_answer and normalized_answer in text:
        return True
    response_keywords = extract_keywords(response, min_len=3)
    required = 1 if len(keywords) <= 2 else max(1, len(keywords) // 2)
    return len(keywords & response_keywords) >= required


def score_consistency(response: str, extra_info: Any = None) -> float:
    """Score whether reasoning and final answer point to the same option.

    This component intentionally avoids checking correctness against gold; the
    final-answer reward owns that. Here we reward internal agreement and, when
    available, textual support for the final option.
    """
    text = str(response)
    final_answer = extract_answer_letter(text, loose=False)
    if not final_answer:
        return 0.0

    tagged_answers = [match.upper() for match in ANSWER_TAG_RE.findall(text)]
    if len(set(tagged_answers)) > 1:
        return 0.0

    think = think_content(text)
    if not think:
        return 0.25

    mentions = explicit_answer_mentions(think)
    if mentions:
        unique_mentions = set(mentions)
        if final_answer not in unique_mentions:
            return 0.1
        if len(unique_mentions) > 1:
            return 0.35

    support = answer_text_supported(think, final_answer_text(final_answer, extra_info))
    if support is False:
        return 0.55

    return 1.0
