"""Build teacher-model input candidates from processed QA JSONL files.

This script only selects and normalizes teacher input candidates. It does not
call a teacher model and does not generate CoT, SFT, RL, or PRM data.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import re
import string
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LETTERS = ("A", "B", "C", "D")
VALID_SOURCES = {"medqa", "medmcqa"}
VALID_SPLITS = {"train", "dev"}
QUALITY_ORDER = {"high": 0, "medium": 1, "low": 2, "none": 3}
MAX_NO_EXPLANATION_RATIO = 0.30
DEFAULT_MIN_A_RATIO = 0.75
MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
)
MONTH_YEAR_RE = re.compile(
    rf"(?:(?<=[:;,(])\s*|\b)({'|'.join(MONTH_NAMES)})\.?\s+(?:19|20)\d{{2}}\b",
    flags=re.IGNORECASE,
)
IMAGE_DEPENDENT_RE = re.compile(
    r"\b(image|picture|figure|photograph|photomicrograph)\b"
    r"|\b(shown in|is shown|are shown|shown below|shown above)\b"
    r"|\b(given below|given above|as follows below|below features)\b"
    r"|\b(the following|following)\s+(ecg|ekg|x-?ray|ct|mri|ultrasound)\b"
    r"|\b(ecg|ekg|x-?ray|ct|mri|ultrasound)\s+(?:was|is)\s+(?:given|obtained|taken)\b"
    r"|\b(x-?ray|ct|mri|ultrasound|biopsy specimen|gross specimen|histologic section)"
    r"\s+(?:is\s+)?shown\b",
    flags=re.IGNORECASE,
)
AMBIGUOUS_TRUE_EXCEPT_RE = re.compile(
    r"\b(all\s+(?:of\s+)?the\s+following.*except|except\s*[-?]?\s*$"
    r"|not\s+true|true\s+(?:about|regarding)|statement\(s\)\s+is/are\s+true)\b",
    flags=re.IGNORECASE,
)
COMPOSITE_ANSWER_RE = re.compile(
    r"^(?:all of the above|none of the above|[abcd]{2,4}|[a-d][,+/& ]+[a-d].*)$",
    flags=re.IGNORECASE,
)
EXAM_ARTIFACT_RE = re.compile(r"\b(repeat|not related|previous year|aiims|neet|pgimer)\b", re.I)
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
AGE_RE = re.compile(r"\b\d{1,3}[- ]year[- ]old\b", re.I)
PATIENT_RE = re.compile(r"\b(man|woman|boy|girl|male|female|infant|child|patient)\b", re.I)
PRESENTATION_RE = re.compile(
    r"\b(presents|comes|brought|admitted|complain|complains|reports|develops|history)\b",
    re.I,
)
SYMPTOM_RE = re.compile(
    r"\b(fever|pain|diarrhea|vomit|vomiting|cough|dyspnea|shortness of breath|headache|"
    r"seizure|rash|fatigue|bleeding|weight loss|nausea|weakness|confusion|edema)\b",
    re.I,
)
FINDING_RE = re.compile(
    r"\b(blood pressure|pulse|temperature|respirations|oxygen saturation|laboratory|"
    r"hemoglobin|leukocyte|platelet|serum|urine|ecg|eeg|ct|mri|ultrasound|x-ray|"
    r"biopsy|colonoscopy|physical examination|exam|auscultation)\b",
    re.I,
)
HISTORY_RE = re.compile(
    r"\b(takes|medication|past medical history|family history|smoking|alcohol|drug|"
    r"diabetes|hypertension|pregnancy|surgery)\b",
    re.I,
)
REASONING_ASK_RE = re.compile(
    r"\b(most likely|best explanation|mechanism|next step|treatment|diagnosis|cause|"
    r"management|etiology|finding|drug|therapy|pathogenesis)\b",
    re.I,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build teacher SFT input candidates from processed QA data."
    )
    parser.add_argument("--input_dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output_dir", type=Path, default=Path("data/teacher_inputs"))
    parser.add_argument("--target_train_size", type=int, default=12000)
    parser.add_argument("--target_dev_size", type=int, default=1000)
    parser.add_argument(
        "--min_a_ratio",
        type=float,
        default=DEFAULT_MIN_A_RATIO,
        help="Minimum target fraction of A-tier clinical vignette inputs.",
    )
    parser.add_argument(
        "--a_min_question_chars",
        type=int,
        default=250,
        help="Minimum question length for A-tier clinical vignette candidates.",
    )
    parser.add_argument(
        "--a_min_clinical_score",
        type=int,
        default=4,
        help="Minimum clinical clue score for A-tier candidates.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max_samples",
        type=int,
        default=-1,
        help="If positive, read at most this many rows from each input file.",
    )
    parser.add_argument(
        "--filtered_output",
        type=Path,
        default=Path("outputs/data_validation/teacher_input_filtered_samples.jsonl"),
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/teacher_input_stats.md"),
    )
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def remove_exam_dates(text: str) -> str:
    text = MONTH_YEAR_RE.sub(" ", text)
    text = re.sub(r"\s+([,;:.?!])", r"\1", text)
    text = re.sub(r"[:;,]\s*([)\]}]|$)", r"\1", text)
    return text


def sanitize_text(value: Any, *, remove_dates: bool = False) -> str:
    text = clean_text(value).replace("\x00", " ")
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&;", " ")
    text = re.sub(r"&[A-Za-z][A-Za-z0-9#]+;", " ", text)
    if remove_dates:
        text = remove_exam_dates(text)
    return clean_text(text)


def normalize_question(value: Any) -> str:
    text = sanitize_text(value, remove_dates=True).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def explanation_quality(explanation: str) -> str:
    length = len(clean_text(explanation))
    if length == 0:
        return "none"
    if length < 30:
        return "low"
    if length < 120:
        return "medium"
    return "high"


def has_html_residue(text: str) -> bool:
    lower_text = text.lower()
    html_tokens = ("&nbsp;", "&amp;", "&lt;", "&gt;", "<br", "</", "<p", "<div", "<span")
    return any(token in lower_text for token in html_tokens) or bool(
        re.search(r"<[a-z][^>]*>", lower_text)
    )


def is_dirty_text(question: str, explanation: str) -> bool:
    combined = f"{question} {explanation}"
    cleaned_question = clean_text(question)
    cleaned_explanation = clean_text(explanation)

    if "&;" in combined or "\x00" in combined:
        return True
    if cleaned_question.endswith("...") or cleaned_explanation.endswith("..."):
        return True
    if has_html_residue(combined):
        return True
    if re.search(r"[^A-Za-z0-9\s.,;:?!'\"()\[\]{}\-/+*=<>%&°µμα-ωΑ-Ω]{4,}", combined):
        return True
    if re.search(r"([#@$^~`|\\]){3,}", combined):
        return True
    return False


def options_have_duplicates(options: dict[str, Any]) -> bool:
    values = [clean_text(options.get(letter)).lower() for letter in LETTERS]
    return len(values) != len(set(values))


def answer_is_composite(answer_text: str) -> bool:
    compact = clean_text(answer_text).lower()
    compact = re.sub(r"\s+", " ", compact)
    return bool(COMPOSITE_ANSWER_RE.fullmatch(compact))


def high_risk_question_reasons(question: str, answer_text: str, dirty_text: bool) -> list[str]:
    reasons: list[str] = []
    if dirty_text:
        reasons.append("dirty_text")
    if len(question) < 30:
        reasons.append("too_short_for_teacher")
    if IMAGE_DEPENDENT_RE.search(question):
        reasons.append("image_dependent")
    if AMBIGUOUS_TRUE_EXCEPT_RE.search(question):
        reasons.append("ambiguous_true_except")
    if answer_is_composite(answer_text):
        reasons.append("composite_answer")
    if EXAM_ARTIFACT_RE.search(question):
        reasons.append("exam_artifact")
    if SOURCE_NOISE_RE.search(f"{question} {answer_text}"):
        reasons.append("source_noise")
    return reasons


def clinical_score(question: str) -> int:
    checks = (
        AGE_RE,
        PATIENT_RE,
        PRESENTATION_RE,
        SYMPTOM_RE,
        FINDING_RE,
        HISTORY_RE,
        REASONING_ASK_RE,
    )
    return sum(bool(pattern.search(question)) for pattern in checks)


def classify_quality_tier(
    question: str,
    answer_text: str,
    dirty_text: bool,
    a_min_question_chars: int,
    a_min_clinical_score: int,
) -> tuple[str, str, int, list[str]]:
    risk_reasons = high_risk_question_reasons(question, answer_text, dirty_text)
    score = clinical_score(question)
    if risk_reasons:
        return "C", "reject", score, risk_reasons

    if len(question) >= a_min_question_chars and score >= a_min_clinical_score:
        return "A", "clinical_vignette", score, ["clinical_vignette"]

    return "B", "short_fact", score, ["short_fact"]


def input_files(input_dir: Path) -> list[Path]:
    return [
        input_dir / "medmcqa_train.jsonl",
        input_dir / "medqa_train.jsonl",
        input_dir / "medmcqa_dev.jsonl",
        input_dir / "medqa_dev.jsonl",
    ]


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


def build_filter_record(
    sample: dict[str, Any],
    reasons: list[str],
) -> dict[str, Any]:
    return {
        "id": clean_text(sample.get("id")),
        "source": clean_text(sample.get("source")),
        "split": clean_text(sample.get("split")),
        "filter_reasons": reasons,
        "sample": sample,
    }


def validate_and_convert_sample(
    sample: dict[str, Any],
    seen_ids: set[str],
    seen_questions: set[str],
    args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, list[str]]:
    reasons: list[str] = []

    sample_id = clean_text(sample.get("id"))
    source = clean_text(sample.get("source"))
    split = clean_text(sample.get("split"))
    question = sanitize_text(sample.get("question"), remove_dates=True)
    explanation = sanitize_text(sample.get("explanation"), remove_dates=True)
    subject = clean_text(sample.get("subject"))
    topic = clean_text(sample.get("topic"))
    answer = clean_text(sample.get("answer")).upper()
    options = sample.get("options")

    if not sample_id:
        reasons.append("missing_id")
    elif sample_id in seen_ids:
        reasons.append("duplicate_id")

    if source not in VALID_SOURCES:
        reasons.append("invalid_source")
    if split not in VALID_SPLITS:
        reasons.append("invalid_split")
    if clean_text(sample.get("choice_type")) != "single":
        reasons.append("invalid_choice_type")

    if not question:
        reasons.append("empty_question")
    elif len(question) < 20:
        reasons.append("short_question")

    normalized_question = normalize_question(question)
    if not normalized_question:
        reasons.append("empty_normalized_question")
    elif normalized_question in seen_questions:
        reasons.append("duplicate_question")

    cleaned_options: dict[str, str] = {}
    if not isinstance(options, dict):
        reasons.append("invalid_options")
    else:
        for letter in LETTERS:
            option = sanitize_text(options.get(letter))
            cleaned_options[letter] = option
            if not option:
                reasons.append(f"empty_option_{letter}")
        if all(cleaned_options.get(letter) for letter in LETTERS) and options_have_duplicates(
            cleaned_options
        ):
            reasons.append("option_duplicate")

    if answer not in LETTERS:
        reasons.append("invalid_answer")

    if reasons:
        return None, reasons

    answer_text = cleaned_options[answer]
    dirty_text = is_dirty_text(question, explanation)
    quality_tier, question_type, score, tier_reasons = classify_quality_tier(
        question=question,
        answer_text=answer_text,
        dirty_text=dirty_text,
        a_min_question_chars=args.a_min_question_chars,
        a_min_clinical_score=args.a_min_clinical_score,
    )
    if quality_tier == "C":
        return None, [f"tier_c_{reason}" for reason in tier_reasons]

    quality = {
        "has_explanation": bool(explanation),
        "explanation_len": len(explanation),
        "explanation_quality": explanation_quality(explanation),
        "question_len": len(question),
        "option_duplicate": False,
        "dirty_text": dirty_text,
        "quality_tier": quality_tier,
        "question_type": question_type,
        "clinical_score": score,
        "tier_reasons": tier_reasons,
    }

    seen_ids.add(sample_id)
    seen_questions.add(normalized_question)

    return (
        {
            "id": sample_id,
            "source": source,
            "split": split,
            "question": question,
            "options": cleaned_options,
            "answer": answer,
            "answer_text": answer_text,
            "explanation": explanation,
            "subject": subject,
            "topic": topic,
            "quality_tier": quality_tier,
            "question_type": question_type,
            "clinical_score": score,
            "expected_step_range": "4-6" if quality_tier == "A" else "2-3",
            "input_quality": quality,
            "_normalized_question": normalized_question,
        },
        [],
    )


def collect_candidates(
    input_dir: Path,
    max_samples: int,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Counter[str], Counter[str], Counter[str]]:
    candidates: list[dict[str, Any]] = []
    filtered_records: list[dict[str, Any]] = []
    raw_counts: Counter[str] = Counter()
    filtered_reason_counts: Counter[str] = Counter()
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()

    for path in input_files(input_dir):
        rows = read_jsonl(path, max_samples)
        raw_counts[path.name] += len(rows)
        for sample in rows:
            converted, reasons = validate_and_convert_sample(sample, seen_ids, seen_questions, args)
            if converted is None:
                filtered_records.append(build_filter_record(sample, reasons))
                filtered_reason_counts.update(reasons)
                continue
            candidates.append(converted)

    valid_counts = Counter(f"{row['source']}_{row['split']}" for row in candidates)
    return candidates, filtered_records, raw_counts, valid_counts, filtered_reason_counts


def candidate_sort_key(
    sample: dict[str, Any],
    random_keys: dict[str, float],
) -> tuple[int, int, int, int, int, float]:
    quality = sample["input_quality"]
    tier = sample.get("quality_tier", "B")
    if tier == "A":
        source_rank = 0 if sample["source"] == "medqa" else 1
    else:
        source_rank = 0 if sample["source"] == "medmcqa" else 1
    return (
        int(quality["dirty_text"]),
        source_rank,
        QUALITY_ORDER.get(quality["explanation_quality"], 99),
        -int(sample.get("clinical_score") or 0),
        -int(quality.get("question_len") or 0),
        random_keys[sample["id"]],
    )


def choose_from_pool(
    pool: list[dict[str, Any]],
    needed: int,
    selected_ids: set[str],
    no_explanation_count: int,
    no_explanation_limit: int,
) -> tuple[list[dict[str, Any]], int]:
    chosen: list[dict[str, Any]] = []
    for sample in pool:
        if len(chosen) >= needed:
            break
        if sample["id"] in selected_ids:
            continue
        has_explanation = sample["input_quality"]["has_explanation"]
        if not has_explanation and no_explanation_count >= no_explanation_limit:
            continue
        chosen.append(sample)
        selected_ids.add(sample["id"])
        if not has_explanation:
            no_explanation_count += 1
    return chosen, no_explanation_count


def select_split_candidates(
    candidates: list[dict[str, Any]],
    split: str,
    target_size: int,
    seed: int,
    min_a_ratio: float,
) -> list[dict[str, Any]]:
    if target_size <= 0:
        return []

    no_explanation_limit = int(target_size * MAX_NO_EXPLANATION_RATIO)
    split_candidates = [row for row in candidates if row["split"] == split]

    rng = random.Random(seed + (0 if split == "train" else 10_000))
    random_keys = {row["id"]: rng.random() for row in split_candidates}
    pools: dict[str, list[dict[str, Any]]] = {
        "A": [row for row in split_candidates if row.get("quality_tier") == "A"],
        "B": [row for row in split_candidates if row.get("quality_tier") == "B"],
    }
    for pool in pools.values():
        pool.sort(key=lambda row: candidate_sort_key(row, random_keys))

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    no_explanation_count = 0
    a_target = min(len(pools["A"]), math.ceil(target_size * min_a_ratio))
    b_target = max(target_size - a_target, 0)

    chosen, no_explanation_count = choose_from_pool(
        pools["A"],
        a_target,
        selected_ids,
        no_explanation_count,
        no_explanation_limit,
    )
    selected.extend(chosen)

    chosen, no_explanation_count = choose_from_pool(
        pools["B"],
        b_target,
        selected_ids,
        no_explanation_count,
        no_explanation_limit,
    )
    selected.extend(chosen)

    if len(selected) < target_size:
        remainder_pool = [row for row in split_candidates if row["id"] not in selected_ids]
        remainder_pool.sort(key=lambda row: candidate_sort_key(row, random_keys))
        chosen, no_explanation_count = choose_from_pool(
            remainder_pool,
            target_size - len(selected),
            selected_ids,
            no_explanation_count,
            no_explanation_limit,
        )
        selected.extend(chosen)

    rng.shuffle(selected)
    return [strip_private_fields(row) for row in selected]


def strip_private_fields(sample: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in sample.items() if not key.startswith("_")}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def counter_to_lines(counter: Counter[Any], empty_label: str = "<EMPTY>") -> list[str]:
    if not counter:
        return ["- 无"]
    return [f"- `{key if key else empty_label}`：{value}" for key, value in counter.most_common()]


def preview_block(rows: list[dict[str, Any]], limit: int = 10) -> list[str]:
    lines: list[str] = []
    for row in rows[:limit]:
        preview = {
            "id": row["id"],
            "source": row["source"],
            "split": row["split"],
            "question": row["question"],
            "answer": row["answer"],
            "answer_text": row["answer_text"],
            "quality_tier": row.get("quality_tier"),
            "question_type": row.get("question_type"),
            "clinical_score": row.get("clinical_score"),
            "expected_step_range": row.get("expected_step_range"),
            "input_quality": row["input_quality"],
        }
        lines.extend(["```json", json.dumps(preview, ensure_ascii=False, indent=2), "```", ""])
    if not lines:
        lines.append("无")
    return lines


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Counter[Any]]:
    summary: dict[str, Counter[Any]] = {
        "source": Counter(),
        "split": Counter(),
        "answer": Counter(),
        "explanation_quality": Counter(),
        "quality_tier": Counter(),
        "question_type": Counter(),
        "tier_source": Counter(),
        "subject": Counter(),
    }
    for row in rows:
        summary["source"][row["source"]] += 1
        summary["split"][row["split"]] += 1
        summary["answer"][row["answer"]] += 1
        summary["explanation_quality"][row["input_quality"]["explanation_quality"]] += 1
        summary["quality_tier"][row.get("quality_tier") or "<EMPTY>"] += 1
        summary["question_type"][row.get("question_type") or "<EMPTY>"] += 1
        summary["tier_source"][
            f"{row.get('quality_tier') or '<EMPTY>'}/{row.get('source') or '<EMPTY>'}"
        ] += 1
        if row["source"] == "medmcqa":
            summary["subject"][row.get("subject") or "<EMPTY>"] += 1
    return summary


def write_report(
    path: Path,
    train_rows: list[dict[str, Any]],
    dev_rows: list[dict[str, Any]],
    raw_counts: Counter[str],
    valid_counts: Counter[str],
    filtered_reason_counts: Counter[str],
    target_train_size: int,
    target_dev_size: int,
    min_a_ratio: float,
    seed: int,
    max_samples: int,
) -> None:
    all_rows = train_rows + dev_rows
    summary = summarize_rows(all_rows)
    dirty_count = sum(1 for row in all_rows if row["input_quality"]["dirty_text"])
    reached_target = len(train_rows) >= target_train_size and len(dev_rows) >= target_dev_size
    train_tiers = Counter(row.get("quality_tier") or "<EMPTY>" for row in train_rows)
    dev_tiers = Counter(row.get("quality_tier") or "<EMPTY>" for row in dev_rows)
    train_a_ratio = train_tiers.get("A", 0) / len(train_rows) if train_rows else 0.0
    dev_a_ratio = dev_tiers.get("A", 0) / len(dev_rows) if dev_rows else 0.0

    lines = [
        "# Teacher Input 候选数据统计",
        "",
        f"- seed：`{seed}`",
        f"- max_samples：`{max_samples}`",
        f"- train 候选目标数量：{target_train_size}",
        f"- dev 候选目标数量：{target_dev_size}",
        f"- 目标 A 档最小占比：{min_a_ratio:.2%}",
        f"- train 实际输出数量：{len(train_rows)}",
        f"- dev 实际输出数量：{len(dev_rows)}",
        f"- train A 档占比：{train_a_ratio:.2%}",
        f"- dev A 档占比：{dev_a_ratio:.2%}",
        f"- 是否达到目标数量：{'是' if reached_target else '否'}",
        "",
        "## 原始输入样本数",
        "",
        *counter_to_lines(raw_counts),
        "",
        "## 清洗后候选池样本数",
        "",
        *counter_to_lines(valid_counts),
        "",
        "## 输出 source 分布",
        "",
        *counter_to_lines(summary["source"]),
        "",
        "## 输出 split 分布",
        "",
        *counter_to_lines(summary["split"]),
        "",
        "## answer 分布",
        "",
        *counter_to_lines(summary["answer"]),
        "",
        "## explanation_quality 分布",
        "",
        *counter_to_lines(summary["explanation_quality"]),
        "",
        "## quality_tier 分布",
        "",
        *counter_to_lines(summary["quality_tier"]),
        "",
        "## question_type 分布",
        "",
        *counter_to_lines(summary["question_type"]),
        "",
        "## quality_tier/source 分布",
        "",
        *counter_to_lines(summary["tier_source"]),
        "",
        "## 文本质量标记",
        "",
        f"- dirty_text 数量：{dirty_count}",
        f"- option_duplicate 过滤数量：{filtered_reason_counts.get('option_duplicate', 0)}",
        f"- duplicate_question 过滤数量：{filtered_reason_counts.get('duplicate_question', 0)}",
        "",
        "## filter reason 数量",
        "",
        *counter_to_lines(filtered_reason_counts),
        "",
        "## MedMCQA subject Top 20",
        "",
        *counter_to_lines(Counter(dict(summary["subject"].most_common(20)))),
        "",
        "## 前 10 条 teacher input 预览",
        "",
        *preview_block(all_rows, 10),
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def print_summary(
    train_rows: list[dict[str, Any]],
    dev_rows: list[dict[str, Any]],
    filtered_reason_counts: Counter[str],
    report_path: Path,
) -> None:
    summary = summarize_rows(train_rows + dev_rows)
    print("Teacher input candidates built.")
    print(f"  train: {len(train_rows)}")
    print(f"  dev: {len(dev_rows)}")
    print(f"  source: {dict(summary['source'])}")
    print(f"  quality_tier: {dict(summary['quality_tier'])}")
    print(f"  question_type: {dict(summary['question_type'])}")
    print(f"  explanation_quality: {dict(summary['explanation_quality'])}")
    print(f"  filtered: {sum(filtered_reason_counts.values())}")
    print(f"  report: {report_path}")


def main() -> None:
    args = parse_args()
    try:
        candidates, filtered_records, raw_counts, valid_counts, filtered_reason_counts = (
            collect_candidates(args.input_dir, args.max_samples, args)
        )
        train_rows = select_split_candidates(
            candidates,
            split="train",
            target_size=args.target_train_size,
            seed=args.seed,
            min_a_ratio=args.min_a_ratio,
        )
        dev_rows = select_split_candidates(
            candidates,
            split="dev",
            target_size=args.target_dev_size,
            seed=args.seed,
            min_a_ratio=args.min_a_ratio,
        )

        write_jsonl(args.output_dir / "teacher_sft_train_inputs.jsonl", train_rows)
        write_jsonl(args.output_dir / "teacher_sft_dev_inputs.jsonl", dev_rows)
        write_jsonl(args.filtered_output, filtered_records)
        write_report(
            args.report_path,
            train_rows,
            dev_rows,
            raw_counts,
            valid_counts,
            filtered_reason_counts,
            args.target_train_size,
            args.target_dev_size,
            args.min_a_ratio,
            args.seed,
            args.max_samples,
        )
        print_summary(train_rows, dev_rows, filtered_reason_counts, args.report_path)
    except Exception as exc:  # noqa: BLE001 - CLI should surface a clear failure.
        raise SystemExit(f"ERROR: failed to build teacher inputs: {exc}") from exc


if __name__ == "__main__":
    main()
