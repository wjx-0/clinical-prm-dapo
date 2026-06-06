"""Use an OpenAI-compatible judge model to review generated SFT rows."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_sft_with_teacher import (  # noqa: E402
    call_openai_compatible,
    clean_text,
    first_env_value,
    load_env_file,
)


SYSTEM_PROMPT = """You are a strict medical SFT data quality judge.

Evaluate whether a generated chain-of-thought style answer is suitable for supervised fine-tuning.
Be conservative, but do not reject merely because the prose style is not perfect.

Criteria:
1. The final answer letter must match the expected answer.
2. Medical facts must be correct or at least not contradicted by standard medical knowledge.
3. Reasoning must be grounded in the question, answer choices, and answer text. It must not invent missing symptoms, labs, imaging findings, smear findings, biopsy findings, or physical exam findings.
4. Each step should be useful. Option comparison is optional and should not be filler.
5. No data-generation traces such as "provided answer", "gold answer", "metadata", or "training data".
6. Length should be concise and appropriate for the question type.

Return only valid JSON."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge generated SFT quality with an LLM.")
    parser.add_argument("--env_file", type=Path, default=Path(".env"))
    parser.add_argument("--raw_train", type=Path, required=True)
    parser.add_argument("--rule_eval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report_path", type=Path, required=True)
    parser.add_argument("--model_name", default="")
    parser.add_argument("--base_url", default="")
    parser.add_argument("--api_key", default="")
    parser.add_argument("--num_workers", type=int, default=5)
    parser.add_argument("--max_samples", type=int, default=-1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max_retries", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max_tokens", type=int, default=350)
    return parser.parse_args()


def apply_env_defaults(args: argparse.Namespace) -> None:
    load_env_file(args.env_file)
    if not args.model_name:
        args.model_name = first_env_value(
            "JUDGE_MODEL_NAME",
            "DEEPSEEK_MODEL_NAME",
            "TEACHER_MODEL_NAME",
            "MODEL_NAME",
        )
    if not args.base_url:
        args.base_url = first_env_value(
            "JUDGE_BASE_URL",
            "DEEPSEEK_BASE_URL",
            "TEACHER_BASE_URL",
            "OPENAI_BASE_URL",
            "BASE_URL",
        )
    if not args.api_key:
        args.api_key = first_env_value(
            "JUDGE_API_KEY",
            "DEEPSEEK_API_KEY",
            "TEACHER_API_KEY",
            "LLM_API_KEY",
            "OPENAI_API_KEY",
        )


def read_jsonl(path: Path, max_samples: int = -1) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if max_samples > 0 and len(rows) >= max_samples:
                break
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_existing_ids(path: Path) -> set[str]:
    return {clean_text(row.get("id")) for row in read_jsonl(path)}


def build_user_prompt(row: dict[str, Any], rule_eval: dict[str, Any] | None) -> str:
    rule_block = json.dumps(rule_eval or {}, ensure_ascii=False)
    sample_block = {
        "id": row.get("id"),
        "source": row.get("source"),
        "quality_tier": row.get("quality_tier"),
        "question_type": row.get("question_type"),
        "input": row.get("input"),
        "output": row.get("output"),
        "expected_answer": row.get("answer"),
        "expected_answer_text": row.get("answer_text"),
    }
    return f"""Review this generated medical SFT sample.

Rule-based precheck:
{rule_block}

Sample:
{json.dumps(sample_block, ensure_ascii=False)}

Return JSON with exactly these keys:
{{
  "verdict": "PASS" | "WARN" | "FAIL",
  "answer_correct": true | false,
  "medical_facts_ok": true | false,
  "grounded": true | false,
  "steps_useful": true | false,
  "no_data_trace": true | false,
  "length_ok": true | false,
  "issues": ["short issue labels"],
  "comment": "one concise sentence"
}}
"""


def extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def normalize_judge_result(value: dict[str, Any]) -> dict[str, Any]:
    verdict = clean_text(value.get("verdict")).upper()
    if verdict not in {"PASS", "WARN", "FAIL"}:
        verdict = "WARN"
    issues = value.get("issues")
    if not isinstance(issues, list):
        issues = []
    return {
        "verdict": verdict,
        "answer_correct": bool(value.get("answer_correct")),
        "medical_facts_ok": bool(value.get("medical_facts_ok")),
        "grounded": bool(value.get("grounded")),
        "steps_useful": bool(value.get("steps_useful")),
        "no_data_trace": bool(value.get("no_data_trace")),
        "length_ok": bool(value.get("length_ok")),
        "issues": [clean_text(issue) for issue in issues if clean_text(issue)],
        "comment": clean_text(value.get("comment"))[:500],
    }


def judge_one(
    row: dict[str, Any],
    rule_eval: dict[str, Any] | None,
    args: argparse.Namespace,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(row, rule_eval)},
    ]
    last_error = ""
    for attempt in range(1, max(args.max_retries, 1) + 1):
        try:
            raw = call_openai_compatible(
                messages=messages,
                model_name=args.model_name,
                base_url=args.base_url,
                api_key=args.api_key,
                max_retries=1,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            parsed = normalize_judge_result(extract_json(raw))
            return {
                "id": clean_text(row.get("id")),
                "source": clean_text(row.get("source")),
                "quality_tier": clean_text(row.get("quality_tier")),
                "rule_status": clean_text((rule_eval or {}).get("rule_status")),
                **parsed,
            }
        except Exception as exc:  # noqa: BLE001 - retry model/parser errors.
            last_error = str(exc)
            if attempt < max(args.max_retries, 1):
                time.sleep(min(2**attempt, 20))
    return {
        "id": clean_text(row.get("id")),
        "source": clean_text(row.get("source")),
        "quality_tier": clean_text(row.get("quality_tier")),
        "rule_status": clean_text((rule_eval or {}).get("rule_status")),
        "verdict": "WARN",
        "answer_correct": False,
        "medical_facts_ok": False,
        "grounded": False,
        "steps_useful": False,
        "no_data_trace": True,
        "length_ok": False,
        "issues": ["judge_error"],
        "comment": last_error[:500],
    }


def process_rows(rows: list[dict[str, Any]], rule_by_id: dict[str, dict[str, Any]], args: argparse.Namespace) -> None:
    if not args.resume and args.output.exists():
        args.output.write_text("", encoding="utf-8")
    existing_ids = load_existing_ids(args.output) if args.resume else set()
    pending = [row for row in rows if clean_text(row.get("id")) not in existing_ids]
    if not pending:
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(args.num_workers, 1)) as executor:
        future_to_row = {
            executor.submit(judge_one, row, rule_by_id.get(clean_text(row.get("id"))), args): row
            for row in pending
        }
        for future in concurrent.futures.as_completed(future_to_row):
            result = future.result()
            append_jsonl(args.output, result)


def counter_lines(counter: Counter[Any]) -> list[str]:
    if not counter:
        return ["- 无"]
    return [f"- `{key}`：{value}" for key, value in counter.most_common()]


def write_report(path: Path, rows: list[dict[str, Any]]) -> None:
    verdicts = Counter(row.get("verdict") for row in rows)
    tier_verdicts = Counter(f"{row.get('quality_tier')}/{row.get('verdict')}" for row in rows)
    issue_counts = Counter(issue for row in rows for issue in row.get("issues", []))
    fail_or_warn = [row for row in rows if row.get("verdict") != "PASS"]
    lines = [
        "# LLM Judge SFT 逐条评估报告",
        "",
        "## Summary",
        "",
        f"- judged rows：{len(rows)}",
        "",
        "## Verdict",
        "",
        *counter_lines(verdicts),
        "",
        "## Tier / Verdict",
        "",
        *counter_lines(tier_verdicts),
        "",
        "## Issues",
        "",
        *counter_lines(issue_counts),
        "",
        "## Flagged Rows",
        "",
        "| id | tier | source | rule | judge | issues | comment |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in fail_or_warn:
        issues = ", ".join(row.get("issues") or []) or "none"
        comment = clean_text(row.get("comment")).replace("|", "/")
        lines.append(
            f"| `{row.get('id')}` | {row.get('quality_tier')} | {row.get('source')} | "
            f"{row.get('rule_status')} | {row.get('verdict')} | {issues} | {comment} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    apply_env_defaults(args)
    raw_rows = read_jsonl(args.raw_train, args.max_samples)
    rule_rows = read_jsonl(args.rule_eval)
    rule_by_id = {clean_text(row.get("id")): row for row in rule_rows}
    process_rows(raw_rows, rule_by_id, args)
    judged_rows = read_jsonl(args.output)
    judged_rows.sort(key=lambda row: clean_text(row.get("id")))
    write_jsonl(args.output, judged_rows)
    write_report(args.report_path, judged_rows)
    verdicts = Counter(row.get("verdict") for row in judged_rows)
    print("LLM judge evaluation finished.")
    print(f"  rows: {len(judged_rows)}")
    print(f"  verdicts: {dict(verdicts)}")
    print(f"  output: {args.output}")
    print(f"  report: {args.report_path}")


if __name__ == "__main__":
    main()
