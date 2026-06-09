"""Download and normalize MMLU medical subsets from Hugging Face.

The output schema matches data/processed/* MCQA files so the existing
OpenAI-compatible evaluation script can reuse it with minimal changes.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


DATASET = "cais/mmlu"
API_BASE = "https://datasets-server.huggingface.co"
SUBJECTS = [
    "anatomy",
    "clinical_knowledge",
    "college_biology",
    "college_medicine",
    "medical_genetics",
    "professional_medicine",
]
SPLITS = ["dev", "validation", "test"]
LETTERS = ["A", "B", "C", "D"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--report-path", type=Path, default=Path("docs/mmlu_medical_download.md"))
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    return parser.parse_args()


def fetch_json(path: str, params: dict[str, Any], *, retries: int = 3) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE}{path}?{query}"
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - CLI should retry transient API failures.
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def fetch_rows(config: str, split: str, page_size: int, sleep_seconds: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    total: int | None = None
    while True:
        payload = fetch_json(
            "/rows",
            {
                "dataset": DATASET,
                "config": config,
                "split": split,
                "offset": offset,
                "length": page_size,
            },
        )
        page_rows = [item["row"] for item in payload.get("rows", [])]
        rows.extend(page_rows)
        total = int(payload.get("num_rows_total") or len(rows))
        offset += len(page_rows)
        if offset >= total or not page_rows:
            break
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    return rows


def normalize_answer(value: Any) -> str:
    if isinstance(value, int):
        if 0 <= value < len(LETTERS):
            return LETTERS[value]
        raise ValueError(f"answer index out of range: {value}")
    text = str(value).strip().upper()
    if text in LETTERS:
        return text
    if text.isdigit():
        index = int(text)
        if 0 <= index < len(LETTERS):
            return LETTERS[index]
    raise ValueError(f"unsupported answer value: {value!r}")


def normalize_row(row: dict[str, Any], *, subject: str, split: str, index: int) -> dict[str, Any]:
    choices = row.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        raise ValueError(f"expected 4 choices for {subject}/{split}/{index}, got {choices!r}")
    answer = normalize_answer(row.get("answer"))
    options = {letter: str(choice) for letter, choice in zip(LETTERS, choices)}
    return {
        "id": f"mmlu_{subject}_{split}_{index + 1:06d}",
        "source": "mmlu",
        "split": split,
        "language": "en",
        "question": str(row.get("question") or ""),
        "options": options,
        "answer": answer,
        "answer_text": options[answer],
        "explanation": "",
        "subject": subject,
        "topic": "",
        "choice_type": "single",
        "mmlu_subject": subject,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def main() -> None:
    args = parse_args()
    rows_by_split: dict[str, list[dict[str, Any]]] = {split: [] for split in SPLITS}
    count_rows: list[list[Any]] = []

    for subject in SUBJECTS:
        for split in SPLITS:
            raw_rows = fetch_rows(subject, split, args.page_size, args.sleep_seconds)
            normalized = [
                normalize_row(row, subject=subject, split=split, index=index)
                for index, row in enumerate(raw_rows)
            ]
            rows_by_split[split].extend(normalized)
            count_rows.append([subject, split, len(normalized)])

    all_rows: list[dict[str, Any]] = []
    for split in SPLITS:
        rows = rows_by_split[split]
        all_rows.extend(rows)
        write_jsonl(args.output_dir / f"mmlu_medical_{split}.jsonl", rows)
    write_jsonl(args.output_dir / "mmlu_medical_all.jsonl", all_rows)

    source_counts = Counter(row["source"] for row in all_rows)
    subject_counts = Counter(row["subject"] for row in all_rows)
    split_counts = Counter(row["split"] for row in all_rows)

    report_lines = [
        "# MMLU Medical Download",
        "",
        f"- dataset: `{DATASET}`",
        f"- output_dir: `{args.output_dir}`",
        f"- total_rows: {len(all_rows)}",
        "",
        "## Split Counts",
        "",
        *[f"- `{split}`: {count}" for split, count in sorted(split_counts.items())],
        "",
        "## Subject Counts",
        "",
        *[f"- `{subject}`: {count}" for subject, count in sorted(subject_counts.items())],
        "",
        "## Source Counts",
        "",
        *[f"- `{source}`: {count}" for source, count in sorted(source_counts.items())],
        "",
        "## Subject x Split",
        "",
        *markdown_table(["subject", "split", "rows"], count_rows),
        "",
        "## Output Files",
        "",
        *[f"- `{args.output_dir / f'mmlu_medical_{split}.jsonl'}`" for split in SPLITS],
        f"- `{args.output_dir / 'mmlu_medical_all.jsonl'}`",
    ]
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("MMLU medical download finished.")
    print(f"  total: {len(all_rows)}")
    for split in SPLITS:
        print(f"  {split}: {len(rows_by_split[split])}")
    print(f"  report: {args.report_path}")


if __name__ == "__main__":
    main()
