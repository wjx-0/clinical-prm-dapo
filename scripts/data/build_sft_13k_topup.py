"""Build a MedMCQA subject-proportional SFT top-up.

This script intentionally does not regenerate the existing 10k SFT set. It
selects new MedMCQA teacher inputs that reduce subject-distribution gaps
relative to the processed MedMCQA train split, then can assemble a final 13k
SFT file from the old 10k plus 3k accepted top-up rows.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_TEACHER_INPUTS_PATH = PROJECT_ROOT / "scripts/data/build_teacher_inputs.py"
FILTER_TEACHER_SFT_PATH = PROJECT_ROOT / "scripts/data/filter_teacher_sft.py"
LETTERS = ("A", "B", "C", "D")
METADATA_FIELDS = {
    "quality_tier",
    "question_type",
    "clinical_score",
    "expected_step_range",
    "cot_source",
}
QUESTION_RE = re.compile(r"Question:\n(.+?)\n\nOptions:", flags=re.DOTALL)
STEP_RE = re.compile(r"\bStep\s+(\d+)\s*:", flags=re.IGNORECASE)
ANSWER_TAG_RE = re.compile(r"<answer>\s*([A-D])\s*</answer>", flags=re.IGNORECASE)
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
VISUAL_DEPENDENT_RE = re.compile(
    r"\b(image|picture|figure|photograph|photomicrograph)\b"
    r"|\b(shown in|is shown|are shown|shown below|shown above)\b"
    r"|\b(given below|given above|as follows below|below features)\b"
    r"|\b(the following|following)\s+(ecg|ekg|x-?ray|ct|mri|ultrasound)\b"
    r"|\b(ecg|ekg|x-?ray|ct|mri|ultrasound)\s+(?:was|is)\s+(?:given|obtained|taken)\b"
    r"|\b(x-?ray|ct|mri|ultrasound|biopsy specimen|gross specimen|histologic section)"
    r"\s+(?:is\s+)?shown\b",
    flags=re.IGNORECASE,
)


def load_build_teacher_inputs_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "build_teacher_inputs", BUILD_TEACHER_INPUTS_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {BUILD_TEACHER_INPUTS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BTI = load_build_teacher_inputs_module()


def load_filter_teacher_sft_module() -> Any:
    spec = importlib.util.spec_from_file_location("filter_teacher_sft", FILTER_TEACHER_SFT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {FILTER_TEACHER_SFT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FTS = load_filter_teacher_sft_module()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    select = subparsers.add_parser("select-inputs")
    select.add_argument(
        "--processed-medmcqa-train",
        type=Path,
        default=Path("data/processed/medmcqa_train.jsonl"),
    )
    select.add_argument(
        "--base-sft",
        type=Path,
        default=Path("data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl"),
    )
    select.add_argument(
        "--exclude-jsonl",
        type=Path,
        action="append",
        default=[],
        help="JSONL files whose ids/questions should not be selected.",
    )
    select.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/teacher_inputs/v3_13k_train_prop_topup3k"),
    )
    select.add_argument(
        "--filtered-output",
        type=Path,
        default=Path(
            "outputs/data_validation/"
            "teacher_input_filtered_samples_v3_13k_train_prop_topup3k.jsonl"
        ),
    )
    select.add_argument(
        "--report-path",
        type=Path,
        default=Path("docs/teacher_input_stats_v3_13k_train_prop_topup3k.md"),
    )
    select.add_argument("--target-size", type=int, default=3000)
    select.add_argument("--seed", type=int, default=20260607)
    select.add_argument("--a-min-question-chars", type=int, default=250)
    select.add_argument("--a-min-clinical-score", type=int, default=4)
    select.add_argument(
        "--target-a-ratio",
        type=float,
        default=0.52,
        help="Approximate A-tier ratio within each subject quota.",
    )

    assemble = subparsers.add_parser("assemble-final")
    assemble.add_argument(
        "--processed-medmcqa-train",
        type=Path,
        default=Path("data/processed/medmcqa_train.jsonl"),
    )
    assemble.add_argument(
        "--base-internal",
        type=Path,
        default=Path("data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl"),
    )
    assemble.add_argument(
        "--base-public",
        type=Path,
        default=Path("data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl"),
    )
    assemble.add_argument(
        "--candidate-clean",
        type=Path,
        action="append",
        required=True,
        help="Clean/review-ready top-up candidates. Can be passed multiple times.",
    )
    assemble.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/sft/v3_13k_train_prop"),
    )
    assemble.add_argument(
        "--report-path",
        type=Path,
        default=Path("docs/sft_13k_train_prop_topup_audit.md"),
    )
    assemble.add_argument("--target-topup-size", type=int, default=3000)
    assemble.add_argument("--seed", type=int, default=20260607)

    collect = subparsers.add_parser("collect-local-candidates")
    collect.add_argument(
        "--processed-medmcqa-train",
        type=Path,
        default=Path("data/processed/medmcqa_train.jsonl"),
    )
    collect.add_argument(
        "--base-sft",
        type=Path,
        default=Path("data/sft/v2_11k/medical_cot_sft_train.clean_10k.jsonl"),
    )
    collect.add_argument(
        "--candidate-sft",
        type=Path,
        action="append",
        required=True,
        help="Historical SFT clean/review-ready files to reuse as local candidates.",
    )
    collect.add_argument(
        "--output",
        type=Path,
        default=Path("data/sft/v3_13k_train_prop_local_candidates/local_reusable_clean.jsonl"),
    )
    collect.add_argument(
        "--rejected-output",
        type=Path,
        default=Path(
            "data/sft/v3_13k_train_prop_local_candidates/local_reusable_rejected.jsonl"
        ),
    )
    collect.add_argument(
        "--report-path",
        type=Path,
        default=Path("docs/sft_13k_train_prop_local_candidate_filter.md"),
    )
    collect.add_argument("--a-min-question-chars", type=int, default=250)
    collect.add_argument("--a-min-clinical-score", type=int, default=4)

    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def subject_of(row: dict[str, Any]) -> str:
    return clean_text(row.get("subject")) or "<EMPTY>"


def read_jsonl(path: Path, *, required: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return []
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pct(num: int, den: int) -> str:
    return f"{100 * num / den:.2f}%" if den else "0.00%"


def extract_sft_question(row: dict[str, Any]) -> str:
    input_text = row.get("input")
    if isinstance(input_text, str):
        match = QUESTION_RE.search(input_text)
        if match:
            return clean_text(match.group(1))
        return clean_text(input_text)
    return clean_text(row.get("question"))


def collect_exclusions(paths: list[Path]) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    questions: set[str] = set()
    for path in paths:
        for row in read_jsonl(path, required=False):
            sample = row.get("sample") if isinstance(row.get("sample"), dict) else row
            sample_id = clean_text(sample.get("id"))
            if sample_id:
                ids.add(sample_id)
            question = extract_sft_question(sample)
            if question:
                questions.add(BTI.normalize_question(question))
    return ids, questions


def train_subject_counts(processed_medmcqa_train: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in read_jsonl(processed_medmcqa_train):
        counts[subject_of(row)] += 1
    return counts


def medmcqa_sft_subject_counts(base_sft: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in read_jsonl(base_sft):
        if row.get("source") == "medmcqa":
            counts[subject_of(row)] += 1
    return counts


def compute_deficits(
    *,
    train_counts: Counter[str],
    current_counts: Counter[str],
    target_size: int,
) -> dict[str, dict[str, Any]]:
    current_total = sum(current_counts.values())
    target_total = current_total + target_size
    train_total = sum(train_counts.values())
    rows: dict[str, dict[str, Any]] = {}
    for subject in sorted(train_counts):
        target_after = round(train_counts[subject] / train_total * target_total)
        current = current_counts[subject]
        deficit = max(0, target_after - current)
        rows[subject] = {
            "subject": subject,
            "train_count": train_counts[subject],
            "train_pct": train_counts[subject] / train_total if train_total else 0.0,
            "current_sft": current,
            "target_after_topup": target_after,
            "raw_deficit": deficit,
        }
    return rows


def allocate_quota(deficit_rows: dict[str, dict[str, Any]], target_size: int) -> Counter[str]:
    positive = {
        subject: int(row["raw_deficit"])
        for subject, row in deficit_rows.items()
        if int(row["raw_deficit"]) > 0
    }
    total_deficit = sum(positive.values())
    if total_deficit <= 0:
        return Counter()

    quotas: Counter[str] = Counter()
    remainders: list[tuple[float, int, str]] = []
    for subject, deficit in positive.items():
        exact = deficit * target_size / total_deficit
        base = min(deficit, math.floor(exact))
        quotas[subject] = base
        remainders.append((exact - base, deficit, subject))

    remaining = target_size - sum(quotas.values())
    for _, _, subject in sorted(remainders, reverse=True):
        if remaining <= 0:
            break
        if quotas[subject] >= positive[subject]:
            continue
        quotas[subject] += 1
        remaining -= 1

    return quotas


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---:" if header != "subject" else "---" for header in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return lines


def select_inputs(args: argparse.Namespace) -> None:
    train_counts = train_subject_counts(args.processed_medmcqa_train)
    current_counts = medmcqa_sft_subject_counts(args.base_sft)
    deficit_rows = compute_deficits(
        train_counts=train_counts,
        current_counts=current_counts,
        target_size=args.target_size,
    )
    quotas = allocate_quota(deficit_rows, args.target_size)

    exclude_paths = [args.base_sft, *args.exclude_jsonl]
    excluded_ids, excluded_questions = collect_exclusions(exclude_paths)
    seen_ids = set(excluded_ids)
    seen_questions = set(excluded_questions)

    bti_args = argparse.Namespace(
        a_min_question_chars=args.a_min_question_chars,
        a_min_clinical_score=args.a_min_clinical_score,
    )
    filtered_records: list[dict[str, Any]] = []
    filter_reasons: Counter[str] = Counter()
    candidates_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for sample in read_jsonl(args.processed_medmcqa_train):
        converted, reasons = BTI.validate_and_convert_sample(
            sample,
            seen_ids,
            seen_questions,
            bti_args,
        )
        if converted is None:
            filtered_records.append(BTI.build_filter_record(sample, reasons))
            filter_reasons.update(reasons)
            continue
        subject = subject_of(converted)
        if quotas.get(subject, 0) > 0:
            candidates_by_subject[subject].append(converted)

    rng = random.Random(args.seed)
    random_keys = {
        row["id"]: rng.random()
        for rows in candidates_by_subject.values()
        for row in rows
    }
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    selected_by_subject: Counter[str] = Counter()
    candidate_counts = Counter({subject: len(rows) for subject, rows in candidates_by_subject.items()})

    for subject, rows in candidates_by_subject.items():
        rows.sort(key=lambda row: BTI.candidate_sort_key(row, random_keys))

    selected_tier_by_subject: Counter[tuple[str, str]] = Counter()
    for subject, quota in quotas.items():
        rows = candidates_by_subject.get(subject, [])
        by_tier = {
            "A": [row for row in rows if row.get("quality_tier") == "A"],
            "B": [row for row in rows if row.get("quality_tier") == "B"],
        }
        a_quota = min(len(by_tier["A"]), round(quota * args.target_a_ratio))
        tier_targets = {"A": a_quota, "B": quota - a_quota}

        for tier in ("A", "B"):
            for row in by_tier[tier]:
                if selected_tier_by_subject[(subject, tier)] >= tier_targets[tier]:
                    break
                if row["id"] in selected_ids:
                    continue
                selected.append(BTI.strip_private_fields(row))
                selected_ids.add(row["id"])
                selected_by_subject[subject] += 1
                selected_tier_by_subject[(subject, tier)] += 1

        if selected_by_subject[subject] < quota:
            for row in rows:
                if selected_by_subject[subject] >= quota:
                    break
                if row["id"] in selected_ids:
                    continue
                tier = row.get("quality_tier") or "<EMPTY>"
                selected.append(BTI.strip_private_fields(row))
                selected_ids.add(row["id"])
                selected_by_subject[subject] += 1
                selected_tier_by_subject[(subject, tier)] += 1

    if len(selected) < args.target_size:
        remaining_pool: list[dict[str, Any]] = []
        for subject, rows in candidates_by_subject.items():
            if selected_by_subject[subject] >= quotas[subject]:
                continue
            remaining_pool.extend(row for row in rows if row["id"] not in selected_ids)
        remaining_pool.sort(key=lambda row: BTI.candidate_sort_key(row, random_keys))
        for row in remaining_pool:
            if len(selected) >= args.target_size:
                break
            if row["id"] in selected_ids:
                continue
            selected.append(BTI.strip_private_fields(row))
            selected_ids.add(row["id"])
            selected_by_subject[subject_of(row)] += 1

    if len(selected) != args.target_size:
        raise RuntimeError(f"Selected {len(selected)} rows, expected {args.target_size}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_output = args.output_dir / "teacher_sft_train_inputs.jsonl"
    dev_output = args.output_dir / "teacher_sft_dev_inputs.jsonl"
    write_jsonl(train_output, selected)
    write_jsonl(dev_output, [])
    write_jsonl(args.filtered_output, filtered_records)

    selected_counts = Counter(subject_of(row) for row in selected)
    tier_counts = Counter(row.get("quality_tier") or "<EMPTY>" for row in selected)
    qtype_counts = Counter(row.get("question_type") or "<EMPTY>" for row in selected)
    answer_counts = Counter(row.get("answer") or "<EMPTY>" for row in selected)
    report_rows = []
    for subject, row in sorted(
        deficit_rows.items(),
        key=lambda item: (-int(item[1]["raw_deficit"]), item[0]),
    ):
        if row["raw_deficit"] <= 0 and selected_counts[subject] <= 0:
            continue
        report_rows.append(
            [
                subject,
                row["current_sft"],
                f"{100 * row['train_pct']:.2f}%",
                row["target_after_topup"],
                row["raw_deficit"],
                quotas[subject],
                candidate_counts[subject],
                selected_counts[subject],
            ]
        )

    lines = [
        "# Teacher Input Topup v3_13k_train_prop_topup3k",
        "",
        f"- generated_at_utc: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`",
        f"- seed: `{args.seed}`",
        f"- target_size: {args.target_size}",
        f"- target_a_ratio: {args.target_a_ratio:.2f}",
        f"- output_train: `{train_output}`",
        f"- output_dev: `{dev_output}`",
        f"- base_sft: `{args.base_sft}`",
        f"- processed_medmcqa_train: `{args.processed_medmcqa_train}`",
        f"- excluded_ids: {len(excluded_ids)}",
        f"- excluded_questions: {len(excluded_questions)}",
        "",
        "## Selected Distribution",
        "",
        "### Quality Tier",
        "",
        *[f"- `{key}`: {value}" for key, value in tier_counts.most_common()],
        "",
        "### Question Type",
        "",
        *[f"- `{key}`: {value}" for key, value in qtype_counts.most_common()],
        "",
        "### Answer",
        "",
        *[f"- `{key}`: {value}" for key, value in answer_counts.most_common()],
        "",
        "## Subject Quotas",
        "",
        *markdown_table(
            [
                "subject",
                "sft_now",
                "medmcqa_train_pct",
                "target_after_topup",
                "raw_deficit",
                "quota",
                "candidate_count",
                "selected",
            ],
            report_rows,
        ),
        "",
        "## Filter Reasons Top 30",
        "",
        *[
            f"- `{reason}`: {count}"
            for reason, count in filter_reasons.most_common(30)
        ],
        "",
    ]
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text("\n".join(lines), encoding="utf-8")


def public_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in METADATA_FIELDS}


def hard_audit(rows: list[dict[str, Any]], *, public: bool = False) -> Counter[str]:
    checks: Counter[str] = Counter()
    ids: Counter[str] = Counter()
    for row in rows:
        sample_id = clean_text(row.get("id"))
        ids[sample_id] += 1
        output = row.get("output") if isinstance(row.get("output"), str) else ""
        input_text = row.get("input") if isinstance(row.get("input"), str) else ""
        answer = clean_text(row.get("answer"))
        tags = [match.group(1).upper() for match in ANSWER_TAG_RE.finditer(output)]
        steps = STEP_RE.findall(output)
        tier = clean_text(row.get("quality_tier")).upper()

        if "<think>" not in output or "</think>" not in output:
            checks["missing_think"] += 1
        if len(tags) != 1:
            checks["missing_answer_tag"] += 1
        elif tags[0] != answer:
            checks["answer_mismatch"] += 1
        if tier == "A" and len(steps) not in {4, 5, 6}:
            checks["bad_a_step_count"] += 1
        if tier == "B" and len(steps) not in {2, 3}:
            checks["bad_b_step_count"] += 1
        if SOURCE_NOISE_RE.search(f"{input_text} {clean_text(row.get('answer_text'))}"):
            checks["source_noise"] += 1
        if VISUAL_DEPENDENT_RE.search(input_text):
            checks["visual_dependency"] += 1
        if re.search(
            r"gold answer|provided answer|quality_tier|metadata|data generation",
            output,
            flags=re.IGNORECASE,
        ):
            checks["internal_trace_in_output"] += 1
        if public:
            for field in METADATA_FIELDS:
                if field in row:
                    checks[f"public_has_{field}"] += 1

    checks["duplicate_ids"] = sum(count - 1 for count in ids.values() if count > 1)
    return checks


def select_topup_rows(
    *,
    base_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    processed_medmcqa_train: Path,
    target_size: int,
    seed: int,
) -> tuple[list[dict[str, Any]], Counter[str], dict[str, dict[str, Any]]]:
    current_counts = Counter(
        subject_of(row) for row in base_rows if row.get("source") == "medmcqa"
    )
    train_counts = train_subject_counts(processed_medmcqa_train)
    deficit_rows = compute_deficits(
        train_counts=train_counts,
        current_counts=current_counts,
        target_size=target_size,
    )
    quotas = allocate_quota(deficit_rows, target_size)

    base_ids = {clean_text(row.get("id")) for row in base_rows}
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(candidate_rows):
        if row.get("source") != "medmcqa":
            continue
        if clean_text(row.get("id")) in base_ids:
            continue
        audited = hard_audit([row])
        if any(value for key, value in audited.items() if key != "duplicate_ids"):
            continue
        copy = dict(row)
        copy["_candidate_index"] = index
        by_subject[subject_of(row)].append(copy)

    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()

    def candidate_key(row: dict[str, Any]) -> tuple[int, int, int, int, float]:
        tier_rank = 0 if row.get("quality_tier") == "A" else 1
        qtype_rank = 0 if row.get("question_type") == "clinical_vignette" else 1
        score = int(row.get("clinical_score") or 0)
        output_len = len(row.get("output", ""))
        return (tier_rank, qtype_rank, -score, -output_len, rng.random())

    for rows in by_subject.values():
        rows.sort(key=candidate_key)

    selected_counts: Counter[str] = Counter()
    for subject, quota in quotas.items():
        for row in by_subject.get(subject, []):
            if selected_counts[subject] >= quota:
                break
            sample_id = clean_text(row.get("id"))
            if sample_id in selected_ids:
                continue
            clean_row = {key: value for key, value in row.items() if not key.startswith("_")}
            selected.append(clean_row)
            selected_ids.add(sample_id)
            selected_counts[subject] += 1

    if len(selected) < target_size:
        remainder: list[dict[str, Any]] = []
        for subject, rows in by_subject.items():
            if selected_counts[subject] >= quotas.get(subject, 0):
                continue
            remainder.extend(row for row in rows if clean_text(row.get("id")) not in selected_ids)
        remainder.sort(key=candidate_key)
        for row in remainder:
            if len(selected) >= target_size:
                break
            sample_id = clean_text(row.get("id"))
            if sample_id in selected_ids:
                continue
            clean_row = {key: value for key, value in row.items() if not key.startswith("_")}
            selected.append(clean_row)
            selected_ids.add(sample_id)
            selected_counts[subject_of(row)] += 1

    if len(selected) < target_size:
        remainder = []
        for rows in by_subject.values():
            remainder.extend(row for row in rows if clean_text(row.get("id")) not in selected_ids)
        remainder.sort(key=candidate_key)
        for row in remainder:
            if len(selected) >= target_size:
                break
            sample_id = clean_text(row.get("id"))
            if sample_id in selected_ids:
                continue
            clean_row = {key: value for key, value in row.items() if not key.startswith("_")}
            selected.append(clean_row)
            selected_ids.add(sample_id)
            selected_counts[subject_of(row)] += 1

    if len(selected) != target_size:
        raise RuntimeError(f"Selected {len(selected)} top-up rows, expected {target_size}")

    return selected, quotas, deficit_rows


def build_processed_index(path: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        sample_id = clean_text(row.get("id"))
        if sample_id:
            index[sample_id] = row
    return index


def default_filter_args() -> argparse.Namespace:
    return argparse.Namespace(
        reject_dirty_input=True,
        min_output_chars=120,
        max_output_chars=2500,
        min_steps=4,
        max_steps=6,
        a_min_steps=4,
        a_max_steps=6,
        b_min_steps=2,
        b_max_steps=3,
    )


def rebuild_metadata(
    row: dict[str, Any],
    processed_index: dict[str, dict[str, Any]],
    bti_args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, list[str]]:
    sample_id = clean_text(row.get("id"))
    processed = processed_index.get(sample_id)
    if processed is None:
        return None, ["missing_processed_source"]
    if processed.get("source") != "medmcqa" or processed.get("split") != "train":
        return None, ["not_medmcqa_train"]

    converted, reasons = BTI.validate_and_convert_sample(
        processed,
        seen_ids=set(),
        seen_questions=set(),
        args=bti_args,
    )
    if converted is None:
        return None, [f"teacher_input_{reason}" for reason in reasons]

    updated = dict(row)
    for key in (
        "source",
        "split",
        "answer",
        "answer_text",
        "subject",
        "topic",
        "quality_tier",
        "question_type",
        "clinical_score",
        "expected_step_range",
    ):
        updated[key] = converted.get(key)
    updated["cot_source"] = updated.get("cot_source") or "teacher_generated"
    return updated, []


def collect_local_candidates(args: argparse.Namespace) -> None:
    base_ids = {clean_text(row.get("id")) for row in read_jsonl(args.base_sft)}
    processed_index = build_processed_index(args.processed_medmcqa_train)
    bti_args = argparse.Namespace(
        a_min_question_chars=args.a_min_question_chars,
        a_min_clinical_score=args.a_min_clinical_score,
    )
    filter_args = default_filter_args()

    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    reason_counts: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()
    path_kept: Counter[str] = Counter()

    for path in args.candidate_sft:
        rows = read_jsonl(path)
        path_counts[str(path)] += len(rows)
        for row in rows:
            sample_id = clean_text(row.get("id"))
            reasons: list[str] = []
            if not sample_id:
                reasons.append("missing_id")
            if sample_id in base_ids:
                reasons.append("already_in_base_10k")
            if sample_id in seen_ids:
                reasons.append("duplicate_candidate_id")
            if row.get("source") != "medmcqa":
                reasons.append("not_medmcqa")
            if row.get("split") != "train":
                reasons.append("not_train")

            rebuilt: dict[str, Any] | None = None
            if not reasons:
                rebuilt, metadata_reasons = rebuild_metadata(row, processed_index, bti_args)
                reasons.extend(metadata_reasons)

            if rebuilt is not None and not reasons:
                validation_reasons, dirty_input = FTS.validate_sample(rebuilt, filter_args)
                reasons.extend(validation_reasons)
                if not reasons:
                    audit = hard_audit([rebuilt])
                    hard_failures = [
                        key
                        for key, value in audit.items()
                        if value and key != "duplicate_ids"
                    ]
                    reasons.extend(f"hard_audit_{key}" for key in hard_failures)
            else:
                dirty_input = False

            if reasons:
                reason_counts.update(reasons)
                rejected.append(
                    {
                        "id": sample_id,
                        "source": clean_text(row.get("source")),
                        "split": clean_text(row.get("split")),
                        "reject_reasons": sorted(set(reasons)),
                        "dirty_input": dirty_input,
                        "candidate_path": str(path),
                        "sample": row,
                    }
                )
                continue

            assert rebuilt is not None
            kept.append(FTS.clean_final_row(rebuilt))
            seen_ids.add(sample_id)
            path_kept[str(path)] += 1

    write_jsonl(args.output, kept)
    write_jsonl(args.rejected_output, rejected)

    subject_counts = Counter(subject_of(row) for row in kept)
    tier_counts = Counter(row.get("quality_tier") or "<EMPTY>" for row in kept)
    qtype_counts = Counter(row.get("question_type") or "<EMPTY>" for row in kept)
    step_counts = Counter(len(STEP_RE.findall(row.get("output", ""))) for row in kept)
    audit = hard_audit(kept)

    lines = [
        "# SFT 13k Local Candidate Filter",
        "",
        f"- generated_at_utc: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`",
        f"- base_sft: `{args.base_sft}`",
        f"- processed_medmcqa_train: `{args.processed_medmcqa_train}`",
        f"- output: `{args.output}`",
        f"- rejected_output: `{args.rejected_output}`",
        f"- kept_rows: {len(kept)}",
        f"- rejected_rows: {len(rejected)}",
        "",
        "## Candidate File Counts",
        "",
        *[
            f"- `{path}`: total={path_counts[path]}, kept={path_kept[path]}"
            for path in path_counts
        ],
        "",
        "## Kept Quality Tier",
        "",
        *[f"- `{key}`: {value}" for key, value in tier_counts.most_common()],
        "",
        "## Kept Question Type",
        "",
        *[f"- `{key}`: {value}" for key, value in qtype_counts.most_common()],
        "",
        "## Kept Step Count",
        "",
        *[f"- `{key}`: {value}" for key, value in step_counts.most_common()],
        "",
        "## Kept Subject Top 30",
        "",
        *[f"- `{key}`: {value}" for key, value in subject_counts.most_common(30)],
        "",
        "## Reject Reasons Top 30",
        "",
        *[f"- `{key}`: {value}" for key, value in reason_counts.most_common(30)],
        "",
        "## Hard Audit",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(audit.items())],
        "",
    ]
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text("\n".join(lines), encoding="utf-8")


def assemble_final(args: argparse.Namespace) -> None:
    base_internal = read_jsonl(args.base_internal)
    base_public = read_jsonl(args.base_public)
    candidate_rows: list[dict[str, Any]] = []
    candidate_source_counts: Counter[str] = Counter()
    for path in args.candidate_clean:
        rows = read_jsonl(path)
        candidate_rows.extend(rows)
        candidate_source_counts[str(path)] += len(rows)

    topup_rows, quotas, deficit_rows = select_topup_rows(
        base_rows=base_internal,
        candidate_rows=candidate_rows,
        processed_medmcqa_train=args.processed_medmcqa_train,
        target_size=args.target_topup_size,
        seed=args.seed,
    )

    final_internal = base_internal + topup_rows
    final_public = base_public + [public_row(row) for row in topup_rows]
    topup_public = [public_row(row) for row in topup_rows]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    internal_path = args.output_dir / "medical_cot_sft_train.clean_13k.jsonl"
    public_path = args.output_dir / "medical_cot_sft_train.clean_13k_public.jsonl"
    topup_path = args.output_dir / "medical_cot_sft_train.topup_3k.jsonl"
    topup_public_path = args.output_dir / "medical_cot_sft_train.topup_3k_public.jsonl"
    dataset_info_path = args.output_dir / "dataset_info.json"
    manifest_path = args.output_dir / "medical_cot_sft_train.clean_13k_public.manifest.json"
    sha_path = args.output_dir / "medical_cot_sft_train.clean_13k_public.sha256"

    write_jsonl(internal_path, final_internal)
    write_jsonl(public_path, final_public)
    write_jsonl(topup_path, topup_rows)
    write_jsonl(topup_public_path, topup_public)

    version_label = args.output_dir.name
    dataset_info = {
        f"medical_cot_sft_{version_label}_clean{len(final_public)}": {
            "file_name": public_path.name,
            "formatting": "alpaca",
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "response": "output",
            },
        },
        f"medical_cot_sft_{version_label}_topup{len(topup_public)}": {
            "file_name": topup_public_path.name,
            "formatting": "alpaca",
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "response": "output",
            },
        },
    }
    dataset_info_path.write_text(
        json.dumps(dataset_info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "version": version_label,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": args.seed,
        "base_internal": str(args.base_internal),
        "base_public": str(args.base_public),
        "candidate_clean": [str(path) for path in args.candidate_clean],
        "outputs": {
            "final_internal": {
                "path": str(internal_path),
                "lines": len(final_internal),
                "sha256": sha256_file(internal_path),
            },
            "final_public": {
                "path": str(public_path),
                "lines": len(final_public),
                "sha256": sha256_file(public_path),
            },
            "topup_internal": {
                "path": str(topup_path),
                "lines": len(topup_rows),
                "sha256": sha256_file(topup_path),
            },
            "topup_public": {
                "path": str(topup_public_path),
                "lines": len(topup_public),
                "sha256": sha256_file(topup_public_path),
            },
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    sha_path.write_text(f"{sha256_file(public_path)}  {public_path.name}\n", encoding="utf-8")

    source_counts = Counter(row.get("source") or "<EMPTY>" for row in final_internal)
    topup_subject_counts = Counter(subject_of(row) for row in topup_rows)
    final_medmcqa_subject_counts = Counter(
        subject_of(row) for row in final_internal if row.get("source") == "medmcqa"
    )
    tier_counts = Counter(row.get("quality_tier") or "<EMPTY>" for row in final_internal)
    qtype_counts = Counter(row.get("question_type") or "<EMPTY>" for row in final_internal)
    step_counts = Counter(len(STEP_RE.findall(row.get("output", ""))) for row in final_internal)
    base_audit = hard_audit(base_internal)
    topup_audit = hard_audit(topup_rows)
    internal_audit = hard_audit(final_internal)
    public_audit = hard_audit(final_public, public=True)

    report_rows = []
    train_counts = train_subject_counts(args.processed_medmcqa_train)
    train_total = sum(train_counts.values())
    for subject in sorted(final_medmcqa_subject_counts, key=lambda s: (-topup_subject_counts[s], s)):
        if topup_subject_counts[subject] <= 0:
            continue
        report_rows.append(
            [
                subject,
                topup_subject_counts[subject],
                quotas[subject],
                deficit_rows.get(subject, {}).get("raw_deficit", 0),
                final_medmcqa_subject_counts[subject],
                f"{100 * final_medmcqa_subject_counts[subject] / sum(final_medmcqa_subject_counts.values()):.2f}%",
                f"{100 * train_counts[subject] / train_total:.2f}%",
            ]
        )

    lines = [
        "# SFT Train-Proportional Topup Audit",
        "",
        f"- generated_at_utc: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`",
        f"- base_internal_rows: {len(base_internal)}",
        f"- topup_rows: {len(topup_rows)}",
        f"- final_internal_rows: {len(final_internal)}",
        f"- final_public_rows: {len(final_public)}",
        f"- output_dir: `{args.output_dir}`",
        "",
        "## Candidate Inputs",
        "",
        *[f"- `{path}`: {count}" for path, count in candidate_source_counts.items()],
        "",
        "## Final Source Distribution",
        "",
        *[f"- `{key}`: {value}" for key, value in source_counts.most_common()],
        "",
        "## Final Quality Tier",
        "",
        *[f"- `{key}`: {value}" for key, value in tier_counts.most_common()],
        "",
        "## Final Question Type",
        "",
        *[f"- `{key}`: {value}" for key, value in qtype_counts.most_common()],
        "",
        "## Final Step Count",
        "",
        *[f"- `{key}`: {value}" for key, value in step_counts.most_common()],
        "",
        "## Topup Subject Allocation",
        "",
        *markdown_table(
            [
                "subject",
                "topup_selected",
                "quota",
                "raw_deficit",
                "final_medmcqa_count",
                "final_medmcqa_pct",
                "medmcqa_train_pct",
            ],
            report_rows,
        ),
        "",
        "## Base Hard Audit",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(base_audit.items())],
        "",
        "## Topup Hard Audit",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(topup_audit.items())],
        "",
        "## Final Hard Audit",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(internal_audit.items())],
        "",
        "## Final Public Metadata Audit",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(public_audit.items())],
        "",
        "## Output Files",
        "",
        f"- `{internal_path}`",
        f"- `{public_path}`",
        f"- `{topup_path}`",
        f"- `{topup_public_path}`",
        f"- `{dataset_info_path}`",
        f"- `{manifest_path}`",
        f"- `{sha_path}`",
        "",
    ]
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.command == "select-inputs":
        select_inputs(args)
    elif args.command == "collect-local-candidates":
        collect_local_candidates(args)
    elif args.command == "assemble-final":
        assemble_final(args)
    else:
        raise ValueError(args.command)


if __name__ == "__main__":
    main()
