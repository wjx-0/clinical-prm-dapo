"""Process reward model scoring adapter.

The adapter has two modes:

1. A lazy Hugging Face sequence-classification scorer when ``prm.model_path``
   or ``PRM_MODEL_PATH`` is configured.
2. A deterministic rule fallback that scores process structure, specificity,
   and support for the final option. This keeps GRPO smoke tests usable before
   the learned PRM checkpoint exists.
"""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from reward.answer_reward import extract_answer_letter
    from reward.format_reward import score_format
except ImportError:
    from answer_reward import extract_answer_letter
    from format_reward import score_format


DEFAULT_CONFIG_PATH = Path("configs/verl/reward_config.yaml")
THINK_RE = re.compile(r"<think>(.*?)</think>", re.IGNORECASE | re.DOTALL)
STEP_RE = re.compile(
    r"\bStep\s+(\d+)\s*:\s*(.*?)(?=\n\s*Step\s+\d+\s*:|\n\s*</think>|$)",
    re.IGNORECASE | re.DOTALL,
)
ANSWER_TAG_RE = re.compile(r"<answer>\s*[A-D]\s*</answer>", re.IGNORECASE | re.DOTALL)
GENERIC_PHRASES = (
    "the question stem is reviewed",
    "the selected choice",
    "the remaining choices",
    "best match",
    "given information",
    "appears to match",
    "without a specific",
)
DIRTY_PATTERNS = (
    r"&;",
    r"aEUR",
    r"\x00",
    r"([!?.,;:])\1{3,}",
    r"(?:\S+\s*\|\s*){3,}\S+",
)
STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "among",
    "answer",
    "because",
    "been",
    "being",
    "best",
    "between",
    "both",
    "cannot",
    "choice",
    "choices",
    "clinical",
    "common",
    "following",
    "from",
    "given",
    "have",
    "into",
    "likely",
    "most",
    "option",
    "patient",
    "patients",
    "question",
    "rather",
    "seen",
    "should",
    "such",
    "than",
    "that",
    "their",
    "there",
    "these",
    "this",
    "those",
    "through",
    "which",
    "while",
    "with",
    "would",
}

_SCORER: Any = None
_SCORER_ERROR: str | None = None


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@lru_cache(maxsize=4)
def load_reward_config(path: str | None = None) -> dict[str, Any]:
    config_path = Path(path or os.environ.get("REWARD_CONFIG_PATH") or DEFAULT_CONFIG_PATH)
    if not config_path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    with config_path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}
    return loaded if isinstance(loaded, dict) else {}


def env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def prompt_to_text(prompt: Any) -> str:
    if isinstance(prompt, str):
        return prompt
    if isinstance(prompt, list):
        chunks: list[str] = []
        for item in prompt:
            if isinstance(item, dict):
                chunks.append(clean_text(item.get("content")))
            else:
                chunks.append(clean_text(item))
        return "\n".join(chunk for chunk in chunks if chunk)
    return clean_text(prompt)


def think_content(response: str) -> str:
    match = THINK_RE.search(str(response))
    return match.group(1).strip() if match else ""


def extract_steps(response: str) -> list[str]:
    think = think_content(response)
    return [clean_text(match.group(2)) for match in STEP_RE.finditer(think)]


def step_numbers(response: str) -> list[int]:
    think = think_content(response)
    return [int(match.group(1)) for match in STEP_RE.finditer(think)]


def english_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", text))


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


def expected_step_bounds(extra_info: Any, response: str) -> tuple[int, int]:
    if isinstance(extra_info, dict):
        expected = clean_text(extra_info.get("expected_step_range"))
        match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", expected)
        if match:
            return int(match.group(1)), int(match.group(2))
        question_type = clean_text(extra_info.get("question_type")).lower()
        if question_type == "short_fact":
            return 2, 3
        if question_type == "clinical_vignette":
            return 4, 6
        question_chars = extra_info.get("question_chars")
        if isinstance(question_chars, int) and question_chars >= 450:
            return 4, 6

    # Without metadata, infer gently from response length so short fact answers
    # are not over-penalized.
    return (2, 6) if len(response) < 1200 else (3, 7)


def score_step_count(steps: list[str], bounds: tuple[int, int]) -> float:
    count = len(steps)
    low, high = bounds
    if count == 0:
        return 0.0
    if low <= count <= high:
        return 1.0
    distance = low - count if count < low else count - high
    return clamp(1.0 - 0.25 * distance)


def score_step_quality(response: str, steps: list[str]) -> float:
    if not steps:
        return 0.0
    numbers = step_numbers(response)
    sequential = numbers == list(range(1, len(numbers) + 1))
    length_scores = [clamp(english_word_count(step) / 10.0) for step in steps]
    generic_penalty = sum(
        1
        for step in steps
        if any(phrase in step.lower() for phrase in GENERIC_PHRASES)
    )
    base = sum(length_scores) / len(length_scores)
    if sequential:
        base = 0.85 * base + 0.15
    else:
        base *= 0.75
    if generic_penalty:
        base -= min(0.4, 0.15 * generic_penalty)
    return clamp(base)


def score_keyword_grounding(response: str, prompt: Any, extra_info: Any) -> float | None:
    source_text = ""
    if isinstance(extra_info, dict):
        options = extra_info.get("options")
        option_text = " ".join(clean_text(value) for value in options.values()) if isinstance(options, dict) else ""
        source_text = " ".join(
            clean_text(part)
            for part in (
                extra_info.get("question"),
                extra_info.get("answer_text"),
                option_text,
            )
            if part
        )
    if not source_text:
        source_text = prompt_to_text(prompt)

    keywords = extract_keywords(source_text)
    if len(keywords) < 3:
        return None
    response_keywords = extract_keywords(response)
    hits = len(keywords & response_keywords)
    required = 2 if len(keywords) >= 10 else 1
    return clamp(hits / max(required, 1))


def score_answer_support(response: str, extra_info: Any) -> float | None:
    answer_text = final_answer_text(response, extra_info)
    keywords = extract_keywords(answer_text, min_len=3)
    if not keywords:
        return None
    normalized_answer = clean_text(answer_text).lower()
    response_lower = clean_text(response).lower()
    if normalized_answer and normalized_answer in response_lower:
        return 1.0
    response_keywords = extract_keywords(response, min_len=3)
    required = 1 if len(keywords) <= 2 else max(1, len(keywords) // 2)
    return clamp(len(keywords & response_keywords) / required)


def score_cleanliness(response: str, max_chars: int) -> float:
    text = str(response)
    if len(text) > max_chars:
        return 0.0
    if any(re.search(pattern, text) for pattern in DIRTY_PATTERNS):
        return 0.0
    answer_tags = ANSWER_TAG_RE.findall(text)
    if len(answer_tags) != 1:
        return 0.3 if answer_tags else 0.0
    if text.strip().endswith("..."):
        return 0.4
    return 1.0


def rule_score_prm(
    response: str,
    *,
    prompt: Any = None,
    extra_info: Any = None,
    config: dict[str, Any] | None = None,
) -> float:
    config = config or {}
    prm_config = config.get("prm") if isinstance(config.get("prm"), dict) else {}
    max_chars = int(prm_config.get("max_chars") or 4096)
    text = str(response)
    steps = extract_steps(text)
    bounds = expected_step_bounds(extra_info, text)

    components: list[tuple[float, float]] = [
        (score_format(text), 0.18),
        (score_step_count(steps, bounds), 0.22),
        (score_step_quality(text, steps), 0.25),
        (score_cleanliness(text, max_chars), 0.12),
    ]

    grounding = score_keyword_grounding(text, prompt, extra_info)
    if grounding is not None:
        components.append((grounding, 0.11))

    support = score_answer_support(text, extra_info)
    if support is not None:
        components.append((support, 0.12))

    weight_sum = sum(weight for _, weight in components)
    if weight_sum <= 0:
        return 0.0
    return clamp(sum(score * weight for score, weight in components) / weight_sum)


def model_input_text(prompt: Any, response: str) -> str:
    prompt_text = prompt_to_text(prompt)
    if prompt_text:
        return f"{prompt_text}\n\nAssistant response:\n{response}"
    return str(response)


class HFSequenceScorer:
    def __init__(self, model_path: str, *, max_length: int = 4096) -> None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            trust_remote_code=True,
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()

    def score(self, prompt: Any, response: str) -> float:
        inputs = self.tokenizer(
            model_input_text(prompt, response),
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with self.torch.no_grad():
            logits = self.model(**inputs).logits[0].detach().float().cpu()
        if logits.numel() == 1:
            return float(self.torch.sigmoid(logits[0]).item())
        probs = self.torch.softmax(logits, dim=-1)
        return float(probs[-1].item())


def get_model_scorer(config: dict[str, Any]) -> Any:
    global _SCORER, _SCORER_ERROR
    prm_config = config.get("prm") if isinstance(config.get("prm"), dict) else {}
    model_path = os.environ.get("PRM_MODEL_PATH") or clean_text(prm_config.get("model_path"))
    use_model = env_flag("PRM_USE_MODEL", bool(prm_config.get("use_model", bool(model_path))))
    if not model_path or not use_model:
        return None
    if _SCORER is not None:
        return _SCORER
    if _SCORER_ERROR is not None:
        return None
    try:
        max_length = int(prm_config.get("max_model_length") or prm_config.get("max_chars") or 4096)
        _SCORER = HFSequenceScorer(model_path, max_length=max_length)
    except Exception as exc:  # noqa: BLE001 - reward fallback should keep training alive.
        _SCORER_ERROR = f"{type(exc).__name__}: {exc}"
        return None
    return _SCORER


def score_prm(
    response: str,
    *,
    prompt: Any = None,
    ground_truth: Any = None,
    extra_info: Any = None,
    config: dict[str, Any] | None = None,
) -> float:
    del ground_truth
    config = config or load_reward_config()
    scorer = get_model_scorer(config)
    if scorer is not None:
        try:
            score = scorer.score(prompt, response)
            if math.isfinite(score):
                return clamp(score)
        except Exception:  # noqa: BLE001 - fall through to rule PRM.
            pass
    return rule_score_prm(response, prompt=prompt, extra_info=extra_info, config=config)
