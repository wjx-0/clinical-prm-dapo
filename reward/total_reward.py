"""Combine project reward components for verl."""

try:
    from reward.answer_reward import score_answer
    from reward.format_reward import score_format
    from reward.length_reward import score_length
except ImportError:
    from answer_reward import score_answer
    from format_reward import score_format
    from length_reward import score_length


def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    """verl-compatible reward hook.

    Adjust this signature if your installed verl recipe expects a different
    reward function interface.
    """
    del data_source, extra_info
    answer_score = score_answer(solution_str, ground_truth)
    format_score = score_format(solution_str)
    length_score = score_length(solution_str)
    return 0.7 * answer_score + 0.2 * format_score + 0.1 * length_score
