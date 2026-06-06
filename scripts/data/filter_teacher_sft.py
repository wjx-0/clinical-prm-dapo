"""Strictly filter raw teacher-generated SFT data into final SFT JSONL."""

from __future__ import annotations

import argparse
import difflib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
REQUIRED_FIELDS = ("instruction", "input", "output", "answer")
STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "among",
    "because",
    "been",
    "being",
    "best",
    "between",
    "both",
    "cannot",
    "characteristic",
    "choice",
    "choices",
    "clinical",
    "common",
    "following",
    "from",
    "have",
    "into",
    "most",
    "patient",
    "patients",
    "question",
    "rather",
    "seen",
    "should",
    "shows",
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
    "within",
    "would",
}
FORBIDDEN_PHRASES = (
    "gold answer",
    "provided answer",
    "provided explanation",
    "correct option is given",
    "according to the provided",
    "I was given",
    "Ans.",
    "Ans:",
    "Answer:",
    "quality_tier",
    "question_type",
    "metadata",
    "supervised fine-tuning",
    "training-quality",
    "data generation",
    "The central reasoning point is",
    "This is supported by the related detail",
    "Recognize this as a medical multiple-choice question",
    "is 'a' i.e.",
    "is 'b' i.e.",
    "is 'c' i.e.",
    "is 'd' i.e.",
)
GENERIC_TEMPLATE_PHRASES = (
    "the question stem is reviewed",
    "the selected choice corresponds to",
    "the remaining choices are treated as less appropriate",
    "the answer option that should be supported by the reasoning",
)
MEDICAL_SIGNAL_WORDS = {
    "acid",
    "activity",
    "anemia",
    "antibody",
    "artery",
    "bacteria",
    "blood",
    "bone",
    "cancer",
    "cell",
    "cells",
    "deficiency",
    "diagnosis",
    "disease",
    "drug",
    "enzyme",
    "fever",
    "gene",
    "hormone",
    "infection",
    "inhibits",
    "lesion",
    "liver",
    "muscle",
    "nerve",
    "protein",
    "receptor",
    "renal",
    "syndrome",
    "therapy",
    "treatment",
    "tumor",
    "virus",
}
STEP_RE = re.compile(
    r"\bStep\s+(\d+)\s*:\s*(.*?)(?=\n\s*Step\s+\d+\s*:|\n\s*</think>|$)",
    flags=re.IGNORECASE | re.DOTALL,
)
ANSWER_TAG_RE = re.compile(r"<answer>\s*([^<]+?)\s*</answer>", flags=re.IGNORECASE)
THINK_RE = re.compile(r"<think>(.*?)</think>", flags=re.IGNORECASE | re.DOTALL)
SOURCE_NOISE_RE = re.compile(
    r"\b("
    r"depament|shoness|spos|hea\s+rate|uicaria|aery|investigadon|"
    r"ahritis|ahrh?algia|coicosteroid|aspaate|impairement|"
    r"gestaut|jang syndrome|sta\s+iv|sta\s+magnesium|staed|"
    r"ours\s+a\s+diagnosis|c6h12o|pneunocystis|hypeension|hypeensive|"
    r"hypehyroidism|polyaeritis|chlordiazepozide|tetra\s+cyclic|"
    r"eliminatined|spos-\s*related|sholy|repos|sho\s+of\s+breath|"
    r"discomfo|todler|fuher|mostproable|quandrandectomy|oetegenic|"
    r"osteclastoma|exeion|paial|interveebral|nonnal|aerial|sacroilitis"
    r")\b",
    flags=re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter raw teacher SFT data into final high-quality SFT JSONL."
    )
    parser.add_argument(
        "--raw_train",
        type=Path,
        default=Path("data/sft/teacher_generated_sft_train.raw.jsonl"),
    )
    parser.add_argument(
        "--raw_dev",
        type=Path,
        default=Path("data/sft/teacher_generated_sft_dev.raw.jsonl"),
    )
    parser.add_argument(
        "--output_train",
        type=Path,
        default=Path("data/sft/medical_cot_sft_train.jsonl"),
    )
    parser.add_argument(
        "--output_dev",
        type=Path,
        default=Path("data/sft/medical_cot_sft_dev.jsonl"),
    )
    parser.add_argument(
        "--rejected_output",
        type=Path,
        default=Path("data/sft/teacher_generated_sft_rejected_quality.jsonl"),
    )
    parser.add_argument(
        "--preview_output",
        type=Path,
        default=Path("data/sft/medical_cot_sft_preview_100.jsonl"),
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/teacher_sft_quality_filter_report.md"),
    )
    parser.add_argument("--target_train_size", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reject_dirty_input", action="store_true")
    parser.add_argument("--min_output_chars", type=int, default=120)
    parser.add_argument("--max_output_chars", type=int, default=2500)
    parser.add_argument("--min_steps", type=int, default=4)
    parser.add_argument("--max_steps", type=int, default=6)
    parser.add_argument("--a_min_steps", type=int, default=4)
    parser.add_argument("--a_max_steps", type=int, default=6)
    parser.add_argument("--b_min_steps", type=int, default=2)
    parser.add_argument("--b_max_steps", type=int, default=3)
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_text(value: Any) -> str:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", clean_text(value))
    text = text.lower()
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: Any, *, min_len: int = 4) -> set[str]:
    normalized = normalize_text(text)
    keywords: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", normalized):
        if len(token) < min_len:
            continue
        if token in STOPWORDS:
            continue
        keywords.add(token)
        if token.endswith("s") and len(token) > min_len:
            keywords.add(token[:-1])
    return keywords


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Raw SFT file does not exist: {path}")

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                rows.append(json.loads(text))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSON in {path}:{line_no}: {exc}") from exc

    if not rows:
        print(f"WARNING: raw SFT file is empty: {path}", file=sys.stderr)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def split_think_content(output: str) -> str:
    match = THINK_RE.search(output)
    return match.group(1) if match else ""


def extract_steps(output: str) -> list[str]:
    think = split_think_content(output)
    return [clean_text(match.group(2)) for match in STEP_RE.finditer(think)]


def english_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", text))


def step_bounds(sample: dict[str, Any], args: argparse.Namespace) -> tuple[int, int]:
    quality_tier = clean_text(sample.get("quality_tier")).upper()
    if quality_tier == "A":
        return args.a_min_steps, args.a_max_steps
    if quality_tier == "B":
        return args.b_min_steps, args.b_max_steps
    return args.min_steps, args.max_steps


def dirty_input(sample: dict[str, Any]) -> bool:
    text = sample.get("input", "")
    if not isinstance(text, str):
        return True
    answer_text = clean_text(sample.get("answer_text", ""))
    if SOURCE_NOISE_RE.search(f"{text} {answer_text}"):
        return True
    if "&;" in text or "aEUR" in text or "\x00" in text:
        return True
    if re.search(r"</?[A-Za-z][A-Za-z0-9]*(?:\s+[^>]*)?>", text):
        return True
    if re.search(r"([!?.,;:])\1{3,}", text):
        return True
    return False


def output_dirty_reasons(output: str) -> list[str]:
    reasons: list[str] = []
    stripped = output.strip()
    if "&;" in output:
        reasons.append("dirty_output_amp_semicolon")
    if "aEUR" in output:
        reasons.append("dirty_output_aeuro")
    if "\x00" in output:
        reasons.append("dirty_output_null")
    if stripped.endswith("..."):
        reasons.append("truncated_output_ellipsis")
    if "W..." in output:
        reasons.append("dirty_output_w_ellipsis")
    if re.search(r"([!?.,;:])\1{3,}", output):
        reasons.append("repeated_punctuation")
    if re.search(r"(?:\S+\s*\|\s*){3,}\S+", output) or output.count("\t") >= 3:
        reasons.append("table_compressed_gibberish")

    steps = extract_steps(output)
    if steps:
        last_step = steps[-1].strip()
        if last_step and not re.search(r"[.!?]\s*$", last_step):
            reasons.append("truncated_last_step")
    return reasons


def forbidden_phrase_reasons(output: str) -> list[str]:
    output_lower = output.lower()
    reasons: list[str] = []
    for phrase in FORBIDDEN_PHRASES:
        if phrase in {"Ans.", "Ans:"}:
            matched = bool(re.search(r"\bans\s*[\.:]", output, flags=re.IGNORECASE))
        elif phrase == "Answer:":
            matched = bool(re.search(r"\banswer\s*:", output, flags=re.IGNORECASE))
        else:
            matched = phrase.lower() in output_lower
        if matched:
            normalized = re.sub(r"[^a-z0-9]+", "_", phrase.lower()).strip("_")
            reasons.append(f"forbidden_phrase_{normalized}")
    return reasons


def validate_basic_format(sample: dict[str, Any], args: argparse.Namespace) -> list[str]:
    reasons: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in sample:
            reasons.append(f"missing_field_{field}")

    output = sample.get("output")
    answer = sample.get("answer")
    if not isinstance(output, str):
        return reasons + ["output_not_string"]

    output = output.strip()
    if len(output) < args.min_output_chars:
        reasons.append("output_too_short")
    if len(output) > args.max_output_chars:
        reasons.append("output_too_long")

    for tag in ("<think>", "</think>", "<answer>", "</answer>"):
        if tag not in output:
            reasons.append(f"missing_tag_{tag.strip('<>/')}")

    if output.lower().count("<answer>") != 1 or output.lower().count("</answer>") != 1:
        reasons.append("invalid_answer_tag_count")

    answer_matches = list(ANSWER_TAG_RE.finditer(output))
    if len(answer_matches) != 1:
        reasons.append("invalid_answer_tag")
    else:
        parsed_answer = clean_text(answer_matches[0].group(1))
        if parsed_answer not in LETTERS:
            reasons.append("invalid_answer_tag_value")
        if answer not in LETTERS:
            reasons.append("invalid_sample_answer")
        elif parsed_answer != answer:
            reasons.append("answer_mismatch")
        if output[answer_matches[0].end() :].strip():
            reasons.append("text_after_answer_tag")

    min_steps, max_steps = step_bounds(sample, args)
    steps = extract_steps(output)
    if len(steps) < min_steps:
        reasons.append(f"too_few_steps_for_tier_{clean_text(sample.get('quality_tier')) or 'unknown'}")
    if len(steps) > max_steps:
        reasons.append(f"too_many_steps_for_tier_{clean_text(sample.get('quality_tier')) or 'unknown'}")
    for index, step in enumerate(steps, start=1):
        if english_word_count(step) < 8:
            reasons.append(f"step_{index}_too_short")

    return reasons


def input_keywords(sample: dict[str, Any]) -> set[str]:
    return extract_keywords(sample.get("input", ""))


def answer_keywords(sample: dict[str, Any]) -> set[str]:
    return extract_keywords(sample.get("answer_text", ""), min_len=3)


def should_enforce_answer_text_support(answer_text: Any) -> bool:
    text = clean_text(answer_text)
    if not text:
        return False
    compact_lower = re.sub(r"[^a-z0-9]+", "", text.lower())
    if compact_lower in {"none", "allofabove", "alloftheabove", "allabove"}:
        return False
    if re.search(r"\d+\s*-\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)", text, re.I):
        return False
    compact = re.sub(r"[^A-Za-z0-9]+", "", text)
    if compact and (compact.isupper() or compact.isdigit()) and len(compact) <= 8:
        return False
    if re.search(r"\d", compact) and len(compact) <= 8:
        return False
    keywords = answer_keywords({"answer_text": text})
    if not keywords:
        return False
    if len(keywords) == 1:
        only = next(iter(keywords))
        if len(only) <= 3 or only.isdigit():
            return False
    return True


def covered_keywords(keywords: set[str], output: str) -> set[str]:
    output_tokens = extract_keywords(output, min_len=3)
    return keywords & output_tokens


def fuzzy_covered_keywords(keywords: set[str], output: str) -> set[str]:
    output_tokens = extract_keywords(output, min_len=3)
    covered: set[str] = set()
    for keyword in keywords:
        for token in output_tokens:
            if keyword == token:
                covered.add(keyword)
                break
            if min(len(keyword), len(token)) >= 5:
                ratio = difflib.SequenceMatcher(None, keyword, token).ratio()
                if ratio >= 0.84:
                    covered.add(keyword)
                    break
    return covered


def step_contains_specific_keywords(step: str, keywords: set[str], min_count: int = 1) -> bool:
    return len(covered_keywords(keywords, step)) >= min_count


def is_short_definition_question(sample: dict[str, Any], keywords: set[str]) -> bool:
    input_text = clean_text(sample.get("input", ""))
    question = input_text.split("\n\nOptions:", 1)[0]
    return len(question) < 140 or len(keywords) <= 5


def validate_reasoning_quality(sample: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    output = sample.get("output", "")
    steps = extract_steps(output)
    keywords = input_keywords(sample)
    answer_kw = answer_keywords(sample)
    output_keyword_hits = covered_keywords(keywords, output)
    short_definition = is_short_definition_question(sample, keywords)

    required_hits = 1 if short_definition else 2
    if len(keywords) >= required_hits and len(output_keyword_hits) < required_hits:
        reasons.append("low_input_keyword_coverage")

    if steps:
        step1_hits = fuzzy_covered_keywords(keywords, steps[0])
        if not step1_hits and len(output_keyword_hits) < required_hits:
            reasons.append("weak_step1")

    if answer_kw and should_enforce_answer_text_support(sample.get("answer_text", "")):
        answer_hits = fuzzy_covered_keywords(answer_kw, output)
        normalized_answer_text = normalize_text(sample.get("answer_text", ""))
        normalized_output = normalize_text(output)
        if normalized_answer_text and normalized_answer_text not in normalized_output:
            min_answer_hits = 1 if len(answer_kw) <= 2 else max(1, len(answer_kw) // 2)
            if len(answer_hits) < min_answer_hits:
                reasons.append("answer_text_not_supported")

    if len(steps) >= 3:
        output_lower = output.lower()
        generic_template = any(phrase in output_lower for phrase in GENERIC_TEMPLATE_PHRASES)
        generic_step_terms = (
            "selected choice",
            "remaining choices",
            "best match",
            "key clue",
            "given information",
            "relevant medical concept",
        )
        step2_lower = steps[1].lower()
        step3_lower = steps[2].lower()
        generic_step2 = any(term in step2_lower for term in generic_step_terms)
        generic_step3 = any(term in step3_lower for term in generic_step_terms)
        step2_hits = covered_keywords(keywords | answer_kw | MEDICAL_SIGNAL_WORDS, steps[1])
        step3_hits = covered_keywords(keywords | answer_kw | MEDICAL_SIGNAL_WORDS, steps[2])
        if generic_template or (
            generic_step2
            and generic_step3
            and len(step2_hits) == 0
            and len(step3_hits) == 0
        ):
            reasons.append("generic_reasoning")

    return reasons


def explicit_answer_mentions(output: str) -> list[str]:
    patterns = (
        r"(?:best|final|correct)\s+(?:answer|choice)\s+(?:is|:)\s*([A-D])\b",
        r"(?:answer|choice)\s+(?:is|:)\s*([A-D])\b",
        r"\boption\s+([A-D])\s+(?:is|as)\s+(?:the\s+)?(?:best|correct|final)\b",
        r"\b([A-D])\s+is\s+(?:the\s+)?(?:best|correct|final)\s+(?:answer|choice)\b",
    )
    mentions: list[str] = []
    for pattern in patterns:
        mentions.extend(match.upper() for match in re.findall(pattern, output, flags=re.IGNORECASE))
    return mentions


def validate_logic_consistency(sample: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    answer = sample.get("answer")
    mentions = explicit_answer_mentions(sample.get("output", ""))
    mention_set = set(mentions)
    if any(mention != answer for mention in mention_set):
        reasons.append("explicit_wrong_answer_mention")
    if len(mention_set) > 1:
        reasons.append("multiple_final_answer_mentions")
    return reasons


def validate_sample(sample: dict[str, Any], args: argparse.Namespace) -> tuple[list[str], bool]:
    reasons: list[str] = []
    sample_dirty_input = dirty_input(sample)
    if sample_dirty_input and args.reject_dirty_input:
        reasons.append("dirty_input")

    output = sample.get("output", "")
    reasons.extend(validate_basic_format(sample, args))
    if isinstance(output, str):
        reasons.extend(forbidden_phrase_reasons(output))
        reasons.extend(output_dirty_reasons(output))
        if not any(
            reason.startswith("missing_tag")
            or reason.startswith("invalid_answer_tag")
            or reason.startswith("too_few_steps")
            or reason.startswith("too_many_steps")
            or reason in {"output_not_string"}
            for reason in reasons
        ):
            reasons.extend(validate_reasoning_quality(sample))
            reasons.extend(validate_logic_consistency(sample))

    return sorted(set(reasons)), sample_dirty_input


def build_rejected_row(
    sample: dict[str, Any],
    reasons: list[str],
    sample_dirty_input: bool,
) -> dict[str, Any]:
    return {
        "id": clean_text(sample.get("id")),
        "source": clean_text(sample.get("source")),
        "split": clean_text(sample.get("split")),
        "reject_reasons": reasons,
        "dirty_input": sample_dirty_input,
        "sample": sample,
    }


def clean_final_row(sample: dict[str, Any]) -> dict[str, Any]:
    row = dict(sample)
    if isinstance(row.get("output"), str):
        row["output"] = row["output"].strip()
    return row


def filter_rows(
    raw_rows: list[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Counter[str], int]:
    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    dirty_input_count = 0

    for sample in raw_rows:
        reasons, sample_dirty_input = validate_sample(sample, args)
        if sample_dirty_input:
            dirty_input_count += 1
        if reasons:
            rejected.append(build_rejected_row(sample, reasons, sample_dirty_input))
            reason_counts.update(reasons)
            continue
        kept.append(clean_final_row(sample))

    return kept, rejected, reason_counts, dirty_input_count


def count_steps(row: dict[str, Any]) -> int:
    return len(extract_steps(row.get("output", "")))


def summarize_final(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output_lengths = [len(row.get("output", "")) for row in rows]
    step_counts = [count_steps(row) for row in rows]
    tier_counts = Counter(row.get("quality_tier") or "<EMPTY>" for row in rows)
    question_type_counts = Counter(row.get("question_type") or "<EMPTY>" for row in rows)
    tier_source_counts = Counter(
        f"{row.get('quality_tier') or '<EMPTY>'}/{row.get('source') or 'unknown'}"
        for row in rows
    )
    steps_by_tier: dict[str, Counter[int]] = {}
    for row in rows:
        tier = row.get("quality_tier") or "<EMPTY>"
        steps_by_tier.setdefault(tier, Counter())[count_steps(row)] += 1
    return {
        "source_counts": Counter(row.get("source") or "unknown" for row in rows),
        "answer_counts": Counter(row.get("answer") or "unknown" for row in rows),
        "subject_counts": Counter(row.get("subject") or "<EMPTY>" for row in rows),
        "tier_counts": tier_counts,
        "question_type_counts": question_type_counts,
        "tier_source_counts": tier_source_counts,
        "steps_by_tier": steps_by_tier,
        "avg_output_len": sum(output_lengths) / len(output_lengths) if output_lengths else 0.0,
        "min_output_len": min(output_lengths) if output_lengths else 0,
        "max_output_len": max(output_lengths) if output_lengths else 0,
        "avg_step_count": sum(step_counts) / len(step_counts) if step_counts else 0.0,
    }


def rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def recommendation(
    raw_count: int,
    final_train_count: int,
    rejected_count: int,
    dirty_input_count: int,
    reason_counts: Counter[str],
    target_train_size: int,
) -> tuple[str, str]:
    keep_rate = rate(raw_count - rejected_count, raw_count)
    answer_mismatch = reason_counts.get("answer_mismatch", 0)
    format_errors = sum(
        count
        for reason, count in reason_counts.items()
        if reason.startswith("missing_")
        or reason.startswith("invalid_")
        or reason.startswith("too_few_steps")
        or reason.startswith("too_many_steps")
        or reason
        in {
            "answer_mismatch",
            "text_after_answer_tag",
            "output_too_short",
            "output_too_long",
        }
    )

    if keep_rate < 0.5 or answer_mismatch >= 5 or format_errors >= max(10, raw_count * 0.05):
        return "FAIL", "不建议训练：保留率过低、答案不一致或格式错误较多。"

    target_met = target_train_size == 0 or final_train_count >= target_train_size
    forbidden_count = sum(
        count for reason, count in reason_counts.items() if reason.startswith("forbidden_phrase")
    )
    forbidden_rate = rate(forbidden_count, raw_count)
    dirty_rate = rate(dirty_input_count, raw_count)

    if target_met and keep_rate >= 0.75 and answer_mismatch == 0 and forbidden_rate <= 0.01:
        return "PASS", "可进入 SFT：格式稳定、保留率较高，未发现答案不一致。"

    if keep_rate >= 0.5:
        notes = []
        if not target_met:
            notes.append("final train 数量未达到目标")
        if keep_rate < 0.75:
            notes.append("保留率中等")
        if dirty_rate > 0.05:
            notes.append("dirty_input 较多")
        if forbidden_rate > 0.01:
            notes.append("禁止短语命中偏多")
        detail = "；".join(notes) if notes else "建议人工抽查后再训练"
        return "WARNING", f"可训练但建议人工抽查：{detail}。"

    return "FAIL", "不建议训练：质量过滤后有效样本不足。"


def counter_lines(counter: Counter[Any], limit: int | None = None) -> list[str]:
    items = counter.most_common(limit)
    if not items:
        return ["- 无"]
    return [f"- `{key}`：{value}" for key, value in items]


def steps_by_tier_lines(steps_by_tier: dict[str, Counter[int]]) -> list[str]:
    if not steps_by_tier:
        return ["- 无"]
    lines: list[str] = []
    for tier in sorted(steps_by_tier):
        parts = ", ".join(
            f"{step_count}步={count}" for step_count, count in sorted(steps_by_tier[tier].items())
        )
        lines.append(f"- `{tier}`：{parts}")
    return lines


def write_report(
    path: Path,
    raw_train: list[dict[str, Any]],
    raw_dev: list[dict[str, Any]],
    final_train: list[dict[str, Any]],
    final_dev: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    reason_counts: Counter[str],
    dirty_input_count: int,
    preview_output: Path,
    target_train_size: int,
) -> None:
    all_raw_count = len(raw_train) + len(raw_dev)
    all_final = final_train + final_dev
    all_rejected_count = len(rejected)
    summary = summarize_final(all_final)
    train_tiers = Counter(row.get("quality_tier") or "<EMPTY>" for row in final_train)
    train_a_count = train_tiers.get("A", 0)
    train_a_ratio = train_a_count / len(final_train) if final_train else 0.0
    status, advice = recommendation(
        raw_count=all_raw_count,
        final_train_count=len(final_train),
        rejected_count=all_rejected_count,
        dirty_input_count=dirty_input_count,
        reason_counts=reason_counts,
        target_train_size=target_train_size,
    )
    missing_train = max(target_train_size - len(final_train), 0) if target_train_size > 0 else 0

    lines = [
        "# Teacher SFT 质量过滤报告",
        "",
        "## 样本数",
        "",
        f"- raw train 样本数：{len(raw_train)}",
        f"- raw dev 样本数：{len(raw_dev)}",
        f"- final train 样本数：{len(final_train)}",
        f"- final dev 样本数：{len(final_dev)}",
        f"- final train A 档数量：{train_a_count}",
        f"- final train A 档占比：{train_a_ratio:.2%}",
        f"- rejected 样本数：{all_rejected_count}",
        f"- overall keep rate：{rate(len(all_final), all_raw_count):.2%}",
        f"- train keep rate：{rate(len(final_train), len(raw_train)):.2%}",
        f"- dev keep rate：{rate(len(final_dev), len(raw_dev)):.2%}",
        "",
        "## Reject Reason 分布",
        "",
        *counter_lines(reason_counts),
        "",
        "## Source 分布",
        "",
        *counter_lines(summary["source_counts"]),
        "",
        "## Quality Tier 分布",
        "",
        *counter_lines(summary["tier_counts"]),
        "",
        "## Question Type 分布",
        "",
        *counter_lines(summary["question_type_counts"]),
        "",
        "## Quality Tier / Source 分布",
        "",
        *counter_lines(summary["tier_source_counts"]),
        "",
        "## Answer 分布",
        "",
        *counter_lines(summary["answer_counts"]),
        "",
        "## Subject Top 20",
        "",
        *counter_lines(summary["subject_counts"], limit=20),
        "",
        "## Output 与 Step 统计",
        "",
        f"- 平均 output 长度：{summary['avg_output_len']:.2f}",
        f"- 最短 output 长度：{summary['min_output_len']}",
        f"- 最长 output 长度：{summary['max_output_len']}",
        f"- 平均 Step 数：{summary['avg_step_count']:.2f}",
        "",
        "## Step 数 / Quality Tier",
        "",
        *steps_by_tier_lines(summary["steps_by_tier"]),
        "",
        "## Dirty Input",
        "",
        f"- dirty_input 数量：{dirty_input_count}",
        "",
        "## Preview",
        "",
        f"- preview_100 路径：`{preview_output}`",
        "",
        "## Target Gap",
        "",
        f"- target_train_size：{target_train_size}",
        f"- final train 还差：{missing_train}",
        "",
        "## 最终建议",
        "",
        f"- {status}：{advice}",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def split_by_declared_split(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train_rows: list[dict[str, Any]] = []
    dev_rows: list[dict[str, Any]] = []
    for row in rows:
        if row.get("split") == "dev":
            dev_rows.append(row)
        else:
            train_rows.append(row)
    return train_rows, dev_rows


def main() -> None:
    args = parse_args()
    try:
        raw_train = read_jsonl(args.raw_train)
        raw_dev = read_jsonl(args.raw_dev)
        if not raw_train and not raw_dev:
            raise RuntimeError("Both raw train and raw dev files are empty.")

        final_from_train, rejected_train, train_reasons, dirty_train = filter_rows(raw_train, args)
        final_from_dev, rejected_dev, dev_reasons, dirty_dev = filter_rows(raw_dev, args)

        final_train, misplaced_dev_from_train = split_by_declared_split(final_from_train)
        misplaced_train_from_dev, final_dev = split_by_declared_split(final_from_dev)
        final_train.extend(misplaced_train_from_dev)
        final_dev.extend(misplaced_dev_from_train)

        rng = random.Random(args.seed)
        rng.shuffle(final_train)
        rng.shuffle(final_dev)
        all_final = final_train + final_dev
        preview_rows = (
            rng.sample(all_final, k=min(100, len(all_final))) if all_final else []
        )

        rejected = rejected_train + rejected_dev
        reason_counts = train_reasons + dev_reasons
        dirty_input_count = dirty_train + dirty_dev

        write_jsonl(args.output_train, final_train)
        write_jsonl(args.output_dev, final_dev)
        write_jsonl(args.rejected_output, rejected)
        write_jsonl(args.preview_output, preview_rows)
        write_report(
            args.report_path,
            raw_train=raw_train,
            raw_dev=raw_dev,
            final_train=final_train,
            final_dev=final_dev,
            rejected=rejected,
            reason_counts=reason_counts,
            dirty_input_count=dirty_input_count,
            preview_output=args.preview_output,
            target_train_size=args.target_train_size,
        )

        print("Teacher SFT quality filtering finished.")
        print(f"  raw train: {len(raw_train)}")
        print(f"  raw dev: {len(raw_dev)}")
        print(f"  final train: {len(final_train)}")
        print(f"  final dev: {len(final_dev)}")
        print(f"  rejected quality: {len(rejected)}")
        print(f"  report: {args.report_path}")
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI should surface a clear failure.
        raise SystemExit(f"ERROR: failed to filter teacher SFT data: {exc}") from exc


if __name__ == "__main__":
    main()
