"""Evaluate generated teacher SFT rows with deterministic quality checks."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
STEP_RE = re.compile(
    r"\bStep\s+(\d+)\s*:\s*(.*?)(?=\n\s*Step\s+\d+\s*:|\n\s*</think>|$)",
    flags=re.IGNORECASE | re.DOTALL,
)
ANSWER_TAG_RE = re.compile(r"<answer>\s*([^<]+?)\s*</answer>", flags=re.IGNORECASE)
QUESTION_RE = re.compile(r"Question:\n(.+?)\n\nOptions:", flags=re.DOTALL)
TRACE_RE = re.compile(
    r"gold answer|provided answer|provided explanation|quality_tier|metadata|"
    r"supervised fine-tuning|training-quality|data generation|correct answer was",
    flags=re.IGNORECASE,
)
IMAGE_LIKE_RE = re.compile(
    r"\b(image|figure|photograph|photomicrograph|shown below|shown above|is shown|"
    r"are shown|given below|given above)\b",
    flags=re.IGNORECASE,
)
GENERIC_RE = re.compile(
    r"question stem is reviewed|selected choice corresponds|remaining choices are treated|"
    r"best match the key clue|relevant medical concept",
    flags=re.IGNORECASE,
)
STOPWORDS = {
    "about",
    "after",
    "among",
    "because",
    "best",
    "choice",
    "clinical",
    "following",
    "from",
    "have",
    "most",
    "patient",
    "question",
    "should",
    "that",
    "this",
    "which",
    "with",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate generated SFT quality row by row.")
    parser.add_argument("--raw_train", type=Path, required=True)
    parser.add_argument("--clean_train", type=Path, required=True)
    parser.add_argument("--rejected_quality", type=Path, required=True)
    parser.add_argument("--eval_output", type=Path, required=True)
    parser.add_argument("--report_path", type=Path, required=True)
    parser.add_argument("--sample_preview", type=int, default=30)
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_text(value: Any) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_question(input_text: str) -> str:
    match = QUESTION_RE.search(input_text)
    return clean_text(match.group(1)) if match else ""


def extract_steps(output: str) -> list[str]:
    return [clean_text(match.group(2)) for match in STEP_RE.finditer(output)]


def english_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", text))


def keywords(text: str, min_len: int = 4) -> set[str]:
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", normalize_text(text)):
        if len(token) < min_len or token in STOPWORDS:
            continue
        tokens.add(token)
        if token.endswith("s") and len(token) > min_len:
            tokens.add(token[:-1])
    return tokens


def answer_text_supported(answer_text: str, output: str) -> bool:
    answer_norm = normalize_text(answer_text)
    output_norm = normalize_text(output)
    if not answer_norm:
        return True
    compact = re.sub(r"[^a-z0-9]+", "", answer_norm)
    if len(compact) <= 3 or compact.isdigit():
        return True
    if answer_norm in output_norm:
        return True
    answer_keywords = keywords(answer_text, min_len=4)
    if not answer_keywords:
        return True
    output_keywords = keywords(output, min_len=4)
    hits = answer_keywords & output_keywords
    return len(hits) >= max(1, len(answer_keywords) // 2)


def step_bounds(row: dict[str, Any]) -> tuple[int, int]:
    tier = clean_text(row.get("quality_tier")).upper()
    if tier == "A":
        return 4, 6
    if tier == "B":
        return 2, 3
    return 3, 6


def evaluate_row(
    row: dict[str, Any],
    clean_ids: set[str],
    rejected_reasons: dict[str, list[str]],
) -> dict[str, Any]:
    sample_id = clean_text(row.get("id"))
    output = row.get("output") if isinstance(row.get("output"), str) else ""
    input_text = row.get("input") if isinstance(row.get("input"), str) else ""
    question = extract_question(input_text)
    answer = clean_text(row.get("answer"))
    answer_text = clean_text(row.get("answer_text"))
    steps = extract_steps(output)
    min_steps, max_steps = step_bounds(row)
    reasons: list[str] = []
    warnings: list[str] = []

    answer_tags = [clean_text(match.group(1)) for match in ANSWER_TAG_RE.finditer(output)]
    format_ok = (
        output.count("<think>") == 1
        and output.count("</think>") == 1
        and output.lower().count("<answer>") == 1
        and output.lower().count("</answer>") == 1
        and len(answer_tags) == 1
    )
    if not format_ok:
        reasons.append("format_invalid")
    if len(answer_tags) != 1 or answer_tags[0] not in LETTERS:
        reasons.append("answer_tag_invalid")
    elif answer_tags[0] != answer:
        reasons.append("answer_mismatch")

    if sample_id not in clean_ids:
        reasons.append("filter_rejected")
        for reason in rejected_reasons.get(sample_id, []):
            reasons.append(f"filter_{reason}")

    if len(steps) < min_steps:
        reasons.append("too_few_steps_for_tier")
    if len(steps) > max_steps:
        reasons.append("too_many_steps_for_tier")
    if output and output.strip()[-1:] == "." and "</answer>" not in output:
        reasons.append("truncated_output")
    if steps and not re.search(r"[.!?]\s*$", steps[-1]):
        reasons.append("truncated_last_step")
    if steps and english_word_count(steps[-1]) < 9:
        warnings.append("short_final_step")

    if TRACE_RE.search(output):
        reasons.append("data_generation_trace")
    if IMAGE_LIKE_RE.search(input_text):
        warnings.append("image_like_input_phrase")
    if GENERIC_RE.search(output):
        warnings.append("generic_template_phrase")
    if not answer_text_supported(answer_text, output):
        warnings.append("answer_text_not_explicitly_supported")

    question_keywords = keywords(question, min_len=4)
    output_keywords = keywords(output, min_len=4)
    if len(question_keywords) >= 6 and len(question_keywords & output_keywords) < 3:
        warnings.append("low_question_keyword_coverage")
    if steps:
        step1_keywords = keywords(steps[0], min_len=4)
        if len(question_keywords) >= 6 and len(question_keywords & step1_keywords) < 2:
            warnings.append("weak_step1_grounding")

    if len(output) < 250:
        warnings.append("output_short")
    if len(output) > 1800:
        warnings.append("output_long")

    if reasons:
        status = "FAIL"
    elif warnings:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "id": sample_id,
        "source": clean_text(row.get("source")),
        "split": clean_text(row.get("split")),
        "quality_tier": clean_text(row.get("quality_tier")) or "<EMPTY>",
        "question_type": clean_text(row.get("question_type")) or "<EMPTY>",
        "answer": answer,
        "answer_text": answer_text,
        "question_len": len(question),
        "output_len": len(output),
        "step_count": len(steps),
        "filter_pass": sample_id in clean_ids,
        "rule_status": status,
        "fail_reasons": sorted(set(reasons)),
        "warnings": sorted(set(warnings)),
        "question_preview": question[:180],
        "final_step": steps[-1] if steps else "",
        "medical_fact_check": "not_rule_verifiable",
    }


def counter_lines(counter: Counter[Any]) -> list[str]:
    if not counter:
        return ["- 无"]
    return [f"- `{key}`：{value}" for key, value in counter.most_common()]


def write_report(path: Path, evaluations: list[dict[str, Any]], sample_preview: int) -> None:
    status_counts = Counter(row["rule_status"] for row in evaluations)
    tier_counts = Counter(row["quality_tier"] for row in evaluations)
    tier_status = Counter(f"{row['quality_tier']}/{row['rule_status']}" for row in evaluations)
    fail_reasons = Counter(reason for row in evaluations for reason in row["fail_reasons"])
    warnings = Counter(reason for row in evaluations for reason in row["warnings"])
    clean_count = sum(1 for row in evaluations if row["filter_pass"])
    a_count = sum(1 for row in evaluations if row["filter_pass"] and row["quality_tier"] == "A")
    a_ratio = a_count / clean_count if clean_count else 0.0

    lines = [
        "# SFT 逐条质量评估报告",
        "",
        "## Summary",
        "",
        f"- total raw rows：{len(evaluations)}",
        f"- filter pass rows：{clean_count}",
        f"- filter pass A tier：{a_count}",
        f"- filter pass A ratio：{a_ratio:.2%}",
        "- medical_fact_check：规则无法可靠验证医学事实正确性，需人工抽检或 LLM-as-judge 复核。",
        "",
        "## Rule Status",
        "",
        *counter_lines(status_counts),
        "",
        "## Quality Tier",
        "",
        *counter_lines(tier_counts),
        "",
        "## Tier / Status",
        "",
        *counter_lines(tier_status),
        "",
        "## Fail Reasons",
        "",
        *counter_lines(fail_reasons),
        "",
        "## Warnings",
        "",
        *counter_lines(warnings),
        "",
        "## Row-Level Evaluation",
        "",
        "| # | id | tier | source | steps | status | issues | question preview |",
        "|---:|---|---|---|---:|---|---|---|",
    ]
    for index, row in enumerate(evaluations, start=1):
        issues = ", ".join(row["fail_reasons"] + row["warnings"]) or "ok"
        preview = row["question_preview"].replace("|", "/")
        lines.append(
            f"| {index} | `{row['id']}` | {row['quality_tier']} | {row['source']} | "
            f"{row['step_count']} | {row['rule_status']} | {issues} | {preview} |"
        )

    flagged = [row for row in evaluations if row["rule_status"] != "PASS"][:sample_preview]
    lines.extend(["", "## Flagged Preview", ""])
    if not flagged:
        lines.append("无")
    for row in flagged:
        lines.extend(
            [
                f"### {row['id']} [{row['rule_status']}]",
                "",
                f"- tier/source：{row['quality_tier']} / {row['source']}",
                f"- fail_reasons：{', '.join(row['fail_reasons']) or '无'}",
                f"- warnings：{', '.join(row['warnings']) or '无'}",
                f"- final_step：{row['final_step']}",
                "",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    raw_rows = read_jsonl(args.raw_train)
    clean_ids = {clean_text(row.get("id")) for row in read_jsonl(args.clean_train)}
    rejected_reasons = {
        clean_text(row.get("id")): list(row.get("reject_reasons") or [])
        for row in read_jsonl(args.rejected_quality)
    }
    evaluations = [evaluate_row(row, clean_ids, rejected_reasons) for row in raw_rows]
    write_jsonl(args.eval_output, evaluations)
    write_report(args.report_path, evaluations, args.sample_preview)

    status_counts = Counter(row["rule_status"] for row in evaluations)
    print("SFT quality evaluation finished.")
    print(f"  rows: {len(evaluations)}")
    print(f"  status: {dict(status_counts)}")
    print(f"  eval: {args.eval_output}")
    print(f"  report: {args.report_path}")


if __name__ == "__main__":
    main()
