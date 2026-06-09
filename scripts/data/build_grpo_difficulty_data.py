"""Build GRPO data from train MCQA samples with model-estimated difficulty.

Workflow:
1. build-candidates: choose a 20k candidate pool from MedQA/MedMCQA train.
2. sample-difficulty: call an OpenAI-compatible API and sample each prompt n times.
3. select-grpo: select 10k train + monitor rows by difficulty buckets and write
   verl-compatible parquet files.
"""

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


LETTERS = ("A", "B", "C", "D")
DEFAULT_OUTPUT_DIR = Path("data/rl/v1_grpo_10k")
DEFAULT_EXCLUDE_SFT = Path(
    "data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k.jsonl"
)
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
VISUAL_DEPENDENT_RE = re.compile(
    r"("
    r"\b(?:image|figure|photograph|histology slide|microscopy|radiograph|x-?ray|ct scan|mri)"
    r"\b.{0,60}\b(?:shown|below|above|arrow|marked)\b"
    r"|"
    r"\b(?:shown|below|above|arrow|marked)\b.{0,60}"
    r"\b(?:image|figure|photograph|radiograph|x-?ray|ct scan|mri)\b"
    r")",
    flags=re.IGNORECASE,
)
STRICT_ANSWER_RE = re.compile(r"<answer>\s*([A-D])\s*</answer>", flags=re.IGNORECASE)
LOOSE_ANSWER_PATTERNS = [
    re.compile(r"(?:final|best|correct)\s+(?:answer|choice)\s*(?:is|:)\s*([A-D])\b", re.I),
    re.compile(r"\banswer\s*(?:is|:)\s*([A-D])\b", re.I),
    re.compile(r"\boption\s*([A-D])\b", re.I),
]
BUCKET_LABELS = {
    0: "hard_0_of_4",
    1: "medium_hard_1_of_4",
    2: "medium_2_of_4",
    3: "medium_easy_3_of_4",
    4: "easy_4_of_4",
}
BUCKET_WEIGHTS = {2: 0.40, 1: 0.25, 3: 0.25, 0: 0.05, 4: 0.05}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-candidates")
    build.add_argument("--medqa-train", type=Path, default=Path("data/processed/medqa_train.jsonl"))
    build.add_argument(
        "--medmcqa-train", type=Path, default=Path("data/processed/medmcqa_train.jsonl")
    )
    build.add_argument("--exclude-sft", type=Path, action="append", default=[DEFAULT_EXCLUDE_SFT])
    build.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    build.add_argument(
        "--candidate-output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "difficulty_candidate_pool.jsonl",
    )
    build.add_argument(
        "--report-path",
        type=Path,
        default=Path("docs/rl_v1_grpo_10k_candidate_pool.md"),
    )
    build.add_argument("--medqa-candidates", type=int, default=5000)
    build.add_argument("--medmcqa-long-candidates", type=int, default=7500)
    build.add_argument("--medmcqa-short-candidates", type=int, default=7500)
    build.add_argument("--long-threshold", type=int, default=180)
    build.add_argument("--seed", type=int, default=20260608)

    sample = subparsers.add_parser("sample-difficulty")
    sample.add_argument(
        "--candidate-input",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "difficulty_candidate_pool.jsonl",
    )
    sample.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "difficulty_samples_epoch1_n4.jsonl",
    )
    sample.add_argument(
        "--report-path",
        type=Path,
        default=Path("docs/rl_v1_grpo_10k_difficulty_sampling.md"),
    )
    sample.add_argument("--model", required=True)
    sample.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    sample.add_argument("--api-key", default="EMPTY")
    sample.add_argument("--num-generations", type=int, default=4)
    sample.add_argument("--workers", type=int, default=16)
    sample.add_argument("--temperature", type=float, default=0.7)
    sample.add_argument("--top-p", type=float, default=0.95)
    sample.add_argument("--max-tokens", type=int, default=768)
    sample.add_argument("--timeout", type=float, default=180.0)
    sample.add_argument("--retries", type=int, default=2)
    sample.add_argument("--resume", action="store_true")
    sample.add_argument("--progress-every", type=int, default=50)
    sample.add_argument("--max-rows", type=int, default=0, help="0 means all candidate rows.")

    select = subparsers.add_parser("select-grpo")
    select.add_argument(
        "--difficulty-input",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "difficulty_samples_epoch1_n4.jsonl",
    )
    select.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    select.add_argument(
        "--report-path",
        type=Path,
        default=Path("docs/rl_v1_grpo_10k_selection.md"),
    )
    select.add_argument("--train-size", type=int, default=10000)
    select.add_argument("--val-size", type=int, default=500)
    select.add_argument("--medqa-train-size", type=int, default=4000)
    select.add_argument("--medmcqa-train-size", type=int, default=6000)
    select.add_argument("--seed", type=int, default=20260608)

    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Missing pyarrow. Please install pyarrow in the verl env.") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return lines


def valid_processed_row(row: dict[str, Any]) -> str | None:
    options = row.get("options")
    if not clean_text(row.get("id")):
        return "empty_id"
    if not clean_text(row.get("source")):
        return "empty_source"
    if not clean_text(row.get("question")):
        return "empty_question"
    if not isinstance(options, dict):
        return "invalid_options"
    for letter in LETTERS:
        if not clean_text(options.get(letter)):
            return f"empty_option_{letter}"
    answer = row.get("answer")
    if answer not in LETTERS:
        return "invalid_answer"
    if clean_text(row.get("answer_text")) != clean_text(options.get(answer)):
        return "answer_text_mismatch"
    if VISUAL_DEPENDENT_RE.search(clean_text(row.get("question"))):
        return "visual_dependency"
    return None


def format_prompt(row: dict[str, Any]) -> str:
    options = row["options"]
    return (
        f"{PROMPT_HEADER}\n\n"
        "Question:\n"
        f"{clean_text(row['question'])}\n\n"
        "Options:\n"
        f"A. {clean_text(options['A'])}\n"
        f"B. {clean_text(options['B'])}\n"
        f"C. {clean_text(options['C'])}\n"
        f"D. {clean_text(options['D'])}\n\n"
        f"{REQUIREMENTS}"
    )


def public_candidate_row(row: dict[str, Any], *, length_bucket: str, long_threshold: int) -> dict[str, Any]:
    options = row["options"]
    return {
        "id": row["id"],
        "source": row["source"],
        "split": row.get("split", "train"),
        "language": row.get("language", "en"),
        "question": clean_text(row["question"]),
        "options": {letter: clean_text(options[letter]) for letter in LETTERS},
        "answer": row["answer"],
        "answer_text": clean_text(row["answer_text"]),
        "subject": clean_text(row.get("subject", "")),
        "topic": clean_text(row.get("topic", "")),
        "choice_type": clean_text(row.get("choice_type", "single")),
        "question_chars": len(clean_text(row["question"])),
        "length_bucket": length_bucket,
        "long_threshold": long_threshold,
        "prompt": format_prompt(row),
    }


def sft_seen_ids(paths: list[Path]) -> set[str]:
    seen: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for row in read_jsonl(path):
            sample_id = clean_text(row.get("id"))
            if sample_id:
                seen.add(sample_id)
    return seen


def filtered_pool(
    path: Path,
    *,
    seen_ids: set[str],
    long_threshold: int,
    reason_counts: Counter[str],
) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    for row in read_jsonl(path):
        sample_id = clean_text(row.get("id"))
        if sample_id in seen_ids:
            reason_counts["sft_seen_id"] += 1
            continue
        reason = valid_processed_row(row)
        if reason:
            reason_counts[reason] += 1
            continue
        length_bucket = "long" if len(clean_text(row["question"])) >= long_threshold else "short"
        pool.append(public_candidate_row(row, length_bucket=length_bucket, long_threshold=long_threshold))
    return pool


def stratified_sample(rows: list[dict[str, Any]], size: int, seed: int) -> list[dict[str, Any]]:
    if size <= 0:
        return []
    if len(rows) <= size:
        return list(rows)

    rng = random.Random(seed)
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_subject[row.get("subject") or "<EMPTY>"].append(row)
    for group in by_subject.values():
        rng.shuffle(group)

    total = len(rows)
    subjects = sorted(by_subject)
    quotas: dict[str, int] = {}
    fractional: list[tuple[float, str]] = []
    for subject in subjects:
        exact = size * len(by_subject[subject]) / total
        quota = min(len(by_subject[subject]), int(exact))
        quotas[subject] = quota
        fractional.append((exact - quota, subject))

    remaining = size - sum(quotas.values())
    for _, subject in sorted(fractional, reverse=True):
        if remaining <= 0:
            break
        if quotas[subject] < len(by_subject[subject]):
            quotas[subject] += 1
            remaining -= 1

    selected: list[dict[str, Any]] = []
    for subject in subjects:
        selected.extend(by_subject[subject][: quotas[subject]])
    rng.shuffle(selected)
    return selected[:size]


def build_candidates(args: argparse.Namespace) -> None:
    seen_ids = sft_seen_ids(args.exclude_sft)
    reasons: Counter[str] = Counter()
    medqa_pool = filtered_pool(
        args.medqa_train,
        seen_ids=seen_ids,
        long_threshold=args.long_threshold,
        reason_counts=reasons,
    )
    medmcqa_pool = filtered_pool(
        args.medmcqa_train,
        seen_ids=seen_ids,
        long_threshold=args.long_threshold,
        reason_counts=reasons,
    )
    medmcqa_long = [row for row in medmcqa_pool if row["length_bucket"] == "long"]
    medmcqa_short = [row for row in medmcqa_pool if row["length_bucket"] == "short"]

    selected = []
    selected.extend(stratified_sample(medqa_pool, args.medqa_candidates, args.seed + 1))
    selected.extend(stratified_sample(medmcqa_long, args.medmcqa_long_candidates, args.seed + 2))
    selected.extend(stratified_sample(medmcqa_short, args.medmcqa_short_candidates, args.seed + 3))
    rng = random.Random(args.seed)
    rng.shuffle(selected)

    write_jsonl(args.candidate_output, selected)

    source_counts = Counter(row["source"] for row in selected)
    length_counts = Counter(f"{row['source']}/{row['length_bucket']}" for row in selected)
    subject_counts = Counter(
        row.get("subject") or "<EMPTY>" for row in selected if row["source"] == "medmcqa"
    )
    lines = [
        "# GRPO v1 Difficulty Candidate Pool",
        "",
        f"- output: `{args.candidate_output}`",
        f"- selected_rows: {len(selected)}",
        f"- sft_seen_ids_excluded: {len(seen_ids)}",
        f"- long_threshold: {args.long_threshold}",
        f"- seed: {args.seed}",
        "",
        "## Source Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(source_counts.items())],
        "",
        "## Length Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(length_counts.items())],
        "",
        "## MedMCQA Subject Top 30",
        "",
        *[f"- `{key}`: {value}" for key, value in subject_counts.most_common(30)],
        "",
        "## Filter Reasons",
        "",
        *[f"- `{key}`: {value}" for key, value in reasons.most_common()],
    ]
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Candidate pool built.")
    print(f"  rows: {len(selected)}")
    print(f"  output: {args.candidate_output}")
    print(f"  report: {args.report_path}")


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


def post_chat_completions(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    num_generations: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
    timeout: float,
    retries: int,
) -> tuple[list[str], str]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "n": num_generations,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    last_error = ""
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            choices = data.get("choices") or []
            responses = [
                clean_text(choice.get("message", {}).get("content", ""))
                for choice in choices
                if isinstance(choice, dict)
            ]
            return responses, ""
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            KeyError,
            IndexError,
            json.JSONDecodeError,
        ) as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    return [], last_error


def sample_one(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    responses, error = post_chat_completions(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        prompt=row["prompt"],
        num_generations=args.num_generations,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        retries=args.retries,
    )
    gold = row["answer"]
    strict_preds = [strict_answer(response) for response in responses]
    loose_preds = [loose_answer(response) for response in responses]
    strict_correct = [pred == gold for pred in strict_preds]
    loose_correct = [pred == gold for pred in loose_preds]
    correct_count = sum(bool(value) for value in loose_correct)
    result = dict(row)
    result.update(
        {
            "difficulty_model": args.model,
            "num_generations_requested": args.num_generations,
            "num_generations_returned": len(responses),
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens,
            "responses": responses,
            "pred_strict": strict_preds,
            "pred_loose": loose_preds,
            "strict_correct": strict_correct,
            "loose_correct": loose_correct,
            "correct_count": correct_count,
            "difficulty_bucket": BUCKET_LABELS.get(correct_count, f"{correct_count}_of_n"),
            "error": error,
        }
    )
    return result


def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    for row in read_jsonl(path):
        sample_id = clean_text(row.get("id"))
        if sample_id:
            ids.add(sample_id)
    return ids


def sample_difficulty(args: argparse.Namespace) -> None:
    rows = read_jsonl(args.candidate_input)
    if args.max_rows > 0:
        rows = rows[: args.max_rows]
    done = completed_ids(args.output) if args.resume else set()
    pending = [row for row in rows if clean_text(row.get("id")) not in done]
    args.output.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    processed = 0
    total = len(pending)
    error_count = 0
    mode = "a" if args.resume and args.output.exists() else "w"
    with args.output.open(mode, encoding="utf-8") as f:
        with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_id = {executor.submit(sample_one, row, args): row["id"] for row in pending}
            for future in futures.as_completed(future_to_id):
                result = future.result()
                if result.get("error"):
                    error_count += 1
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                processed += 1
                if args.progress_every > 0 and processed % args.progress_every == 0:
                    elapsed = time.time() - start
                    print(
                        f"Progress: {processed}/{total} "
                        f"({100 * processed / total:.2f}%) elapsed={elapsed:.1f}s "
                        f"errors={error_count}",
                        flush=True,
                    )

    all_results = read_jsonl(args.output)
    write_difficulty_report(args.report_path, all_results, args)
    print("Difficulty sampling finished.")
    print(f"  output: {args.output}")
    print(f"  report: {args.report_path}")


def write_difficulty_report(path: Path, rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    source_counts = Counter(row["source"] for row in rows)
    bucket_counts = Counter(row.get("difficulty_bucket") or "<EMPTY>" for row in rows)
    source_bucket_counts = Counter(
        f"{row.get('source')}/{row.get('difficulty_bucket')}" for row in rows
    )
    error_count = sum(1 for row in rows if row.get("error"))
    returned_counts = Counter(row.get("num_generations_returned") for row in rows)
    lines = [
        "# GRPO v1 Difficulty Sampling",
        "",
        f"- candidate_input: `{args.candidate_input}`",
        f"- output: `{args.output}`",
        f"- model: `{args.model}`",
        f"- num_generations: {args.num_generations}",
        f"- temperature: {args.temperature}",
        f"- top_p: {args.top_p}",
        f"- max_tokens: {args.max_tokens}",
        f"- total_rows: {len(rows)}",
        f"- error_rows: {error_count}",
        "",
        "## Source Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(source_counts.items())],
        "",
        "## Difficulty Bucket Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(bucket_counts.items())],
        "",
        "## Source x Difficulty Bucket",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(source_bucket_counts.items())],
        "",
        "## Returned Generation Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(returned_counts.items())],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def bucket_quotas(size: int) -> dict[int, int]:
    quotas = {bucket: int(size * weight) for bucket, weight in BUCKET_WEIGHTS.items()}
    remaining = size - sum(quotas.values())
    order = [2, 1, 3, 0, 4]
    idx = 0
    while remaining > 0:
        quotas[order[idx % len(order)]] += 1
        remaining -= 1
        idx += 1
    return quotas


def successful_difficulty_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for row in read_jsonl(path):
        if row.get("error"):
            continue
        if int(row.get("num_generations_returned") or 0) <= 0:
            continue
        rows.append(row)
    return rows


def select_by_bucket(rows: list[dict[str, Any]], size: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    by_bucket: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_bucket[int(row.get("correct_count") or 0)].append(row)
    for bucket_rows in by_bucket.values():
        rng.shuffle(bucket_rows)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    quotas = bucket_quotas(size)

    for bucket in [2, 1, 3, 0, 4]:
        quota = quotas[bucket]
        for row in by_bucket.get(bucket, []):
            if quota <= 0:
                break
            if row["id"] in selected_ids:
                continue
            selected.append(row)
            selected_ids.add(row["id"])
            quota -= 1

    if len(selected) < size:
        fallback = [row for row in rows if row["id"] not in selected_ids]
        fallback.sort(key=lambda row: (abs(int(row.get("correct_count") or 0) - 2), rng.random()))
        for row in fallback:
            if len(selected) >= size:
                break
            selected.append(row)
            selected_ids.add(row["id"])

    if len(selected) < size:
        raise RuntimeError(f"selected {len(selected)} rows, expected {size}")
    rng.shuffle(selected)
    return selected[:size]


def select_source_rows(
    rows: list[dict[str, Any]],
    *,
    source: str,
    size: int,
    seed: int,
) -> list[dict[str, Any]]:
    source_rows = [row for row in rows if row.get("source") == source]
    if source == "medmcqa":
        long_target = size // 2
        short_target = size - long_target
        long_rows = [row for row in source_rows if row.get("length_bucket") == "long"]
        short_rows = [row for row in source_rows if row.get("length_bucket") == "short"]
        selected = select_by_bucket(long_rows, long_target, seed + 11)
        selected.extend(select_by_bucket(short_rows, short_target, seed + 12))
        random.Random(seed).shuffle(selected)
        return selected
    return select_by_bucket(source_rows, size, seed)


def verl_row(row: dict[str, Any], *, split: str) -> dict[str, Any]:
    return {
        "data_source": "medical_mcqa",
        "prompt": [{"role": "user", "content": row["prompt"]}],
        "ability": "medical_mcqa",
        "reward_model": {"style": "rule", "ground_truth": row["answer"]},
        "extra_info": {
            "id": row["id"],
            "source": row["source"],
            "split": split,
            "subject": row.get("subject", ""),
            "topic": row.get("topic", ""),
            "answer_text": row.get("answer_text", ""),
            "options": row.get("options", {}),
            "question_chars": row.get("question_chars", 0),
            "length_bucket": row.get("length_bucket", ""),
            "correct_count": row.get("correct_count"),
            "difficulty_bucket": row.get("difficulty_bucket"),
            "difficulty_model": row.get("difficulty_model"),
        },
    }


def select_grpo(args: argparse.Namespace) -> None:
    rows = successful_difficulty_rows(args.difficulty_input)
    rng = random.Random(args.seed)
    rng.shuffle(rows)

    val_medqa = round(args.val_size * args.medqa_train_size / args.train_size)
    val_medmcqa = args.val_size - val_medqa
    targets = {
        ("medqa", "train"): args.medqa_train_size,
        ("medmcqa", "train"): args.medmcqa_train_size,
        ("medqa", "val"): val_medqa,
        ("medmcqa", "val"): val_medmcqa,
    }

    selected_raw: dict[str, list[dict[str, Any]]] = {"train": [], "val": []}
    used_ids: set[str] = set()
    for split in ["val", "train"]:
        for source in ["medqa", "medmcqa"]:
            source_rows = [row for row in rows if row["id"] not in used_ids]
            chosen = select_source_rows(
                source_rows,
                source=source,
                size=targets[(source, split)],
                seed=args.seed + (1 if split == "train" else 100) + (0 if source == "medqa" else 10),
            )
            selected_raw[split].extend(chosen)
            used_ids.update(row["id"] for row in chosen)
        rng.shuffle(selected_raw[split])

    train_verl = [verl_row(row, split="train") for row in selected_raw["train"]]
    val_verl = [verl_row(row, split="val") for row in selected_raw["val"]]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_jsonl = args.output_dir / "train.jsonl"
    val_jsonl = args.output_dir / "val.jsonl"
    train_parquet = args.output_dir / "train.parquet"
    val_parquet = args.output_dir / "val.parquet"
    selected_debug = args.output_dir / "selected_debug.jsonl"

    write_jsonl(train_jsonl, train_verl)
    write_jsonl(val_jsonl, val_verl)
    write_parquet(train_parquet, train_verl)
    write_parquet(val_parquet, val_verl)
    write_jsonl(selected_debug, selected_raw["train"] + selected_raw["val"])
    write_selection_report(args.report_path, selected_raw, rows, args)

    print("GRPO data selected.")
    print(f"  train: {len(train_verl)} -> {train_parquet}")
    print(f"  val: {len(val_verl)} -> {val_parquet}")
    print(f"  report: {args.report_path}")


def write_selection_report(
    path: Path,
    selected_raw: dict[str, list[dict[str, Any]]],
    eligible_rows: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    all_selected = selected_raw["train"] + selected_raw["val"]

    def counts(rows: list[dict[str, Any]], key: str) -> Counter[str]:
        values: list[str] = []
        for row in rows:
            value = row.get(key)
            values.append("<EMPTY>" if value is None or value == "" else str(value))
        return Counter(values)

    rows_table = []
    for split in ["train", "val"]:
        split_rows = selected_raw[split]
        source_counts = counts(split_rows, "source")
        bucket_counts = counts(split_rows, "correct_count")
        length_counts = Counter(
            f"{row.get('source')}/{row.get('length_bucket')}" for row in split_rows
        )
        rows_table.append([split, "total", len(split_rows)])
        for source, count in sorted(source_counts.items()):
            rows_table.append([split, f"source:{source}", count])
        for bucket, count in sorted(bucket_counts.items()):
            rows_table.append([split, f"correct_count:{bucket}", count])
        for length_key, count in sorted(length_counts.items()):
            rows_table.append([split, f"length:{length_key}", count])

    subject_counts = Counter(
        row.get("subject") or "<EMPTY>" for row in all_selected if row.get("source") == "medmcqa"
    )
    eligible_bucket_counts = counts(eligible_rows, "correct_count")
    lines = [
        "# GRPO v1 10k Selection",
        "",
        f"- difficulty_input: `{args.difficulty_input}`",
        f"- output_dir: `{args.output_dir}`",
        f"- eligible_rows: {len(eligible_rows)}",
        f"- train_size: {len(selected_raw['train'])}",
        f"- val_size: {len(selected_raw['val'])}",
        f"- seed: {args.seed}",
        "",
        "## Eligible Difficulty Buckets",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(eligible_bucket_counts.items())],
        "",
        "## Selected Counts",
        "",
        *markdown_table(["split", "metric", "count"], rows_table),
        "",
        "## Selected MedMCQA Subject Top 30",
        "",
        *[f"- `{key}`: {value}" for key, value in subject_counts.most_common(30)],
        "",
        "## Output Files",
        "",
        f"- `{args.output_dir / 'train.jsonl'}`",
        f"- `{args.output_dir / 'train.parquet'}`",
        f"- `{args.output_dir / 'val.jsonl'}`",
        f"- `{args.output_dir / 'val.parquet'}`",
        f"- `{args.output_dir / 'selected_debug.jsonl'}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.command == "build-candidates":
        build_candidates(args)
    elif args.command == "sample-difficulty":
        sample_difficulty(args)
    elif args.command == "select-grpo":
        select_grpo(args)
    else:
        raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
