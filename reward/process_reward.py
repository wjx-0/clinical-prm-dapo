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

EXCLUSION_MARKERS = (
    "rules out",
    "ruled out",
    "less likely",
    "unlikely",
    "not consistent",
    "does not",
    "cannot",
    "would not",
    "incorrect because",
    "wrong because",
    "exclude",
    "against",
)

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


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


def differential_coverage_score(think: str, response: str, extra_info: Any) -> float:
    """Score whether the reasoning considers and eliminates distractor options."""
    if not isinstance(extra_info, dict):
        return 0.0
    options = extra_info.get("options")
    if not isinstance(options, dict):
        return 0.0

    final_answer = extract_answer_letter(response, loose=False)
    distractors = [k for k in options if k != final_answer]
    if not distractors:
        return 0.0

    think_lower = think.lower()
    mentioned = sum(1 for k in distractors if k.lower() in think_lower or clean_text(options[k]).lower()[:20] in think_lower)
    mention_score = clamp(mentioned / len(distractors))

    has_exclusion = any(marker in think_lower for marker in EXCLUSION_MARKERS)
    return clamp(0.6 * mention_score + 0.4 * float(has_exclusion))


def medical_keyword_overlap_score(think: str, extra_info: Any) -> float:
    """Score keyword overlap between reasoning and the question stem."""
    if not isinstance(extra_info, dict):
        return 0.0
    question = clean_text(extra_info.get("question", ""))
    if not question:
        return 0.0
    q_keywords = extract_keywords(question, min_len=4)
    if not q_keywords:
        return 0.0
    t_keywords = extract_keywords(think, min_len=4)
    overlap = len(q_keywords & t_keywords)
    # reward grows quickly but caps at 1.0 around 4+ shared keywords
    return clamp(overlap / max(4, len(q_keywords) * 0.4))


def step_structure_score(think: str) -> float:
    """Score whether reasoning has multiple distinct sentences (stepwise)."""
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(think) if len(s.strip()) > 20]
    count = len(sentences)
    if count <= 1:
        return 0.2
    if count == 2:
        return 0.5
    if count == 3:
        return 0.75
    return 1.0


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

    diff_score = differential_coverage_score(think, text, extra_info)
    kw_score = medical_keyword_overlap_score(think, extra_info)
    step_score = step_structure_score(think)

    score = (
        0.25 * length_score
        + 0.15 * marker_score
        + 0.20 * support_score
        + 0.20 * diff_score
        + 0.10 * kw_score
        + 0.10 * step_score
    )
    if generic_penalty:
        score -= min(0.35, 0.15 * generic_penalty)
    return clamp(score)
