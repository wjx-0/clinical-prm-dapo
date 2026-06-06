"""Generate raw teacher SFT data from teacher input candidates.

This script calls a teacher backend and performs only light format validation.
Strict quality filtering is intentionally left to a later filter script.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import os
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


INSTRUCTION = (
    "Please solve the following medical multiple-choice question with "
    "step-by-step reasoning. Put your reasoning inside <think></think> and "
    "the final answer inside <answer></answer>."
)
SYSTEM_PROMPT = """You are a medical reasoning data generation assistant.

Your task is to generate high-quality supervised fine-tuning responses for medical multiple-choice questions.

You must produce clean, concise, medically grounded step-by-step reasoning that supports the provided correct answer.

You are not solving the question from scratch. You are rewriting or generating a training-quality reasoning trace based on the question, answer choices, correct answer, and optional expert explanation.

Strict rules:

1. Do not mention that a correct answer, gold answer, or expert explanation was provided.
2. Do not say "according to the provided explanation".
3. Do not copy noisy raw explanation text.
4. Do not introduce unsupported patient details, laboratory values, imaging findings, smear findings, pathology findings, symptoms, or physical exam findings.
5. Do not output multiple final answers.
6. The final answer must exactly match the given correct answer.
7. Use exactly one <answer> tag.
8. The content inside <answer> must be exactly one letter: A, B, C, or D.
9. Use 4 to 6 steps for clinical vignette questions and 2 to 3 steps for short factual questions.
10. Each step should be natural, concise, medically useful, and grounded in the available information.
11. Do not include markdown tables.
12. Do not include citations.
13. Do not include any text after the final </answer> tag.
14. Do not use generic filler steps such as "recognize this as a medical multiple-choice question".
15. Step 1 must use only clues explicitly stated in the question. If the question is short, state the fact being asked without inventing clinical clues.
16. Do not write option comparison merely as filler; compare options only when it helps explain the answer."""
LETTERS = ("A", "B", "C", "D")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate raw SFT responses with a teacher model."
    )
    parser.add_argument(
        "--env_file",
        type=Path,
        default=Path(".env"),
        help="Optional .env file loaded before resolving API settings.",
    )
    parser.add_argument(
        "--train_input",
        type=Path,
        default=Path("data/teacher_inputs/teacher_sft_train_inputs.jsonl"),
    )
    parser.add_argument(
        "--dev_input",
        type=Path,
        default=Path("data/teacher_inputs/teacher_sft_dev_inputs.jsonl"),
    )
    parser.add_argument("--output_dir", type=Path, default=Path("data/sft"))
    parser.add_argument(
        "--report_path",
        type=Path,
        default=Path("docs/teacher_sft_generation_report.md"),
    )
    parser.add_argument(
        "--teacher_backend",
        choices=("mock", "openai", "local"),
        default="",
    )
    parser.add_argument("--model_name", default="")
    parser.add_argument("--base_url", default="")
    parser.add_argument(
        "--api_key",
        default="",
        help="API key. Defaults to OPENAI_API_KEY for openai and EMPTY for local.",
    )
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument(
        "--num_workers",
        type=int,
        default=1,
        help="Number of concurrent teacher API calls. Keep low if the provider rate-limits.",
    )
    parser.add_argument("--max_train_samples", type=int, default=-1)
    parser.add_argument("--max_dev_samples", type=int, default=-1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--sleep_seconds", type=float, default=0.0)
    parser.add_argument("--max_retries", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max_tokens", type=int, default=700)
    return parser.parse_args()


def parse_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            if text.startswith("export "):
                text = text[len("export ") :].strip()
            if "=" not in text:
                print(f"WARNING: skip invalid env line {path}:{line_no}", file=sys.stderr)
                continue
            key, value = text.split("=", 1)
            key = key.strip()
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                print(f"WARNING: skip invalid env key {path}:{line_no}: {key}", file=sys.stderr)
                continue
            os.environ.setdefault(key, parse_env_value(value))


def first_env_value(*keys: str, default: str = "") -> str:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return default


def apply_env_defaults(args: argparse.Namespace) -> None:
    load_env_file(args.env_file)
    if not args.teacher_backend:
        args.teacher_backend = first_env_value("TEACHER_BACKEND", default="mock")
    if not args.model_name:
        args.model_name = first_env_value("TEACHER_MODEL_NAME", "MODEL_NAME")
    if not args.base_url:
        args.base_url = first_env_value("TEACHER_BASE_URL", "OPENAI_BASE_URL", "BASE_URL")
    if not args.api_key:
        args.api_key = first_env_value("TEACHER_API_KEY", "LLM_API_KEY", "OPENAI_API_KEY")
    if args.num_workers <= 1:
        env_workers = first_env_value("TEACHER_NUM_WORKERS")
        if env_workers:
            try:
                args.num_workers = int(env_workers)
            except ValueError:
                print(f"WARNING: invalid TEACHER_NUM_WORKERS: {env_workers}", file=sys.stderr)


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


def read_jsonl(path: Path, max_samples: int = -1) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    if max_samples == 0:
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


def iter_jsonl(path: Path) -> Any:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError as exc:
                print(f"WARNING: invalid JSON in {path}:{line_no}: {exc}", file=sys.stderr)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def truncate_outputs(paths: list[Path]) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")


def format_options(options: dict[str, Any]) -> str:
    return "\n".join(f"{letter}. {sanitize_text(options.get(letter))}" for letter in LETTERS)


def format_sft_input(sample: dict[str, Any]) -> str:
    options = sample.get("options") if isinstance(sample.get("options"), dict) else {}
    return (
        f"Question:\n{sanitize_text(sample.get('question'), remove_dates=True)}"
        f"\n\nOptions:\n{format_options(options)}"
    )


def build_teacher_messages(sample: dict[str, Any]) -> list[dict[str, str]]:
    options = sample.get("options")
    if not isinstance(options, dict):
        raise ValueError(f"sample options must be a dict: {sample.get('id', '')}")

    for letter in LETTERS:
        if not clean_text(options.get(letter)):
            raise ValueError(f"sample is missing option {letter}: {sample.get('id', '')}")

    answer = clean_text(sample.get("answer")).upper()
    if answer not in LETTERS:
        raise ValueError(f"sample has invalid answer: {sample.get('id', '')}")

    quality_tier = clean_text(sample.get("quality_tier")) or "B"
    question_type = clean_text(sample.get("question_type")) or (
        "clinical_vignette" if quality_tier == "A" else "short_fact"
    )
    if quality_tier == "A":
        step_guidance = """Question type:
Clinical vignette / reasoning-heavy question.

Use 4 to 6 concise steps:
Step 1: Extract the explicit clinical clues from the question. Do not add any unstated findings.
Step 2: Connect those clues to the most likely diagnosis, mechanism, pathophysiology, treatment principle, or next management step.
Step 3: Explain the key medical fact or mechanism that makes the answer correct.
Step 4: If useful, compare only the most relevant alternative options. Skip broad option-by-option comparison if it would be filler.
Step 5: Conclude with the answer in plain language.

Target length: usually 140 to 260 words."""
    else:
        step_guidance = """Question type:
Short factual / definition / single-knowledge-point question.

Use 2 to 3 concise steps only:
Step 1: State what the question is asking or the explicit clue it provides. Do not invent clinical context.
Step 2: State the relevant medical fact, classification, mechanism, or association.
Step 3: Optional, briefly distinguish one or two misleading alternatives only if it is useful.

Target length: usually 60 to 140 words. Do not stretch a short factual question into a long chain of reasoning."""

    user_prompt = f"""Generate a supervised fine-tuning response for the following medical multiple-choice question.

Question:
{sanitize_text(sample.get("question"), remove_dates=True)}

Options:
A. {sanitize_text(options.get("A"))}
B. {sanitize_text(options.get("B"))}
C. {sanitize_text(options.get("C"))}
D. {sanitize_text(options.get("D"))}

Correct answer:
{answer}

Correct answer text:
{sanitize_text(sample.get("answer_text"))}

Optional expert explanation:
{sanitize_text(sample.get("explanation"), remove_dates=True)}

Input quality metadata:
quality_tier: {quality_tier}
question_type: {question_type}
expected_step_range: {clean_text(sample.get("expected_step_range")) or ("4-6" if quality_tier == "A" else "2-3")}

Reasoning plan:
{step_guidance}

Required output format:

<think>
Step 1: ...
Step 2: ...
Step 3: ...
</think>
<answer>{answer}</answer>

Additional requirements:

* The reasoning must support the correct answer.
* The reasoning must mention the exact correct answer text at least once when it is a natural medical term, drug, diagnosis, mechanism, or management option.
* The final answer must be exactly <answer>{answer}</answer>.
* Do not mention "gold answer", "provided answer", "provided explanation", "correct option", or "given answer".
* Do not copy the optional expert explanation verbatim if it is noisy.
* If the expert explanation contains typos, exam artifacts, references, page numbers, "Ans.", or compressed table text, rewrite it into clean reasoning.
* If the expert explanation is empty, generate a conservative reasoning trace based only on the question, options, and correct answer text.
* Step 1 must mention only details explicitly present in the question. Do not fabricate patient details, symptoms, labs, imaging findings, smear findings, biopsy findings, or physical exam findings.
* Keep every step useful: question clues -> medical mechanism or fact -> concise answer support.
* Use option comparison only when it clarifies the answer; do not add a generic comparison paragraph.
* The final reasoning step should be a complete explanatory sentence that names the exact answer text and briefly states why it follows.
* Do not say or imply that you are constructing data, rewriting an explanation, or following metadata.
* Output only the final SFT response. No JSON. No markdown. No extra commentary."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def parse_answer_from_messages(messages: list[dict[str, str]]) -> str:
    user_text = messages[-1]["content"] if messages else ""
    match = re.search(r"final answer must be exactly <answer>([A-D])</answer>", user_text)
    if match:
        return match.group(1)
    match = re.search(r"Correct answer:\s*([A-D])", user_text)
    if match:
        return match.group(1)
    return "A"


def parse_answer_text_from_messages(messages: list[dict[str, str]]) -> str:
    user_text = messages[-1]["content"] if messages else ""
    match = re.search(
        r"Correct answer text:\n(.+?)\n\nOptional expert explanation:",
        user_text,
        flags=re.DOTALL,
    )
    return clean_text(match.group(1)) if match else "the selected option"


def parse_quality_tier_from_messages(messages: list[dict[str, str]]) -> str:
    user_text = messages[-1]["content"] if messages else ""
    match = re.search(r"quality_tier:\s*([ABC])", user_text)
    return match.group(1) if match else "B"


def call_mock_teacher(messages: list[dict[str, str]]) -> str:
    answer = parse_answer_from_messages(messages)
    answer_text = parse_answer_text_from_messages(messages)
    quality_tier = parse_quality_tier_from_messages(messages)
    if quality_tier == "A":
        return (
            "<think>\n"
            "Step 1: The question provides a clinical scenario with several findings that need to be connected to the most likely medical decision.\n"
            f"Step 2: The relevant clinical pattern supports {answer_text} as the best answer among the listed choices.\n"
            "Step 3: The mechanism or management principle should follow from the stated findings rather than from unstated details.\n"
            f"Step 4: Therefore, {answer_text} is the best supported choice.\n"
            "</think>\n"
            f"<answer>{answer}</answer>"
        )

    return (
        "<think>\n"
        "Step 1: The question asks for a specific medical fact or association.\n"
        f"Step 2: The relevant fact identifies {answer_text} as the matching choice.\n"
        "</think>\n"
        f"<answer>{answer}</answer>"
    )


def call_openai_compatible(
    messages: list[dict[str, str]],
    model_name: str,
    base_url: str,
    api_key: str,
    max_retries: int,
    temperature: float,
    max_tokens: int,
) -> str:
    if not model_name:
        raise ValueError("--model_name is required for openai/local teacher backends")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing openai package. Please run: pip install openai") from exc

    client_kwargs: dict[str, str] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    last_error: Exception | None = None
    for attempt in range(1, max(max_retries, 1) + 1):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content or ""
        except TypeError:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:  # noqa: BLE001 - retries should catch SDK-specific errors.
            last_error = exc
            if attempt >= max(max_retries, 1):
                break
            time.sleep(min(2**attempt, 30))

    raise RuntimeError(f"teacher model call failed after {max_retries} retries: {last_error}")


def call_teacher_model(
    messages: list[dict[str, str]],
    backend: str,
    model_name: str,
    base_url: str,
    api_key: str,
    max_retries: int,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> str:
    if backend == "mock":
        return call_mock_teacher(messages)

    if backend == "openai":
        resolved_api_key = api_key or first_env_value(
            "TEACHER_API_KEY",
            "LLM_API_KEY",
            "OPENAI_API_KEY",
        )
        if not resolved_api_key:
            raise ValueError("OPENAI_API_KEY is required for --teacher_backend openai")
        return call_openai_compatible(
            messages,
            model_name=model_name,
            base_url=base_url,
            api_key=resolved_api_key,
            max_retries=max_retries,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if backend == "local":
        if not base_url:
            raise ValueError("--base_url is required for --teacher_backend local")
        resolved_api_key = api_key or first_env_value(
            "TEACHER_API_KEY",
            "LLM_API_KEY",
            "OPENAI_API_KEY",
            default="EMPTY",
        )
        return call_openai_compatible(
            messages,
            model_name=model_name,
            base_url=base_url,
            api_key=resolved_api_key,
            max_retries=max_retries,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(f"Unsupported teacher backend: {backend}")


def validate_teacher_output(output: str, expected_answer: str) -> tuple[bool, str, str]:
    text = output.strip() if isinstance(output, str) else ""
    if not text:
        return False, "empty_output", "output is empty"

    required_tags = ("<think>", "</think>", "<answer>", "</answer>")
    missing_tags = [tag for tag in required_tags if tag not in text]
    if missing_tags:
        return False, "invalid_format", f"missing tags: {', '.join(missing_tags)}"

    matches = list(re.finditer(r"<answer>\s*([^<]+?)\s*</answer>", text))
    if len(matches) != 1:
        return False, "invalid_format", f"expected exactly one answer tag, found {len(matches)}"

    parsed_answer = matches[0].group(1).strip()
    if parsed_answer != expected_answer:
        return (
            False,
            "answer_mismatch",
            f"expected answer {expected_answer}, got {parsed_answer}",
        )

    extra_text = text[matches[0].end() :].strip()
    if extra_text:
        return False, "invalid_format", "text found after final </answer> tag"

    return True, "", ""


def build_sft_row(sample: dict[str, Any], output: str) -> dict[str, Any]:
    return {
        "id": clean_text(sample.get("id")),
        "source": clean_text(sample.get("source")),
        "split": clean_text(sample.get("split")),
        "instruction": INSTRUCTION,
        "input": format_sft_input(sample),
        "output": output.strip(),
        "answer": clean_text(sample.get("answer")).upper(),
        "answer_text": clean_text(sample.get("answer_text")),
        "subject": clean_text(sample.get("subject")),
        "topic": clean_text(sample.get("topic")),
        "quality_tier": clean_text(sample.get("quality_tier")),
        "question_type": clean_text(sample.get("question_type")),
        "clinical_score": sample.get("clinical_score", 0),
        "expected_step_range": clean_text(sample.get("expected_step_range")),
        "cot_source": "teacher_generated",
    }


def build_rejected_row(
    sample: dict[str, Any],
    reason: str,
    error: str,
    raw_output: str = "",
) -> dict[str, Any]:
    return {
        "id": clean_text(sample.get("id")),
        "source": clean_text(sample.get("source")),
        "split": clean_text(sample.get("split")),
        "reject_reason": reason,
        "error": error,
        "sample": sample,
        "raw_output": raw_output,
    }


def load_existing_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for row in iter_jsonl(path) or []:
        sample_id = clean_text(row.get("id"))
        if sample_id:
            ids.add(sample_id)
    return ids


def generate_one_sample(
    sample: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[str, dict[str, Any], str]:
    raw_output = ""
    try:
        messages = build_teacher_messages(sample)
    except Exception as exc:  # noqa: BLE001 - malformed sample should be rejected, not fatal.
        return "rejected", build_rejected_row(sample, "parse_error", str(exc)), "parse_error"

    try:
        raw_output = call_teacher_model(
            messages,
            backend=args.teacher_backend,
            model_name=args.model_name,
            base_url=args.base_url,
            api_key=args.api_key,
            max_retries=args.max_retries,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001 - API failure should not stop the batch.
        return (
            "rejected",
            build_rejected_row(sample, "api_error", str(exc), raw_output=raw_output),
            "api_error",
        )

    ok, reason, error = validate_teacher_output(raw_output, clean_text(sample.get("answer")).upper())
    if not ok:
        return (
            "rejected",
            build_rejected_row(sample, reason, error, raw_output=raw_output),
            reason,
        )

    return "generated", build_sft_row(sample, raw_output), ""


def split_pending_rows(
    rows: list[dict[str, Any]],
    existing_ids: set[str],
) -> tuple[list[dict[str, Any]], Counter[str]]:
    stats: Counter[str] = Counter()
    pending_rows: list[dict[str, Any]] = []
    for sample in rows:
        sample_id = clean_text(sample.get("id"))
        if sample_id in existing_ids:
            stats["skipped_resume"] += 1
            continue
        pending_rows.append(sample)
    return pending_rows, stats


def process_result(
    result: tuple[str, dict[str, Any], str],
    output_path: Path,
    rejected_path: Path,
    existing_ids: set[str],
    stats: Counter[str],
) -> None:
    status, row, reason = result
    if status == "generated":
        append_jsonl(output_path, row)
        existing_ids.add(clean_text(row.get("id")))
        stats["generated"] += 1
        return

    append_jsonl(rejected_path, row)
    stats["rejected"] += 1
    stats[reason or "unknown"] += 1


def process_split_sequential(
    rows: list[dict[str, Any]],
    output_path: Path,
    rejected_path: Path,
    existing_ids: set[str],
    args: argparse.Namespace,
) -> Counter[str]:
    pending_rows, stats = split_pending_rows(rows, existing_ids)
    batch_size = max(args.batch_size, 1)

    for index, sample in enumerate(pending_rows, start=1):
        result = generate_one_sample(sample, args)
        process_result(result, output_path, rejected_path, existing_ids, stats)
        if args.sleep_seconds > 0 and index % batch_size == 0:
            time.sleep(args.sleep_seconds)

    return stats


def process_split_concurrent(
    rows: list[dict[str, Any]],
    output_path: Path,
    rejected_path: Path,
    existing_ids: set[str],
    args: argparse.Namespace,
) -> Counter[str]:
    pending_rows, stats = split_pending_rows(rows, existing_ids)
    if not pending_rows:
        return stats

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(args.num_workers, 1)) as executor:
        future_to_sample = {
            executor.submit(generate_one_sample, sample, args): sample for sample in pending_rows
        }
        for completed_count, future in enumerate(
            concurrent.futures.as_completed(future_to_sample),
            start=1,
        ):
            sample = future_to_sample[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - defensive guard around worker failures.
                result = (
                    "rejected",
                    build_rejected_row(sample, "api_error", str(exc)),
                    "api_error",
                )
            process_result(result, output_path, rejected_path, existing_ids, stats)
            if args.sleep_seconds > 0 and completed_count % max(args.batch_size, 1) == 0:
                time.sleep(args.sleep_seconds)

    return stats


def process_split(
    rows: list[dict[str, Any]],
    output_path: Path,
    rejected_path: Path,
    existing_ids: set[str],
    args: argparse.Namespace,
) -> Counter[str]:
    if args.num_workers <= 1:
        return process_split_sequential(rows, output_path, rejected_path, existing_ids, args)
    return process_split_concurrent(rows, output_path, rejected_path, existing_ids, args)


def output_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "train": output_dir / "teacher_generated_sft_train.raw.jsonl",
        "dev": output_dir / "teacher_generated_sft_dev.raw.jsonl",
        "rejected": output_dir / "teacher_generated_sft_rejected_generation.jsonl",
        "preview": output_dir / "teacher_generated_sft_preview_50.jsonl",
    }


def prepare_outputs(paths: dict[str, Path], resume: bool) -> None:
    if resume:
        paths["train"].parent.mkdir(parents=True, exist_ok=True)
        return
    truncate_outputs([paths["train"], paths["dev"], paths["rejected"], paths["preview"]])


def collect_raw_rows(paths: dict[str, Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(list(iter_jsonl(paths["train"]) or []))
    rows.extend(list(iter_jsonl(paths["dev"]) or []))
    return rows


def build_preview(paths: dict[str, Path], seed: int) -> list[dict[str, Any]]:
    raw_rows = collect_raw_rows(paths)
    rng = random.Random(seed)
    preview_rows = rng.sample(raw_rows, k=min(50, len(raw_rows))) if raw_rows else []
    write_jsonl(paths["preview"], preview_rows)
    return preview_rows


def summarize_raw_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output_lengths = [len(row.get("output", "")) for row in rows]
    return {
        "source_counts": Counter(row.get("source") or "unknown" for row in rows),
        "tier_counts": Counter(row.get("quality_tier") or "<EMPTY>" for row in rows),
        "question_type_counts": Counter(row.get("question_type") or "<EMPTY>" for row in rows),
        "answer_counts": Counter(row.get("answer") or "unknown" for row in rows),
        "avg_output_len": sum(output_lengths) / len(output_lengths) if output_lengths else 0.0,
        "min_output_len": min(output_lengths) if output_lengths else 0,
        "max_output_len": max(output_lengths) if output_lengths else 0,
    }


def summarize_rejections(path: Path) -> Counter[str]:
    reasons: Counter[str] = Counter()
    for row in iter_jsonl(path) or []:
        reasons[row.get("reject_reason") or "unknown"] += 1
    return reasons


def counter_lines(counter: Counter[Any]) -> list[str]:
    if not counter:
        return ["- 无"]
    return [f"- `{key}`：{value}" for key, value in counter.most_common()]


def write_report(
    report_path: Path,
    paths: dict[str, Path],
    args: argparse.Namespace,
    train_input_count: int,
    dev_input_count: int,
    split_stats: dict[str, Counter[str]],
) -> None:
    train_rows = list(iter_jsonl(paths["train"]) or [])
    dev_rows = list(iter_jsonl(paths["dev"]) or [])
    all_rows = train_rows + dev_rows
    raw_summary = summarize_raw_rows(all_rows)
    rejected_reason_counts = summarize_rejections(paths["rejected"])
    rejected_count = sum(rejected_reason_counts.values())
    completed = (
        len(train_rows)
        + len(dev_rows)
        + rejected_count
        >= train_input_count + dev_input_count
    )

    lines = [
        "# Teacher SFT Raw 生成报告",
        "",
        f"- backend：`{args.teacher_backend}`",
        f"- model_name：`{args.model_name or '<EMPTY>'}`",
        f"- num_workers：{args.num_workers}",
        f"- train 输入数量：{train_input_count}",
        f"- dev 输入数量：{dev_input_count}",
        f"- train raw 生成数量：{len(train_rows)}",
        f"- dev raw 生成数量：{len(dev_rows)}",
        f"- rejected_generation 数量：{rejected_count}",
        f"- preview_50 路径：`{paths['preview']}`",
        f"- 是否完成全部输入样本：{'是' if completed else '否'}",
        "",
        "## 本次运行统计",
        "",
        f"- train 新生成：{split_stats['train'].get('generated', 0)}",
        f"- train resume 跳过：{split_stats['train'].get('skipped_resume', 0)}",
        f"- train rejected：{split_stats['train'].get('rejected', 0)}",
        f"- dev 新生成：{split_stats['dev'].get('generated', 0)}",
        f"- dev resume 跳过：{split_stats['dev'].get('skipped_resume', 0)}",
        f"- dev rejected：{split_stats['dev'].get('rejected', 0)}",
        "",
        "## rejected reason 分布",
        "",
        *counter_lines(rejected_reason_counts),
        "",
        "## source 分布",
        "",
        *counter_lines(raw_summary["source_counts"]),
        "",
        "## quality_tier 分布",
        "",
        *counter_lines(raw_summary["tier_counts"]),
        "",
        "## question_type 分布",
        "",
        *counter_lines(raw_summary["question_type_counts"]),
        "",
        "## answer 分布",
        "",
        *counter_lines(raw_summary["answer_counts"]),
        "",
        "## output 长度",
        "",
        f"- 平均 output 长度：{raw_summary['avg_output_len']:.2f}",
        f"- 最短 output：{raw_summary['min_output_len']}",
        f"- 最长 output：{raw_summary['max_output_len']}",
    ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def print_summary(paths: dict[str, Path], report_path: Path) -> None:
    train_count = sum(1 for _ in iter_jsonl(paths["train"]) or [])
    dev_count = sum(1 for _ in iter_jsonl(paths["dev"]) or [])
    rejected_count = sum(1 for _ in iter_jsonl(paths["rejected"]) or [])
    print("Teacher SFT raw generation finished.")
    print(f"  train raw: {train_count}")
    print(f"  dev raw: {dev_count}")
    print(f"  rejected: {rejected_count}")
    print(f"  preview: {paths['preview']}")
    print(f"  report: {report_path}")


def main() -> None:
    args = parse_args()
    apply_env_defaults(args)
    paths = output_paths(args.output_dir)

    try:
        train_rows = read_jsonl(args.train_input, args.max_train_samples)
        dev_rows = read_jsonl(args.dev_input, args.max_dev_samples)
        prepare_outputs(paths, args.resume)

        existing_train_ids = load_existing_ids(paths["train"]) if args.resume else set()
        existing_dev_ids = load_existing_ids(paths["dev"]) if args.resume else set()

        train_stats = process_split(
            train_rows,
            paths["train"],
            paths["rejected"],
            existing_train_ids,
            args,
        )
        dev_stats = process_split(
            dev_rows,
            paths["dev"],
            paths["rejected"],
            existing_dev_ids,
            args,
        )

        build_preview(paths, args.seed)
        write_report(
            args.report_path,
            paths,
            args,
            train_input_count=len(train_rows),
            dev_input_count=len(dev_rows),
            split_stats={"train": train_stats, "dev": dev_stats},
        )
        print_summary(paths, args.report_path)
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI should surface a clear failure.
        raise SystemExit(f"ERROR: failed to generate teacher SFT data: {exc}") from exc


if __name__ == "__main__":
    main()
