"""Extract final multiple-choice answers from model responses."""

import re
from typing import Optional


ANSWER_RE = re.compile(r"<answer>\s*([A-Z])\s*</answer>", re.IGNORECASE)


def extract_answer(response: str) -> Optional[str]:
    match = ANSWER_RE.search(response)
    return match.group(1).upper() if match else None
