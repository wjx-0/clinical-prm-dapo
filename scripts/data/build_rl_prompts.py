"""Build RL prompt data for verl GRPO/DAPO from processed QA JSONL."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
DEFAULT_SOURCES = ("medqa", "medmcqa")
PROMPT_HEADER = (
    "Please solve the following medical multiple-choice question with "
    "step-by-step reasoning. Put your reasoning inside <think></think> and "
    "the final answer inside <answer></answer>."
)
REQUIREMENTS = (
    "Requirements:\n"
    "1. Analyze the question step by step.\n"
    "2. Do not mention multiple final answers.\n"
    "3. The final answer must be exactly one of A, B, C, or D.\n"
    "4. Use the format: <answer>LETTER</answer>."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build verl RL prompt data.")
    parser.add_argument("--input_dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output_dir", type=Path, default=Path("data/rl"))
    parser.add_argument("--stats_path", type=Path, default=Path("docs/data_stats_rl.md"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_samples", type=int, default=-1)
    parser.add_argument("--sources", nargs="+", default=list(DEFAULT_SOURCES))
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_for_leak_check(value: str) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"^[a-d]\s*[\.\):]\s*", "", text)
    text = re.sub(r"^[a-d]\s+i\.?e\.?\s*", "", text)
    text = re.sub(r"^ans\.?\s*[\.\):'-]*\s*", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def explanation_is_context_overlap(explanation: str, exempt_texts: list[str]) -> bool:
    explanation_norm = normalize_for_leak_check(explanation)
    if len(explanation_norm) < 20:
        return False
    for text in exempt_texts:
        text_norm = normalize_for_leak_check(text)
        if not text_norm:
            continue
        if explanation_norm in text_norm or text_norm in explanation_norm:
            return True
    return False


def default_files(input_dir: Path, sources: list[str], split: str) -> list[Path]:
    return [input_dir / f"{source}_{split}.jsonl" for source in sources]


def read_jsonl(path: Path, max_samples: int) -> list[dict[str, Any]]:
    if not path.exists():
        print(f"WARNING: missing input file: {path}", file=sys.stderr)
        return []

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            if max_samples > 0 and len(rows) >= max_samples:
                break
            text = line.strip()
            if not text:
                continue
            try:
                rows.append(json.loads(text))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSON in {path}:{line_no}: {exc}") from exc
    return rows


def format_prompt(sample: dict[str, Any]) -> str:
    options = sample["options"]
    return (
        f"{PROMPT_HEADER}\n\n"
        "Question:\n"
        f"{clean_text(sample['question'])}\n\n"
        "Options:\n"
        f"A. {clean_text(options['A'])}\n"
        f"B. {clean_text(options['B'])}\n"
        f"C. {clean_text(options['C'])}\n"
        f"D. {clean_text(options['D'])}\n\n"
        f"{REQUIREMENTS}"
    )


def validate_processed_sample(sample: dict[str, Any]) -> str | None:
    options = sample.get("options")
    if not clean_text(sample.get("id")):
        return "empty_id"
    if not clean_text(sample.get("source")):
        return "empty_source"
    if not clean_text(sample.get("question")):
        return "empty_question"
    if not isinstance(options, dict):
        return "invalid_options"
    for letter in LETTERS:
        if not clean_text(options.get(letter)):
            return f"empty_option_{letter}"
    if sample.get("answer") not in LETTERS:
        return "invalid_answer"
    if sample.get("answer_text") != options.get(sample.get("answer")):
        return "answer_text_mismatch"
    return None


def leakage_errors(
    prompt: str,
    answer: str,
    explanation: str,
    exempt_texts: list[str] | None = None,
) -> list[str]:
    prompt_lower = prompt.lower()
    answer_lower = answer.lower()
    errors: list[str] = []
    forbidden = [
        f"the correct answer is {answer_lower}",
        f"best answer is {answer_lower}",
        f"<answer>{answer_lower}</answer>",
    ]
    for phrase in forbidden:
        if phrase in prompt_lower:
            errors.append(f"gold_answer_leak: {phrase}")

    explanation_text = clean_text(explanation)
    if (
        len(explanation_text) >= 30
        and not explanation_is_context_overlap(explanation_text, exempt_texts or [])
        and explanation_text.lower() in prompt_lower
    ):
        errors.append("explanation_leak")
    return errors


def convert_sample(sample: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    reason = validate_processed_sample(sample)
    if reason:
        return None, reason

    prompt = format_prompt(sample)
    options = sample["options"]
    exempt_texts = [sample.get("question", "")] + [options.get(letter, "") for letter in LETTERS]
    leaks = leakage_errors(
        prompt,
        sample["answer"],
        sample.get("explanation", ""),
        exempt_texts=exempt_texts,
    )
    if leaks:
        return None, ";".join(leaks)

    return {
        "id": sample["id"],
        "source": sample["source"],
        "prompt": prompt,
        "answer": sample["answer"],
        "answer_text": sample["answer_text"],
        "options": {letter: clean_text(sample["options"][letter]) for letter in LETTERS},
        "explanation": clean_text(sample.get("explanation", "")),
        "subject": clean_text(sample.get("subject", "")),
        "topic": clean_text(sample.get("topic", "")),
    }, None


def build_split(
    paths: list[Path],
    max_samples: int,
    seed: int,
) -> tuple[list[dict[str, Any]], Counter[str], Counter[str], Counter[str], Counter[str]]:
    converted: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    answer_counts: Counter[str] = Counter()
    subject_counts: Counter[str] = Counter()
    filtered_reasons: Counter[str] = Counter()

    for path in paths:
        for sample in read_jsonl(path, max_samples):
            converted_sample, reason = convert_sample(sample)
            if converted_sample is None:
                filtered_reasons[reason or "unknown"] += 1
                continue

            converted.append(converted_sample)
            source_counts[converted_sample["source"]] += 1
            answer_counts[converted_sample["answer"]] += 1
            subject_counts[converted_sample["subject"] or "<EMPTY>"] += 1

    rng = random.Random(seed)
    rng.shuffle(converted)
    return converted, source_counts, answer_counts, subject_counts, filtered_reasons


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Missing pyarrow. Please run: pip install pyarrow") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)


def write_stats(
    stats_path: Path,
    train_rows: list[dict[str, Any]],
    dev_rows: list[dict[str, Any]],
    source_counts: Counter[str],
    answer_counts: Counter[str],
    subject_counts: Counter[str],
    filtered_reasons: Counter[str],
    max_samples: int,
    seed: int,
) -> None:
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    all_rows = train_rows + dev_rows
    avg_prompt_len = (
        sum(len(row["prompt"]) for row in all_rows) / len(all_rows) if all_rows else 0.0
    )
    leakage_count = sum(
        1
        for row in all_rows
        if leakage_errors(
            row["prompt"],
            row["answer"],
            row.get("explanation", ""),
            exempt_texts=list(row.get("options", {}).values()),
        )
    )

    lines = [
        "# RL Prompt 数据构造统计",
        "",
        f"- seed：`{seed}`",
        f"- max_samples：`{max_samples}`",
        "",
        "## 样本数",
        "",
        f"- train：{len(train_rows)}",
        f"- dev：{len(dev_rows)}",
        "",
        "## Source 分布",
        "",
    ]
    for source, count in source_counts.most_common():
        lines.append(f"- {source}：{count}")

    lines.extend(["", "## Answer 分布", ""])
    for answer, count in answer_counts.most_common():
        lines.append(f"- {answer}：{count}")

    lines.extend(["", "## Subject Top 20", ""])
    for subject, count in subject_counts.most_common(20):
        lines.append(f"- {subject}：{count}")

    lines.extend(
        [
            "",
            "## Prompt 长度与泄漏检查",
            "",
            f"- prompt 平均长度：{avg_prompt_len:.2f}",
            f"- gold answer 泄漏样本数：{leakage_count}",
        ]
    )

    lines.extend(["", "## 过滤原因", ""])
    if filtered_reasons:
        for reason, count in filtered_reasons.most_common():
            lines.append(f"- {reason}：{count}")
    else:
        lines.append("- 无")

    stats_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_rl_prompts(args: argparse.Namespace) -> None:
    train_paths = default_files(args.input_dir, args.sources, "train")
    dev_paths = default_files(args.input_dir, args.sources, "dev")

    train_rows, train_sources, train_answers, train_subjects, train_filtered = build_split(
        train_paths, args.max_samples, args.seed
    )
    dev_rows, dev_sources, dev_answers, dev_subjects, dev_filtered = build_split(
        dev_paths, args.max_samples, args.seed + 1
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_jsonl = args.output_dir / "medqa_medmcqa_rl_train.jsonl"
    dev_jsonl = args.output_dir / "medqa_medmcqa_rl_dev.jsonl"
    train_parquet = args.output_dir / "medqa_medmcqa_rl_train.parquet"
    dev_parquet = args.output_dir / "medqa_medmcqa_rl_dev.parquet"

    write_jsonl(train_jsonl, train_rows)
    write_jsonl(dev_jsonl, dev_rows)
    write_parquet(train_parquet, train_rows)
    write_parquet(dev_parquet, dev_rows)
    write_stats(
        stats_path=args.stats_path,
        train_rows=train_rows,
        dev_rows=dev_rows,
        source_counts=train_sources + dev_sources,
        answer_counts=train_answers + dev_answers,
        subject_counts=train_subjects + dev_subjects,
        filtered_reasons=train_filtered + dev_filtered,
        max_samples=args.max_samples,
        seed=args.seed,
    )

    print(f"RL train: {len(train_rows)}")
    print(f"RL dev: {len(dev_rows)}")
    print(f"RL data written to: {args.output_dir}")
    print(f"RL stats written to: {args.stats_path}")


def main() -> None:
    args = parse_args()
    try:
        build_rl_prompts(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[build_rl_prompts] failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
