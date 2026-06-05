"""Final-answer reward utilities."""


def score_answer(prediction: str, gold: str) -> float:
    return 1.0 if prediction.strip().upper() == gold.strip().upper() else 0.0

