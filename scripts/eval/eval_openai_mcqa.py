"""Evaluate MCQA models through an OpenAI-compatible chat completions API."""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import random
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INSTRUCTION = (
    "Please solve the following medical multiple-choice question with "
    "step-by-step reasoning. Put your reasoning inside <think></think> "
    "and the final answer inside <answer></answer>."
)
STRICT_ANSWER_RE = re.compile(r"<answer>\s*([A-D])\s*</answer>", re.IGNORECASE)
LOOSE_ANSWER_PATTERNS = [
    re.compile(r"(?:final|best|correct)\s+(?:answer|choice)\s*(?:is|:)\s*([A-D])\b", re.I),
    re.compile(r"\banswer\s*(?:is|:)\s*([A-D])\b", re.I),
    re.compile(r"\boption\s*([A-D])\b", re.I),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        action="append",
        type=Path,
        required=True,
        help="Processed MCQA JSONL file. Can be passed multiple times.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--sample-per-file", type=int, default=0, help="0 means full file.")
    parser.add_argument("--seed", type=int, default=20260606)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=2)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def sample_rows(rows: list[dict[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    if n <= 0 or n >= len(rows):
        return rows
    rng = random.Random(seed)
    indices = sorted(rng.sample(range(len(rows)), n))
    return [rows[i] for i in indices]


def format_options(options: Any) -> str:
    if isinstance(options, dict):
        return "\n".join(f"{key}. {options.get(key, '')}" for key in ["A", "B", "C", "D"])
    if isinstance(options, list):
        letters = ["A", "B", "C", "D"]
        return "\n".join(f"{letter}. {text}" for letter, text in zip(letters, options))
    return str(options)


def build_prompt(row: dict[str, Any]) -> str:
    question = row.get("question") or row.get("input") or ""
    if "Question:" in question and "Options:" in question:
        body = question
    else:
        body = f"Question:\n{question}\n\nOptions:\n{format_options(row.get('options', {}))}"
    return f"{DEFAULT_INSTRUCTION}\n\n{body}".strip()


def strict_answer(text: str) -> str | None:
    match = STRICT_ANSWER_RE.search(text or "")
    return match.group(1).upper() if match else None


def loose_answer(text: str) -> str | None:
    strict = strict_answer(text)
    if strict:
        return strict
    for pattern in LOOSE_ANSWER_PATTERNS:
        matches = pattern.findall(text or "")
        if matches:
            return matches[-1].upper()
    tail = (text or "")[-80:]
    standalone = re.findall(r"(?:^|[^A-Za-z])([A-D])(?:[^A-Za-z]|$)", tail)
    return standalone[-1].upper() if standalone else None


def post_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    timeout: float,
    retries: int,
) -> tuple[str, str]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    last_error = ""
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return content, ""
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    return "", last_error


def evaluate_one(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    prompt = build_prompt(row)
    response, error = post_chat_completion(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        retries=args.retries,
    )
    pred_strict = strict_answer(response)
    pred_loose = loose_answer(response)
    gold = str(row.get("answer", "")).upper()
    return {
        "id": row.get("id"),
        "source": row.get("source"),
        "split": row.get("split"),
        "answer": gold,
        "answer_text": row.get("answer_text"),
        "pred_strict": pred_strict,
        "pred_loose": pred_loose,
        "strict_correct": pred_strict == gold,
        "loose_correct": pred_loose == gold,
        "format_pass": pred_strict is not None,
        "error": error,
        "response": response,
    }


def pct(num: int, den: int) -> float:
    return round(100.0 * num / den, 2) if den else 0.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    by_source: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        source = row.get("source") or "unknown"
        by_source[source]["total"] += 1
        by_source[source]["strict_correct"] += int(bool(row.get("strict_correct")))
        by_source[source]["loose_correct"] += int(bool(row.get("loose_correct")))
        by_source[source]["format_pass"] += int(bool(row.get("format_pass")))
        by_source[source]["error"] += int(bool(row.get("error")))
    return {
        "total": total,
        "strict_accuracy": pct(sum(bool(r.get("strict_correct")) for r in rows), total),
        "loose_accuracy": pct(sum(bool(r.get("loose_correct")) for r in rows), total),
        "format_pass_rate": pct(sum(bool(r.get("format_pass")) for r in rows), total),
        "error_rate": pct(sum(bool(r.get("error")) for r in rows), total),
        "by_source": {
            source: {
                "total": counts["total"],
                "strict_accuracy": pct(counts["strict_correct"], counts["total"]),
                "loose_accuracy": pct(counts["loose_correct"], counts["total"]),
                "format_pass_rate": pct(counts["format_pass"], counts["total"]),
                "error_rate": pct(counts["error"], counts["total"]),
            }
            for source, counts in sorted(by_source.items())
        },
    }


def write_report(path: Path, args: argparse.Namespace, summary: dict[str, Any]) -> None:
    lines = [
        "# MCQA Evaluation Report",
        "",
        "## Config",
        "",
        f"- model: `{args.model}`",
        f"- base_url: `{args.base_url}`",
        f"- output: `{args.output}`",
        f"- sample_per_file: `{args.sample_per_file}`",
        f"- temperature: `{args.temperature}`",
        f"- max_tokens: `{args.max_tokens}`",
        "",
        "## Summary",
        "",
        f"- total: {summary['total']}",
        f"- strict_accuracy: {summary['strict_accuracy']}%",
        f"- loose_accuracy: {summary['loose_accuracy']}%",
        f"- format_pass_rate: {summary['format_pass_rate']}%",
        f"- error_rate: {summary['error_rate']}%",
        "",
        "## By Source",
        "",
        "| source | total | strict_acc | loose_acc | format_pass | error_rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for source, item in summary["by_source"].items():
        lines.append(
            f"| {source} | {item['total']} | {item['strict_accuracy']}% | "
            f"{item['loose_accuracy']}% | {item['format_pass_rate']}% | {item['error_rate']}% |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    all_rows: list[dict[str, Any]] = []
    for idx, path in enumerate(args.data):
        rows = load_jsonl(path)
        rows = sample_rows(rows, args.sample_per_file, args.seed + idx)
        all_rows.extend(rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_index = {executor.submit(evaluate_one, row, args): i for i, row in enumerate(all_rows)}
        ordered: dict[int, dict[str, Any]] = {}
        for future in futures.as_completed(future_to_index):
            index = future_to_index[future]
            ordered[index] = future.result()
        results = [ordered[i] for i in range(len(all_rows))]

    with args.output.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(results)
    write_report(args.report, args, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
