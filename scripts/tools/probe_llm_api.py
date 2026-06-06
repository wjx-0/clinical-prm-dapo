"""Probe an OpenAI-compatible LLM API without printing secrets.

Examples:
  LLM_API_KEY=... python scripts/tools/probe_llm_api.py --base_url https://api.openai.com/v1
  LLM_API_KEY=... python scripts/tools/probe_llm_api.py --base_url http://localhost:8000/v1 --model_name qwen2.5-7b-instruct
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe OpenAI-compatible model APIs.")
    parser.add_argument(
        "--base_url",
        default="https://api.openai.com/v1",
        help="OpenAI-compatible base URL, usually ending with /v1.",
    )
    parser.add_argument(
        "--api_key",
        default="",
        help="API key. Defaults to LLM_API_KEY, then OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--model_name",
        default="",
        help="Optional model id to test with /chat/completions.",
    )
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument(
        "--output_path",
        type=Path,
        default=Path("outputs/api_probe/model_probe_result.json"),
    )
    return parser.parse_args()


def resolve_api_key(cli_key: str) -> str:
    return cli_key or os.environ.get("LLM_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")


def join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def request_json(
    method: str,
    url: str,
    api_key: str,
    payload: dict[str, Any] | None,
    timeout: int,
) -> tuple[int, dict[str, Any] | list[Any] | str]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: dict[str, Any] | list[Any] | str = json.loads(body)
        except json.JSONDecodeError:
            parsed = body[:2000]
        return exc.code, parsed
    except urllib.error.URLError as exc:
        return 0, f"network error: {exc.reason}"


def extract_model_ids(models_response: dict[str, Any] | list[Any] | str) -> list[str]:
    if isinstance(models_response, dict):
        data = models_response.get("data")
        if isinstance(data, list):
            ids = [item.get("id") for item in data if isinstance(item, dict) and item.get("id")]
            return sorted(str(model_id) for model_id in ids)
        if isinstance(models_response.get("models"), list):
            return sorted(str(model_id) for model_id in models_response["models"])
    if isinstance(models_response, list):
        ids = [item.get("id") for item in models_response if isinstance(item, dict) and item.get("id")]
        return sorted(str(model_id) for model_id in ids)
    return []


def probe_models(base_url: str, api_key: str, timeout: int) -> tuple[int, Any, list[str]]:
    status, response = request_json(
        "GET",
        join_url(base_url, "/models"),
        api_key=api_key,
        payload=None,
        timeout=timeout,
    )
    return status, response, extract_model_ids(response)


def probe_chat(
    base_url: str,
    api_key: str,
    model_name: str,
    timeout: int,
) -> tuple[int, Any]:
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Reply with exactly: ok"},
        ],
        "temperature": 0,
        "max_tokens": 8,
    }
    return request_json(
        "POST",
        join_url(base_url, "/chat/completions"),
        api_key=api_key,
        payload=payload,
        timeout=timeout,
    )


def summarize_chat_response(response: Any) -> str:
    if not isinstance(response, dict):
        return ""
    try:
        return str(response["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError):
        return ""


def write_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    api_key = resolve_api_key(args.api_key)
    if not api_key:
        raise SystemExit(
            "ERROR: missing API key. Set LLM_API_KEY or OPENAI_API_KEY, or pass --api_key."
        )

    result: dict[str, Any] = {
        "base_url": args.base_url,
        "api_key_present": True,
        "models_status": None,
        "models": [],
        "chat_status": None,
        "chat_model": args.model_name,
        "chat_text": "",
        "notes": [],
    }

    models_status, models_response, model_ids = probe_models(args.base_url, api_key, args.timeout)
    result["models_status"] = models_status
    result["models"] = model_ids

    print(f"Base URL: {args.base_url}")
    print(f"API key: present ({len(api_key)} chars, not printed)")
    print(f"/models status: {models_status}")

    if model_ids:
        print("Available model ids:")
        for model_id in model_ids:
            print(f"  - {model_id}")
    else:
        print("No model ids were returned by /models.")
        result["notes"].append(
            "The endpoint did not expose model ids via /models; exact model identity may be hidden."
        )
        if models_status not in (200, 0):
            print(f"/models response preview: {json.dumps(models_response, ensure_ascii=False)[:1000]}")

    if args.model_name:
        chat_status, chat_response = probe_chat(
            args.base_url,
            api_key,
            args.model_name,
            args.timeout,
        )
        result["chat_status"] = chat_status
        result["chat_text"] = summarize_chat_response(chat_response)
        print(f"/chat/completions status for {args.model_name}: {chat_status}")
        print(f"Chat response text: {result['chat_text'] or '<EMPTY>'}")
        if chat_status != 200:
            result["notes"].append("The specified model failed the chat probe.")
            print(f"Chat error preview: {json.dumps(chat_response, ensure_ascii=False)[:1000]}")

    write_result(args.output_path, result)
    print(f"Probe result written to: {args.output_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI should show a clear failure.
        print(f"ERROR: API probe failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
