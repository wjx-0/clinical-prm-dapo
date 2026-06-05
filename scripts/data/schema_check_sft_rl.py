"""Validate generated SFT and RL prompt data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
SFT_FILES = (
    Path("data/sft/medqa_medmcqa_cot_sft_train.jsonl"),
    Path("data/sft/medqa_medmcqa_cot_sft_dev.jsonl"),
)
RL_FILES = (
    Path("data/rl/medqa_medmcqa_rl_train.jsonl"),
    Path("data/rl/medqa_medmcqa_rl_dev.jsonl"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate SFT and RL prompt data.")
    parser.add_argument(
        "--error_output",
        type=Path,
        default=Path("outputs/data_validation/sft_rl_errors.jsonl"),
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/data_stats_sft_rl.md"),
    )
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


def extract_prompt_question(prompt: str) -> str:
    match = re.search(r"Question:\n(.+?)\n\nOptions:", prompt, flags=re.DOTALL)
    return clean_text(match.group(1)) if match else ""


def read_jsonl(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                yield line_no, json.loads(text), None
            except json.JSONDecodeError as exc:
                yield line_no, {}, f"invalid json: {exc.msg}"


def answer_tag_values(output: str) -> list[str]:
    return re.findall(r"<answer>\s*([A-D])\s*</answer>", output)


def mentioned_final_answers(output: str) -> set[str]:
    mentions = set(answer_tag_values(output))
    for match in re.findall(
        r"(?:best answer|final answer|correct answer)\s+is\s+([A-D])(?:[\s\.\),;:]|$)",
        output,
        flags=re.IGNORECASE,
    ):
        mentions.add(match.upper())
    return mentions


def validate_sft_sample(sample: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("instruction", "input", "output"):
        if field not in sample:
            errors.append(f"missing field: {field}")

    instruction = clean_text(sample.get("instruction"))
    input_text = clean_text(sample.get("input"))
    output = sample.get("output") if isinstance(sample.get("output"), str) else ""

    if not instruction:
        errors.append("empty instruction")
    if not input_text:
        errors.append("empty input")

    for tag in ("<think>", "</think>", "<answer>", "</answer>"):
        if tag not in output:
            errors.append(f"missing tag: {tag}")

    if output.count("<answer>") != 1 or output.count("</answer>") != 1:
        errors.append("output must contain exactly one answer tag")

    answers = answer_tag_values(output)
    if len(answers) != 1:
        errors.append("answer tag must contain exactly one of A/B/C/D")

    if len(output) < 80:
        errors.append("output too short")

    step_count = len(re.findall(r"\bStep\s+\d+\s*:", output))
    if step_count < 3:
        errors.append(f"too few steps: {step_count}")

    if len(mentioned_final_answers(output)) > 1:
        errors.append("output mentions multiple final answers")

    return errors


def validate_options(options: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(options, dict):
        return ["options is not a dict"]
    for letter in LETTERS:
        if letter not in options:
            errors.append(f"missing option: {letter}")
        elif not clean_text(options.get(letter)):
            errors.append(f"empty option: {letter}")
    return errors


def rl_leakage_errors(sample: dict[str, Any]) -> list[str]:
    raw_prompt = sample.get("prompt") if isinstance(sample.get("prompt"), str) else ""
    prompt = clean_text(raw_prompt)
    answer = sample.get("answer")
    explanation = clean_text(sample.get("explanation"))
    options = sample.get("options")
    errors: list[str] = []

    if answer in LETTERS:
        prompt_lower = prompt.lower()
        answer_lower = answer.lower()
        forbidden = [
            f"the correct answer is {answer_lower}",
            f"best answer is {answer_lower}",
            f"<answer>{answer_lower}</answer>",
        ]
        for phrase in forbidden:
            if phrase in prompt_lower:
                errors.append(f"gold answer leak: {phrase}")

    exempt_texts: list[str] = []
    if isinstance(options, dict):
        exempt_texts.extend(clean_text(value) for value in options.values())
    prompt_question = extract_prompt_question(raw_prompt)
    if prompt_question:
        exempt_texts.append(prompt_question)
    if (
        len(explanation) >= 30
        and not explanation_is_context_overlap(explanation, exempt_texts)
        and explanation.lower() in prompt.lower()
    ):
        errors.append("prompt contains explanation text")

    return errors


def validate_rl_sample(sample: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("id", "source", "prompt", "answer", "answer_text", "options"):
        if field not in sample:
            errors.append(f"missing field: {field}")

    prompt = clean_text(sample.get("prompt"))
    answer = sample.get("answer")
    options = sample.get("options")

    if not prompt:
        errors.append("empty prompt")
    if answer not in LETTERS:
        errors.append(f"invalid answer: {answer}")

    errors.extend(validate_options(options))
    if isinstance(options, dict) and answer in LETTERS:
        if sample.get("answer_text") != options.get(answer):
            errors.append("answer_text does not equal options[answer]")

    errors.extend(rl_leakage_errors(sample))
    return errors


def write_errors(path: Path, errors: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for error in errors:
            file.write(json.dumps(error, ensure_ascii=False) + "\n")


def empty_stats() -> dict[str, Any]:
    return {
        "count": 0,
        "errors": 0,
        "source_counts": Counter(),
        "total_output_len": 0,
        "total_prompt_len": 0,
        "format_pass": 0,
        "leak_count": 0,
    }


def validate_sft_file(path: Path, stats: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not path.exists():
        print(f"WARNING: missing SFT file: {path}", file=sys.stderr)
        return errors

    for line_no, sample, json_error in read_jsonl(path):
        stats["count"] += 1
        if json_error:
            sample_errors = [json_error]
        else:
            sample_errors = validate_sft_sample(sample)

        if sample_errors:
            stats["errors"] += 1
            errors.append(
                {
                    "file": str(path),
                    "line_no": line_no,
                    "id": sample.get("id", ""),
                    "errors": sample_errors,
                    "sample": sample,
                }
            )
        else:
            stats["format_pass"] += 1

        stats["source_counts"][clean_text(sample.get("source")) or "unknown"] += 1
        stats["total_output_len"] += len(sample.get("output", ""))

    return errors


def validate_rl_file(path: Path, stats: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not path.exists():
        print(f"WARNING: missing RL file: {path}", file=sys.stderr)
        return errors

    for line_no, sample, json_error in read_jsonl(path):
        stats["count"] += 1
        if json_error:
            sample_errors = [json_error]
        else:
            sample_errors = validate_rl_sample(sample)

        if sample_errors:
            stats["errors"] += 1
            if any("leak" in error or "explanation" in error for error in sample_errors):
                stats["leak_count"] += 1
            errors.append(
                {
                    "file": str(path),
                    "line_no": line_no,
                    "id": sample.get("id", ""),
                    "errors": sample_errors,
                    "sample": sample,
                }
            )
        elif rl_leakage_errors(sample):
            stats["leak_count"] += 1

        stats["source_counts"][clean_text(sample.get("source")) or "unknown"] += 1
        stats["total_prompt_len"] += len(sample.get("prompt", ""))

    return errors


def write_report(
    path: Path,
    sft_train_count: int,
    sft_dev_count: int,
    rl_train_count: int,
    rl_dev_count: int,
    sft_stats: dict[str, Any],
    rl_stats: dict[str, Any],
    total_errors: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sft_avg_output = (
        sft_stats["total_output_len"] / sft_stats["count"] if sft_stats["count"] else 0.0
    )
    rl_avg_prompt = (
        rl_stats["total_prompt_len"] / rl_stats["count"] if rl_stats["count"] else 0.0
    )
    sft_pass_rate = (
        sft_stats["format_pass"] / sft_stats["count"] if sft_stats["count"] else 0.0
    )
    passed = total_errors == 0

    lines = [
        "# SFT/RL 数据检查统计",
        "",
        "## 样本数",
        "",
        f"- SFT train：{sft_train_count}",
        f"- SFT dev：{sft_dev_count}",
        f"- RL train：{rl_train_count}",
        f"- RL dev：{rl_dev_count}",
        "",
        "## SFT source 分布",
        "",
    ]
    for source, count in sft_stats["source_counts"].most_common():
        lines.append(f"- {source}：{count}")

    lines.extend(["", "## RL source 分布", ""])
    for source, count in rl_stats["source_counts"].most_common():
        lines.append(f"- {source}：{count}")

    lines.extend(
        [
            "",
            "## 长度与格式",
            "",
            f"- SFT 平均 output 长度：{sft_avg_output:.2f}",
            f"- RL 平均 prompt 长度：{rl_avg_prompt:.2f}",
            f"- SFT 格式通过率：{sft_pass_rate:.4f}",
            f"- RL prompt 泄漏样本数：{rl_stats['leak_count']}",
            "",
            "## Validation 结果",
            "",
            f"- 是否通过：{'通过' if passed else '未通过'}",
            f"- 错误样本数：{total_errors}",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as file:
        return sum(1 for line in file if line.strip())


def schema_check(args: argparse.Namespace) -> None:
    sft_stats = empty_stats()
    rl_stats = empty_stats()
    all_errors: list[dict[str, Any]] = []

    for path in SFT_FILES:
        all_errors.extend(validate_sft_file(path, sft_stats))
    for path in RL_FILES:
        all_errors.extend(validate_rl_file(path, rl_stats))

    write_errors(args.error_output, all_errors)
    write_report(
        path=args.report_path,
        sft_train_count=count_jsonl(SFT_FILES[0]),
        sft_dev_count=count_jsonl(SFT_FILES[1]),
        rl_train_count=count_jsonl(RL_FILES[0]),
        rl_dev_count=count_jsonl(RL_FILES[1]),
        sft_stats=sft_stats,
        rl_stats=rl_stats,
        total_errors=len(all_errors),
    )

    print(f"SFT samples: {sft_stats['count']}, errors: {sft_stats['errors']}")
    print(f"RL samples: {rl_stats['count']}, errors: {rl_stats['errors']}")
    print(f"Errors written to: {args.error_output}")
    print(f"Report written to: {args.report_path}")
    if all_errors:
        print(f"Validation failed: {len(all_errors)} invalid samples.", file=sys.stderr)
    else:
        print("Validation passed.")


def main() -> None:
    args = parse_args()
    try:
        schema_check(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[schema_check_sft_rl] failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
