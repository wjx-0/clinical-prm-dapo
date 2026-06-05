"""Format reward utilities for reasoning responses."""


def score_format(response: str) -> float:
    has_think = "<think>" in response and "</think>" in response
    has_answer = "<answer>" in response and "</answer>" in response
    return 1.0 if has_think and has_answer else 0.0

