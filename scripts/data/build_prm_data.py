"""Build pairwise process reward model data from clean medical CoT SFT data.

The first PRM version treats the reviewed teacher CoT as the preferred
response and creates rejected responses by either reusing real quality-filtered
teacher rejects for the same question or applying deterministic, data-grounded
process perturbations to the clean reasoning.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
DEFAULT_CLEAN_INPUT = Path(
    "data/sft/v3_12866_train_prop_topup2866/medical_cot_sft_train.clean_13k.jsonl"
)
DEFAULT_REJECTED_INPUTS = (
    Path("data/sft/v3_13k_train_prop_topup3k_retry/teacher_generated_sft_rejected_quality.jsonl"),
    Path("data/sft/v2_11k/teacher_generated_sft_rejected_quality.jsonl"),
    Path("data/sft/v2_eval1000/teacher_generated_sft_rejected_quality.jsonl"),
    Path("data/sft/v2_eval300/teacher_generated_sft_rejected_quality.jsonl"),
)
DEFAULT_OUTPUT_DIR = Path("data/prm/v1_12866_process_rm")
DEFAULT_REPORT_PATH = Path("docs/data_stats_prm_v1_12866.md")
DEFAULT_DATASET_PREFIX = "medical_prm_v1_12866_pairwise"
DEFAULT_INSTRUCTION = (
    "Please solve the following medical multiple-choice question with "
    "step-by-step reasoning. Put your reasoning inside <think></think> and "
    "the final answer inside <answer></answer>."
)

THINK_RE = re.compile(r"<think>(.*?)</think>", re.IGNORECASE | re.DOTALL)
STEP_RE = re.compile(
    r"\bStep\s+(\d+)\s*:\s*(.*?)(?=\n\s*Step\s+\d+\s*:|\n\s*</think>|$)",
    re.IGNORECASE | re.DOTALL,
)
ANSWER_TAG_RE = re.compile(r"<answer>\s*([A-D])\s*</answer>", re.IGNORECASE | re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build pairwise PRM/RM data.")
    parser.add_argument(
        "--clean-inputs",
        nargs="+",
        type=Path,
        default=[DEFAULT_CLEAN_INPUT],
        help="Clean SFT JSONL files with instruction/input/output/answer fields.",
    )
    parser.add_argument(
        "--rejected-inputs",
        nargs="*",
        type=Path,
        default=list(DEFAULT_REJECTED_INPUTS),
        help="Optional rejected-quality JSONL files. Matching ids become hard negatives.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--dataset-prefix", default=DEFAULT_DATASET_PREFIX)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-samples", type=int, default=-1)
    parser.add_argument("--negatives-per-sample", type=int, default=2)
    parser.add_argument("--val-ratio", type=float, default=0.02)
    parser.add_argument("--min-steps", type=int, default=2)
    parser.add_argument("--max-output-chars", type=int, default=4096)
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def strip_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def split_think_content(output: str) -> str:
    match = THINK_RE.search(output)
    return match.group(1).strip() if match else ""


def extract_steps(output: str) -> list[str]:
    think = split_think_content(output)
    return [clean_text(match.group(2)) for match in STEP_RE.finditer(think)]


def extract_answer(output: str) -> str:
    matches = ANSWER_TAG_RE.findall(output)
    return matches[-1].upper() if matches else ""


def format_output(steps: list[str], answer: str) -> str:
    rendered_steps = [
        f"Step {index}: {clean_text(step)}" for index, step in enumerate(steps, start=1)
    ]
    return "<think>\n" + "\n".join(rendered_steps) + f"\n</think>\n<answer>{answer}</answer>"


def normalize_options(sample: dict[str, Any]) -> dict[str, str]:
    options = sample.get("options")
    if not isinstance(options, dict):
        return {}
    return {letter: clean_text(options.get(letter)) for letter in LETTERS}


def sample_id(sample: dict[str, Any]) -> str:
    return clean_text(sample.get("id") or sample.get("question_id"))


def validate_clean_sample(
    sample: dict[str, Any],
    *,
    min_steps: int,
    max_output_chars: int,
) -> str | None:
    if not sample_id(sample):
        return "missing_id"
    if not strip_text(sample.get("instruction")):
        return "missing_instruction"
    if not strip_text(sample.get("input")):
        return "missing_input"
    output = strip_text(sample.get("output"))
    if not output:
        return "missing_output"
    if len(output) > max_output_chars:
        return "output_too_long"
    answer = clean_text(sample.get("answer")).upper()
    if answer not in LETTERS:
        return "invalid_answer"
    if extract_answer(output) != answer:
        return "answer_tag_mismatch"
    if len(extract_steps(output)) < min_steps:
        return "too_few_steps"
    return None


def load_clean_samples(args: argparse.Namespace) -> tuple[list[dict[str, Any]], Counter[str]]:
    rows: list[dict[str, Any]] = []
    filtered: Counter[str] = Counter()
    seen_ids: set[str] = set()

    for path in args.clean_inputs:
        if not path.exists():
            raise FileNotFoundError(f"Missing clean input: {path}")
        for sample in read_jsonl(path):
            if args.max_samples > 0 and len(rows) >= args.max_samples:
                break
            reason = validate_clean_sample(
                sample,
                min_steps=args.min_steps,
                max_output_chars=args.max_output_chars,
            )
            if reason:
                filtered[reason] += 1
                continue
            sid = sample_id(sample)
            if sid in seen_ids:
                filtered["duplicate_id"] += 1
                continue
            seen_ids.add(sid)
            rows.append(sample)
    return rows, filtered


def unwrap_rejected_sample(row: dict[str, Any]) -> dict[str, Any]:
    nested = row.get("sample")
    return nested if isinstance(nested, dict) else row


def load_rejected_by_id(paths: list[Path]) -> dict[str, list[dict[str, Any]]]:
    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in paths:
        if not path.exists():
            print(f"WARNING: missing rejected input: {path}", file=sys.stderr)
            continue
        for row in read_jsonl(path):
            sample = unwrap_rejected_sample(row)
            sid = sample_id(sample)
            output = strip_text(sample.get("output"))
            if sid and output:
                by_id[sid].append(
                    {
                        "output": output,
                        "reject_reasons": row.get("reject_reasons", []),
                        "path": str(path),
                    }
                )
    return by_id


def choose_wrong_answer(sample: dict[str, Any], rng: random.Random) -> str:
    answer = clean_text(sample.get("answer")).upper()
    choices = [letter for letter in LETTERS if letter != answer]
    return rng.choice(choices)


def option_text(sample: dict[str, Any], letter: str) -> str:
    return normalize_options(sample).get(letter, "")


def build_real_rejected_negatives(
    sample: dict[str, Any],
    rejected_by_id: dict[str, list[dict[str, Any]]],
) -> list[tuple[str, str, dict[str, Any]]]:
    chosen = strip_text(sample.get("output"))
    candidates: list[tuple[str, str, dict[str, Any]]] = []
    for rejected in rejected_by_id.get(sample_id(sample), []):
        output = strip_text(rejected.get("output"))
        if not output or output == chosen:
            continue
        candidates.append(
            (
                "real_rejected_quality",
                output,
                {
                    "reject_reasons": rejected.get("reject_reasons", []),
                    "rejected_source": rejected.get("path", ""),
                },
            )
        )
    return candidates


def build_truncated_negative(sample: dict[str, Any], steps: list[str]) -> tuple[str, str] | None:
    if len(steps) < 3:
        return None
    keep = max(1, min(len(steps) - 1, len(steps) // 2))
    return "truncated_reasoning", format_output(steps[:keep], clean_text(sample.get("answer")).upper())


def build_drop_final_support_negative(
    sample: dict[str, Any],
    steps: list[str],
) -> tuple[str, str] | None:
    if len(steps) < 3:
        return None
    return (
        "missing_final_support_step",
        format_output(steps[:-1], clean_text(sample.get("answer")).upper()),
    )


def build_shuffled_negative(
    sample: dict[str, Any],
    steps: list[str],
    rng: random.Random,
) -> tuple[str, str] | None:
    if len(steps) < 4:
        return None
    shuffled = steps[:]
    rng.shuffle(shuffled)
    if shuffled == steps:
        shuffled = list(reversed(shuffled))
    return "shuffled_reasoning_order", format_output(shuffled, clean_text(sample.get("answer")).upper())


def build_generic_negative(sample: dict[str, Any]) -> tuple[str, str]:
    answer = clean_text(sample.get("answer")).upper()
    answer_text = clean_text(sample.get("answer_text")) or option_text(sample, answer)
    answer_clause = f"option {answer}"
    if answer_text:
        answer_clause += f", {answer_text}"
    steps = [
        "The question stem is reviewed and the answer choices are compared in a general way.",
        f"The selected choice is {answer_clause}, because it appears to match the topic.",
        "The remaining choices are treated as less appropriate without a specific clinical distinction.",
    ]
    if clean_text(sample.get("quality_tier")).upper() == "A":
        steps.insert(
            1,
            "The key findings should be connected to a mechanism, diagnosis, or management step.",
        )
    return "generic_low_signal_reasoning", format_output(steps, answer)


def build_unsupported_wrong_negative(
    sample: dict[str, Any],
    steps: list[str],
    rng: random.Random,
) -> tuple[str, str]:
    wrong = choose_wrong_answer(sample, rng)
    wrong_text = option_text(sample, wrong)
    first_step = steps[0] if steps else "The question stem contains clinical details that need interpretation."
    final_step = f"The findings are therefore best explained by option {wrong}"
    if wrong_text:
        final_step += f", {wrong_text}"
    final_step += "."
    return "unsupported_wrong_answer_step", format_output([first_step, final_step], wrong)


def build_answer_flip_negative(
    sample: dict[str, Any],
    rng: random.Random,
) -> tuple[str, str]:
    wrong = choose_wrong_answer(sample, rng)
    output = ANSWER_TAG_RE.sub(f"<answer>{wrong}</answer>", strip_text(sample.get("output")), count=1)
    return "answer_tag_flip", output


def build_negative_candidates(
    sample: dict[str, Any],
    rejected_by_id: dict[str, list[dict[str, Any]]],
    rng: random.Random,
) -> list[tuple[str, str, dict[str, Any]]]:
    steps = extract_steps(strip_text(sample.get("output")))
    candidates = build_real_rejected_negatives(sample, rejected_by_id)

    for generated in (
        build_truncated_negative(sample, steps),
        build_drop_final_support_negative(sample, steps),
        build_shuffled_negative(sample, steps, rng),
        build_unsupported_wrong_negative(sample, steps, rng),
        build_generic_negative(sample),
        build_answer_flip_negative(sample, rng),
    ):
        if generated is None:
            continue
        negative_type, output = generated
        candidates.append((negative_type, output, {}))

    deduped: list[tuple[str, str, dict[str, Any]]] = []
    seen_outputs: set[str] = {strip_text(sample.get("output"))}
    for negative_type, output, metadata in candidates:
        output = strip_text(output)
        if not output or output in seen_outputs:
            continue
        seen_outputs.add(output)
        deduped.append((negative_type, output, metadata))
    return deduped


def make_pair_row(
    sample: dict[str, Any],
    rejected_output: str,
    negative_type: str,
    pair_index: int,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    sid = sample_id(sample)
    row = {
        "id": f"{sid}_prm_pair_{pair_index:02d}_{negative_type}",
        "question_id": sid,
        "source": clean_text(sample.get("source")),
        "split": clean_text(sample.get("split")),
        "instruction": strip_text(sample.get("instruction")) or DEFAULT_INSTRUCTION,
        "input": strip_text(sample.get("input")),
        "chosen": strip_text(sample.get("output")),
        "rejected": strip_text(rejected_output),
        "answer": clean_text(sample.get("answer")).upper(),
        "answer_text": clean_text(sample.get("answer_text")),
        "quality_tier": clean_text(sample.get("quality_tier")),
        "question_type": clean_text(sample.get("question_type")),
        "expected_step_range": clean_text(sample.get("expected_step_range")),
        "negative_type": negative_type,
        "cot_source": clean_text(sample.get("cot_source")),
        "chosen_step_count": len(extract_steps(strip_text(sample.get("output")))),
        "rejected_step_count": len(extract_steps(strip_text(rejected_output))),
    }
    if metadata:
        row["negative_metadata"] = metadata
    return row


def split_samples(
    samples: list[dict[str, Any]],
    *,
    val_ratio: float,
    rng: random.Random,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    shuffled = samples[:]
    rng.shuffle(shuffled)
    if val_ratio <= 0 or len(shuffled) < 2:
        return shuffled, []
    val_count = int(round(len(shuffled) * val_ratio))
    val_count = min(max(1, val_count), len(shuffled) - 1)
    return shuffled[val_count:], shuffled[:val_count]


def build_pairs_for_samples(
    samples: list[dict[str, Any]],
    rejected_by_id: dict[str, list[dict[str, Any]]],
    *,
    negatives_per_sample: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sample in samples:
        candidates = build_negative_candidates(sample, rejected_by_id, rng)
        for pair_index, (negative_type, output, metadata) in enumerate(
            candidates[:negatives_per_sample],
            start=1,
        ):
            rows.append(make_pair_row(sample, output, negative_type, pair_index, metadata))
    rng.shuffle(rows)
    return rows


def write_dataset_info(output_dir: Path, dataset_prefix: str) -> None:
    dataset_info = {
        f"{dataset_prefix}_train": {
            "file_name": "prm_pairwise_train.jsonl",
            "formatting": "alpaca",
            "ranking": True,
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "chosen": "chosen",
                "rejected": "rejected",
            },
        },
        f"{dataset_prefix}_val": {
            "file_name": "prm_pairwise_val.jsonl",
            "formatting": "alpaca",
            "ranking": True,
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "chosen": "chosen",
                "rejected": "rejected",
            },
        },
    }
    (output_dir / "dataset_info.json").write_text(
        json.dumps(dataset_info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def avg(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_report(
    path: Path,
    *,
    clean_samples: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    val_rows: list[dict[str, Any]],
    filtered: Counter[str],
    seed: int,
    negatives_per_sample: int,
    val_ratio: float,
    output_dir: Path,
) -> None:
    all_pairs = train_rows + val_rows
    source_counts = Counter(row["source"] or "unknown" for row in all_pairs)
    negative_counts = Counter(row["negative_type"] for row in all_pairs)
    answer_counts = Counter(row["answer"] for row in all_pairs)
    tier_counts = Counter(row["quality_tier"] or "unknown" for row in all_pairs)
    chosen_lengths = [len(row["chosen"]) for row in all_pairs]
    rejected_lengths = [len(row["rejected"]) for row in all_pairs]
    chosen_steps = Counter(row["chosen_step_count"] for row in all_pairs)
    rejected_steps = Counter(row["rejected_step_count"] for row in all_pairs)

    lines = [
        "# PRM pairwise data stats",
        "",
        f"- seed: `{seed}`",
        f"- output_dir: `{output_dir}`",
        f"- clean_samples: {len(clean_samples)}",
        f"- negatives_per_sample: {negatives_per_sample}",
        f"- val_ratio: {val_ratio}",
        "",
        "## Pair counts",
        "",
        f"- train_pairs: {len(train_rows)}",
        f"- val_pairs: {len(val_rows)}",
        f"- total_pairs: {len(all_pairs)}",
        "",
        "## Lengths",
        "",
        f"- avg_chosen_chars: {avg(chosen_lengths):.2f}",
        f"- avg_rejected_chars: {avg(rejected_lengths):.2f}",
        "",
        "## Negative types",
        "",
    ]
    for key, count in negative_counts.most_common():
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## Sources", ""])
    for key, count in source_counts.most_common():
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## Answers", ""])
    for key, count in answer_counts.most_common():
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## Quality tiers", ""])
    for key, count in tier_counts.most_common():
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## Chosen step counts", ""])
    for key, count in sorted(chosen_steps.items()):
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## Rejected step counts", ""])
    for key, count in sorted(rejected_steps.items()):
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## Filtered clean samples", ""])
    if filtered:
        for key, count in filtered.most_common():
            lines.append(f"- {key}: {count}")
    else:
        lines.append("- none")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_prm_data(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    clean_samples, filtered = load_clean_samples(args)
    if not clean_samples:
        raise RuntimeError("No clean samples loaded.")

    rejected_by_id = load_rejected_by_id(args.rejected_inputs)
    train_samples, val_samples = split_samples(clean_samples, val_ratio=args.val_ratio, rng=rng)
    train_rows = build_pairs_for_samples(
        train_samples,
        rejected_by_id,
        negatives_per_sample=args.negatives_per_sample,
        rng=rng,
    )
    val_rows = build_pairs_for_samples(
        val_samples,
        rejected_by_id,
        negatives_per_sample=args.negatives_per_sample,
        rng=rng,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "prm_pairwise_train.jsonl", train_rows)
    write_jsonl(args.output_dir / "prm_pairwise_val.jsonl", val_rows)
    write_dataset_info(args.output_dir, args.dataset_prefix)
    write_report(
        args.report_path,
        clean_samples=clean_samples,
        train_rows=train_rows,
        val_rows=val_rows,
        filtered=filtered,
        seed=args.seed,
        negatives_per_sample=args.negatives_per_sample,
        val_ratio=args.val_ratio,
        output_dir=args.output_dir,
    )

    print(f"Clean samples: {len(clean_samples)}")
    print(f"PRM train pairs: {len(train_rows)}")
    print(f"PRM val pairs: {len(val_rows)}")
    print(f"PRM data written to: {args.output_dir}")
    print(f"PRM stats written to: {args.report_path}")


def main() -> None:
    args = parse_args()
    try:
        build_prm_data(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[build_prm_data] failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
