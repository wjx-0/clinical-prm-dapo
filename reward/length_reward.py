"""Length reward utilities."""


def score_length(response: str, max_chars: int = 4096) -> float:
    return 1.0 if len(response) <= max_chars else 0.0

