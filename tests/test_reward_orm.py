from reward.answer_reward import extract_answer_letter
from reward.length_reward import score_length
from reward.process_reward import score_process
from reward.total_reward import compute_score


EXTRA_INFO = {
    "options": {
        "A": "Improper contact lens hygiene",
        "B": "Ability of Pseudomonas to produce biofilms",
        "C": "Frequent use of topical antibiotics",
        "D": "Transfer resistance genes from flora",
    },
    "answer_text": "Ability of Pseudomonas to produce biofilms",
}


def test_answer_prefers_last_tag():
    assert extract_answer_letter("<answer>A</answer> text <answer>B</answer>") == "B"


def test_length_penalizes_truncated_output():
    assert score_length("<think>unfinished reasoning") == 0.0
    assert score_length("<answer>B</answer>") == 0.2


def test_length_penalizes_overly_long_output():
    normal = "x" * 1000
    long = "x" * 3500
    assert score_length(normal) == 1.0
    assert 0.0 < score_length(long) < 1.0
    assert score_length("x" * 5000) == 0.0


def test_process_rewards_grounded_reasoning():
    response = (
        "<think>Pseudomonas can persist because biofilms protect organisms on "
        "contact lenses and make antimicrobial eradication less likely.</think>"
        "<answer>B</answer>"
    )
    assert score_process(response, EXTRA_INFO) > 0.8


def test_orm_v2_keeps_answer_dominant(monkeypatch):
    monkeypatch.setenv("REWARD_PROFILE", "orm_v2")
    correct = (
        "<think>Pseudomonas can persist because biofilms protect organisms on "
        "contact lenses and make antimicrobial eradication less likely.</think>"
        "<answer>B</answer>"
    )
    wrong = correct.replace("<answer>B</answer>", "<answer>A</answer>")
    assert compute_score("medical_mcqa", correct, {"ground_truth": "B"}, EXTRA_INFO) > 1.1
    assert compute_score("medical_mcqa", wrong, {"ground_truth": "B"}, EXTRA_INFO) < 0.2
