"""Flag suspicious SFT samples and build two clean SFT tiers.

``clean_core`` excludes every suspicious reason and is meant for high-quality
CoT SFT. ``clean_plus_short_fact`` adds back samples whose only issue is a short
fact-style question, which can help expand supervised fine-tuning data.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_BLACKLIST_IDS = {
    "medmcqa_train_143326",
    "medmcqa_train_133172",
    "medmcqa_train_121483",
    "medmcqa_train_052361",
}
IMAGE_PATTERNS = (
    "figure",
    "shown below",
    "shown above",
    "shown belwo",
    "marked area",
    "image",
    "diagram",
    "photograph",
    "photo",
    "picture",
    "histology",
    "ct shows",
    "x-ray is shown",
    "pathologic changes seen",
)
IMAGE_DEPENDENT_REGEXES = (
    r"\b(?:x[-\s]?ray|radiograph|photograph|photo|picture|image|diagram|ct|mri|ultrasound|ecg|ekg)\b[^.\n]{0,120}\b(?:is|are|was|were)\s+shown\b",
    r"\b(?:is|are|was|were)\s+shown\b[^.\n]{0,120}\b(?:figure|image|diagram|photograph|photo|picture|x[-\s]?ray|radiograph)\b",
    r"\b(?:figure|image|diagram|photograph|photo|picture)\s*[A-Z0-9]?\b",
    r"\bshown\s+(?:below|above|belwo|in\s+the\s+(?:image|figure|diagram|photograph|photo|picture))\b",
    r"\b(?:hands?|lesion|specimen|slide|biopsy|microscopic\s+examination)[^.\n]{0,120}\b(?:is|are|was|were)?\s*shown\b",
)
MONTH_NAMES = (
    "Jan",
    "January",
    "Feb",
    "February",
    "Mar",
    "March",
    "Apr",
    "April",
    "May",
    "Jun",
    "June",
    "Jul",
    "July",
    "Aug",
    "August",
    "Sep",
    "Sept",
    "September",
    "Oct",
    "October",
    "Nov",
    "November",
    "Dec",
    "December",
)
MONTH_PATTERN = "|".join(MONTH_NAMES)
DATE_ARTIFACT_REGEXES = (
    rf"\b\d{{1,2}}\s*[-/]\s*(?:{MONTH_PATTERN})\b",
    rf"\b(?:{MONTH_PATTERN})\s*[-/]\s*\d{{1,2}}\b",
    rf"\b(?:{MONTH_PATTERN})\s+\d{{4}}\b",
)
EXTERNAL_STANDARD_PATTERNS = (
    "ICD",
    "IPC",
    "FDA",
    "WHO diagnostic criteria",
    "guideline",
    "Group A",
    "Group B",
    "Group C",
    "Group D",
    "treatment duration",
    "MDR/XDR",
    "approved",
)
COMPOSITE_PHRASES = (
    "all of the above",
    "none of the above",
    "both",
    "2 & 3",
    "1 & 2",
)
COMPOSITE_SHORT_CODES = {"ab", "ac", "ad", "bc"}
CASE_INFO_PATTERNS = (
    r"\b\d+\s*-\s*year\s*-\s*old\b",
    r"\b\d+\s*year\s*old\b",
    r"\bman\b",
    r"\bwoman\b",
    r"\bboy\b",
    r"\bgirl\b",
    r"\bpatient\b",
    r"\bpresents?\b",
    r"\bhistory\b",
    r"\bexamination\b",
    r"\blaboratory\b",
    r"\bvital\b",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flag suspicious SFT samples.")
    parser.add_argument(
        "--input_train",
        type=Path,
        default=Path("data/sft/medical_cot_sft_train.jsonl"),
    )
    parser.add_argument(
        "--input_dev",
        type=Path,
        default=Path("data/sft/medical_cot_sft_dev.jsonl"),
    )
    parser.add_argument(
        "--output_train_clean",
        type=Path,
        default=Path("data/sft/medical_cot_sft_train.clean.jsonl"),
    )
    parser.add_argument(
        "--output_dev_clean",
        type=Path,
        default=Path("data/sft/medical_cot_sft_dev.clean.jsonl"),
    )
    parser.add_argument(
        "--output_train_clean_plus_short_fact",
        type=Path,
        default=Path("data/sft/medical_cot_sft_train.clean_plus_short_fact.jsonl"),
    )
    parser.add_argument(
        "--output_dev_clean_plus_short_fact",
        type=Path,
        default=Path("data/sft/medical_cot_sft_dev.clean_plus_short_fact.jsonl"),
    )
    parser.add_argument(
        "--suspicious_output",
        type=Path,
        default=Path("data/sft/medical_cot_sft_suspicious.jsonl"),
    )
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/sft_suspicious_filter_report.md"),
    )
    parser.add_argument(
        "--blacklist_path",
        type=Path,
        default=Path("data/sft/suspicious_blacklist_ids.txt"),
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+", " ", str(value)).strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        print(f"WARNING: input file does not exist: {path}")
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


def load_blacklist(path: Path) -> set[str]:
    blacklist = set(DEFAULT_BLACKLIST_IDS)
    if not path.exists():
        return blacklist

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            blacklist.add(text)
    return blacklist


def extract_question(input_text: str) -> str:
    match = re.search(r"Question:\n(.+?)(?:\n\nOptions:|$)", input_text, flags=re.DOTALL)
    return clean_text(match.group(1)) if match else clean_text(input_text)


def english_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", text))


def has_case_info(question: str) -> bool:
    return any(re.search(pattern, question, flags=re.IGNORECASE) for pattern in CASE_INFO_PATTERNS)


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    text_lower = text.lower()
    return any(pattern.lower() in text_lower for pattern in patterns)


def has_image_dependency(text: str) -> bool:
    if contains_any(text, IMAGE_PATTERNS):
        return True
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in IMAGE_DEPENDENT_REGEXES)


def has_date_artifact(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in DATE_ARTIFACT_REGEXES)


def has_dirty_text(text: str) -> bool:
    if "aEUR" in text or "&;" in text or "\x00" in text or "FigureAFigureB" in text:
        return True
    if re.search(r"[^A-Za-z0-9\s.,;:?!'\"()\[\]{}\-/+*=<>%&°µα-ωΑ-Ω]{4,}", text):
        return True
    if re.search(r"([#@$^~`|\\]){4,}", text):
        return True
    if re.search(r"\b[a-zA-Z]*[A-Z]{2,}[a-z]{2,}[A-Z]{2,}[a-zA-Z]*\b", text):
        return True
    return False


def has_composite_answer(answer_text: str) -> bool:
    normalized = clean_text(answer_text).lower()
    if any(phrase in normalized for phrase in COMPOSITE_PHRASES):
        return True
    compact = re.sub(r"[^a-z0-9]+", "", normalized)
    if compact in COMPOSITE_SHORT_CODES:
        return True
    if re.fullmatch(r"(?:all|none)", compact):
        return True
    return False


def suspicious_reasons(sample: dict[str, Any], blacklist: set[str]) -> list[str]:
    reasons: list[str] = []
    input_text = sample.get("input") if isinstance(sample.get("input"), str) else ""
    answer_text = sample.get("answer_text") if isinstance(sample.get("answer_text"), str) else ""
    question = extract_question(input_text)

    if has_image_dependency(input_text):
        reasons.append("image_dependent")
    if has_dirty_text(input_text) or has_dirty_text(answer_text):
        reasons.append("dirty_input")
    if has_date_artifact(input_text) or has_date_artifact(answer_text):
        reasons.append("date_artifact")
    if has_composite_answer(answer_text):
        reasons.append("composite_answer")
    if contains_any(input_text, EXTERNAL_STANDARD_PATTERNS):
        reasons.append("external_standard")
    if english_word_count(question) < 8 and not has_case_info(question):
        reasons.append("short_fact_question")
    if clean_text(sample.get("id")) in blacklist:
        reasons.append("manual_blacklist")

    return sorted(set(reasons))


def build_suspicious_row(sample: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    return {
        "id": clean_text(sample.get("id")),
        "source": clean_text(sample.get("source")),
        "split": clean_text(sample.get("split")),
        "suspicious_reasons": reasons,
        "sample": sample,
    }


def split_rows(
    rows: list[dict[str, Any]],
    blacklist: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], Counter[str], int]:
    clean_core_rows: list[dict[str, Any]] = []
    clean_plus_short_fact_rows: list[dict[str, Any]] = []
    suspicious_rows: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    short_fact_only_count = 0

    for sample in rows:
        reasons = suspicious_reasons(sample, blacklist)
        if not reasons:
            clean_core_rows.append(sample)
            clean_plus_short_fact_rows.append(sample)
        elif reasons == ["short_fact_question"]:
            clean_plus_short_fact_rows.append(sample)
            short_fact_only_count += 1
        else:
            suspicious_rows.append(build_suspicious_row(sample, reasons))
            reason_counts.update(reasons)
    return (
        clean_core_rows,
        clean_plus_short_fact_rows,
        suspicious_rows,
        reason_counts,
        short_fact_only_count,
    )


def summarize_samples(rows: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    return {
        "source": Counter(clean_text(row.get("source")) or "unknown" for row in rows),
        "answer": Counter(clean_text(row.get("answer")) or "unknown" for row in rows),
        "subject": Counter(clean_text(row.get("subject")) or "<EMPTY>" for row in rows),
    }


def counter_lines(counter: Counter[str], limit: int | None = None) -> list[str]:
    items = counter.most_common(limit)
    if not items:
        return ["- 无"]
    return [f"- `{key}`：{value}" for key, value in items]


def preview_lines(rows: list[dict[str, Any]], limit: int = 20) -> list[str]:
    lines: list[str] = []
    for row in rows[:limit]:
        sample = row.get("sample", {})
        preview = {
            "id": row.get("id", ""),
            "source": row.get("source", ""),
            "split": row.get("split", ""),
            "suspicious_reasons": row.get("suspicious_reasons", []),
            "answer": sample.get("answer", ""),
            "answer_text": sample.get("answer_text", ""),
            "question": extract_question(sample.get("input", "")),
        }
        lines.extend(["```json", json.dumps(preview, ensure_ascii=False, indent=2), "```", ""])
    if not lines:
        return ["无"]
    return lines


def recommendation(suspicious_rate: float, clean_core_count: int, clean_plus_count: int) -> str:
    if clean_core_count == 0 and clean_plus_count == 0:
        return "FAIL：clean 文件为空，不建议进入 SFT。"
    if suspicious_rate >= 0.35:
        return "WARNING：高风险 suspicious 比例较高，建议人工抽查后再进入 SFT。"
    return "PASS：建议 clean_core 用于高质量 CoT SFT，clean_plus_short_fact 用于扩量 SFT；suspicious 暂不参与训练。"


def write_report(
    path: Path,
    train_rows: list[dict[str, Any]],
    dev_rows: list[dict[str, Any]],
    clean_core_train: list[dict[str, Any]],
    clean_core_dev: list[dict[str, Any]],
    clean_plus_train: list[dict[str, Any]],
    clean_plus_dev: list[dict[str, Any]],
    suspicious_rows: list[dict[str, Any]],
    reason_counts: Counter[str],
    short_fact_only_train: int,
    short_fact_only_dev: int,
    output_train_clean: Path,
    output_dev_clean: Path,
    output_train_clean_plus: Path,
    output_dev_clean_plus: Path,
) -> None:
    total_input = len(train_rows) + len(dev_rows)
    clean_core_rows = clean_core_train + clean_core_dev
    clean_plus_rows = clean_plus_train + clean_plus_dev
    suspicious_samples = [row["sample"] for row in suspicious_rows]
    suspicious_summary = summarize_samples(suspicious_samples)
    suspicious_rate = len(suspicious_rows) / total_input if total_input else 0.0
    short_fact_only_total = short_fact_only_train + short_fact_only_dev

    lines = [
        "# SFT Suspicious 隔离报告",
        "",
        "## 样本数",
        "",
        f"- input train 样本数：{len(train_rows)}",
        f"- input dev 样本数：{len(dev_rows)}",
        f"- clean_core train 样本数：{len(clean_core_train)}",
        f"- clean_core dev 样本数：{len(clean_core_dev)}",
        f"- clean_plus_short_fact train 样本数：{len(clean_plus_train)}",
        f"- clean_plus_short_fact dev 样本数：{len(clean_plus_dev)}",
        f"- 纯 short_fact_question 放回扩量集样本数：{short_fact_only_total}",
        f"- 高风险 suspicious 总数：{len(suspicious_rows)}",
        f"- 高风险 suspicious rate：{suspicious_rate:.2%}",
        "",
        "## 输出文件",
        "",
        f"- clean_core train：`{output_train_clean}`",
        f"- clean_core dev：`{output_dev_clean}`",
        f"- clean_plus_short_fact train：`{output_train_clean_plus}`",
        f"- clean_plus_short_fact dev：`{output_dev_clean_plus}`",
        "",
        "## Suspicious Reason 分布",
        "",
        *counter_lines(reason_counts),
        "",
        "## Suspicious Source 分布",
        "",
        *counter_lines(suspicious_summary["source"]),
        "",
        "## Suspicious Answer 分布",
        "",
        *counter_lines(suspicious_summary["answer"]),
        "",
        "## Suspicious Subject Top 20",
        "",
        *counter_lines(suspicious_summary["subject"], limit=20),
        "",
        "## 前 20 条 suspicious 样本预览",
        "",
        *preview_lines(suspicious_rows, limit=20),
        "## 是否建议用 clean 文件进入 SFT",
        "",
        f"- {recommendation(suspicious_rate, len(clean_core_rows), len(clean_plus_rows))}",
        "",
        "## 使用建议",
        "",
        "- `clean_core`：高质量 CoT 训练优先使用，排除短事实题、缺图题、脏输入、组合答案、外部标准题等。",
        "- `clean_plus_short_fact`：在 `clean_core` 基础上加入纯短事实题，适合数据量不足时扩量 SFT。",
        "- `suspicious`：只保留存在非短事实高风险原因的样本，建议暂不进入训练。",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    try:
        train_rows = read_jsonl(args.input_train)
        dev_rows = read_jsonl(args.input_dev)
        blacklist = load_blacklist(args.blacklist_path)

        (
            clean_core_train,
            clean_plus_train,
            suspicious_train,
            train_reason_counts,
            short_fact_only_train,
        ) = split_rows(train_rows, blacklist)
        (
            clean_core_dev,
            clean_plus_dev,
            suspicious_dev,
            dev_reason_counts,
            short_fact_only_dev,
        ) = split_rows(dev_rows, blacklist)
        suspicious_rows = suspicious_train + suspicious_dev
        reason_counts = train_reason_counts + dev_reason_counts

        rng = random.Random(args.seed)
        rng.shuffle(clean_core_train)
        rng.shuffle(clean_core_dev)
        rng.shuffle(clean_plus_train)
        rng.shuffle(clean_plus_dev)
        rng.shuffle(suspicious_rows)

        write_jsonl(args.output_train_clean, clean_core_train)
        write_jsonl(args.output_dev_clean, clean_core_dev)
        write_jsonl(args.output_train_clean_plus_short_fact, clean_plus_train)
        write_jsonl(args.output_dev_clean_plus_short_fact, clean_plus_dev)
        write_jsonl(args.suspicious_output, suspicious_rows)
        write_report(
            args.report_path,
            train_rows=train_rows,
            dev_rows=dev_rows,
            clean_core_train=clean_core_train,
            clean_core_dev=clean_core_dev,
            clean_plus_train=clean_plus_train,
            clean_plus_dev=clean_plus_dev,
            suspicious_rows=suspicious_rows,
            reason_counts=reason_counts,
            short_fact_only_train=short_fact_only_train,
            short_fact_only_dev=short_fact_only_dev,
            output_train_clean=args.output_train_clean,
            output_dev_clean=args.output_dev_clean,
            output_train_clean_plus=args.output_train_clean_plus_short_fact,
            output_dev_clean_plus=args.output_dev_clean_plus_short_fact,
        )

        print("Suspicious SFT flagging finished.")
        print(f"  input train: {len(train_rows)}")
        print(f"  input dev: {len(dev_rows)}")
        print(f"  clean_core train: {len(clean_core_train)}")
        print(f"  clean_core dev: {len(clean_core_dev)}")
        print(f"  clean_plus_short_fact train: {len(clean_plus_train)}")
        print(f"  clean_plus_short_fact dev: {len(clean_plus_dev)}")
        print(f"  short_fact_only added to plus tier: {short_fact_only_train + short_fact_only_dev}")
        print(f"  high-risk suspicious: {len(suspicious_rows)}")
        print(f"  report: {args.report_path}")
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI should surface a clear failure.
        raise SystemExit(f"ERROR: failed to flag suspicious SFT samples: {exc}") from exc


if __name__ == "__main__":
    main()
