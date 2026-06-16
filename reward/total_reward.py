"""Combine project reward components for verl."""

from __future__ import annotations

from typing import Any

try:
    from reward.answer_reward import score_answer
    from reward.consistency_reward import score_consistency
    from reward.format_reward import FULL_FORMAT_RE, score_format
    from reward.length_reward import score_length
    from reward.process_reward import score_process
    from reward.prm_reward import load_reward_config, score_prm
except ImportError:
    from answer_reward import score_answer
    from consistency_reward import score_consistency
    from format_reward import FULL_FORMAT_RE, score_format
    from length_reward import score_length
    from process_reward import score_process
    from prm_reward import load_reward_config, score_prm


DEFAULT_PROFILES = {
    "orm_v1": {
        "answer": 1.0,
        "format": 0.1,
        "length": 0.05,
        "prm": 0.0,
        "consistency": 0.0,
    },
    "orm_v2": {
        "answer": 1.0,
        "format": 0.08,
        "process": 0.05,
        "consistency": 0.04,
        "length": 0.02,
        "prm": 0.0,
    },
    "prm_v1": {
        "answer": 0.5,
        "prm": 0.2,
        "format": 0.15,
        "process": 0.0,
        "consistency": 0.1,
        "length": 0.05,
    },
}


def _extract_ground_truth(ground_truth: Any) -> Any:
    if isinstance(ground_truth, dict):
        return ground_truth.get("ground_truth") or ground_truth.get("answer") or ground_truth
    return ground_truth


def _active_weights(config: dict[str, Any]) -> dict[str, float]:
    import os

    profiles = config.get("profiles") if isinstance(config.get("profiles"), dict) else {}
    active_profile = os.environ.get("REWARD_PROFILE") or config.get("active_profile") or "orm_v2"
    configured = profiles.get(active_profile) if isinstance(profiles.get(active_profile), dict) else None
    weights = dict(configured or DEFAULT_PROFILES.get(active_profile) or DEFAULT_PROFILES["orm_v2"])

    if os.environ.get("PRM_ENABLED", "").lower() in {"0", "false", "no", "off"}:
        weights["prm"] = 0.0
    if os.environ.get("CONSISTENCY_ENABLED", "").lower() in {"0", "false", "no", "off"}:
        weights["consistency"] = 0.0
    return {key: float(value) for key, value in weights.items()}


def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    """verl-compatible reward hook.

    verl passes the generated response as ``solution_str`` and the reference
    answer as ``ground_truth``. The active reward profile is configured in
    ``configs/verl/reward_config.yaml`` and can be overridden with
    ``REWARD_PROFILE``.
    """
    del data_source
    config = load_reward_config()
    weights = _active_weights(config)
    gold = _extract_ground_truth(ground_truth)

    components: dict[str, float] = {}
    if weights.get("answer", 0.0):
        components["answer"] = score_answer(solution_str, gold)
    if weights.get("format", 0.0):
        components["format"] = score_format(solution_str)
    if weights.get("process", 0.0):
        components["process"] = score_process(solution_str, extra_info=extra_info)
    if weights.get("length", 0.0):
        components["length"] = score_length(solution_str, config=config)
    if weights.get("prm", 0.0):
        components["prm"] = score_prm(
            solution_str,
            ground_truth=gold,
            extra_info=extra_info,
            config=config,
        )
    if weights.get("consistency", 0.0):
        components["consistency"] = score_consistency(solution_str, extra_info=extra_info)
    total = sum(weights.get(name, 0.0) * components[name] for name in components)
    if not FULL_FORMAT_RE.match(str(solution_str)):
        total = min(total, 0.3)
    return total
