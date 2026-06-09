"""Rule-based reasoning-process reward utilities."""

from __future__ import annotations

import re
from typing import Any

try:
    from reward.answer_reward import extract_answer_letter
except ImportError:
    from answer_reward import extract_answer_letter


THINK_RE = re.compile(r"<think>(.*?)</think>", re.IGNORECASE | re.DOTALL)
WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)?")
DIRTY_PATTERNS = (
    r"&;",
    r"aEUR",
    r"\x00",
    r"([!?.,;:])\1{3,}",
)
REASONING_MARKERS = (
    "because",
    "therefore",
    "thus",
    "so ",
    "consistent with",
    "suggests",
    "indicates",
    "rules out",
    "less likely",
    "most likely",
)
GENERIC_PHRASES = (
    "the question stem is reviewed",
    "the selected choice",
    "the remaining choices",
    "best match",
    "given information",
    "appears to match",
    "without a specific",
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


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def think_content(response: str) -> str:
    match = THINK_RE.search(str(response))
    return match.group(1).strip() if match else ""


def english_word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def extract_keywords(text: Any, *, min_len: int = 4) -> set[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+-]*", clean_text(text).lower())
    return {word for word in words if len(word) >= min_len and word not in STOPWORDS}


def final_answer_text(response: str, extra_info: Any) -> str:
    final_answer = extract_answer_letter(response, loose=False)
    if not final_answer or not isinstance(extra_info, dict):
        return ""
    options = extra_info.get("options")
    if isinstance(options, dict):
        return clean_text(options.get(final_answer))
    return clean_text(extra_info.get("answer_text"))


def answer_support_score(think: str, response: str, extra_info: Any) -> float:
    answer_text = final_answer_text(response, extra_info)
    answer_keywords = extract_keywords(answer_text, min_len=3)
    if not answer_keywords:
        return 0.0

    normalized_answer = clean_text(answer_text).lower()
    think_lower = clean_text(think).lower()
    if normalized_answer and normalized_answer in think_lower:
        return 1.0

    think_keywords = extract_keywords(think, min_len=3)
    required = 1 if len(answer_keywords) <= 2 else max(1, len(answer_keywords) // 2)
    return clamp(len(answer_keywords & think_keywords) / required)


def score_process(response: str, extra_info: Any = None) -> float:
    """Score whether the response contains useful, grounded reasoning.

    This is intentionally correctness-agnostic. The answer reward owns gold
    matching; this component only gives a small auxiliary signal for a complete
    reasoning process that supports the model's own final answer.
    """
    text = str(response)
    think = think_content(text)
    if not think:
        return 0.0
    if any(re.search(pattern, text) for pattern in DIRTY_PATTERNS):
        return 0.0

    word_count = english_word_count(think)
    if word_count < 8:
        length_score = 0.0
    elif word_count < 14:
        length_score = 0.45
    elif word_count < 28:
        length_score = 0.80
    else:
        length_score = 1.0

    marker_score = 1.0 if any(marker in think.lower() for marker in REASONING_MARKERS) else 0.4
    support_score = answer_support_score(think, text, extra_info)
    generic_penalty = sum(1 for phrase in GENERIC_PHRASES if phrase in think.lower())

    score = 0.45 * length_score + 0.25 * marker_score + 0.30 * support_score
    if generic_penalty:
        score -= min(0.35, 0.15 * generic_penalty)
    return clamp(score)
