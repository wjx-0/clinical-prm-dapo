# LLM Judge SFT 逐条评估报告

## Summary

- judged rows：300

## Verdict

- `PASS`：290
- `WARN`：6
- `FAIL`：4

## Tier / Verdict

- `A/PASS`：222
- `B/PASS`：68
- `B/WARN`：4
- `B/FAIL`：3
- `A/WARN`：2
- `A/FAIL`：1

## Issues

- `RBC casts atypical for PAN`：2
- `incorrect erythromycin CYP induction mechanism`：1
- `minor ungrounded ECG detail`：1
- `ungrounded imaging findings`：1
- `references unstated CT findings`：1
- `ungrounded_ecg_interpretation`：1
- `invented_ecg_findings`：1
- `febuxostat-azathioprine interaction omitted`：1
- `medically unsafe reasoning`：1
- `ungrounded ECG findings`：1
- `c-peptide physiology imprecise`：1

## Flagged Rows

| id | tier | source | rule | judge | issues | comment |
|---|---|---|---|---|---|---|
| `medmcqa_train_000439` | A | medmcqa | PASS | FAIL | incorrect erythromycin CYP induction mechanism | The answer is correct, but the reasoning includes the incorrect claim that erythromycin increases hepatic cytochrome P450 activity. |
| `medmcqa_train_012054` | B | medmcqa | PASS | WARN | RBC casts atypical for PAN | The answer matches the expected option and reasoning is mostly grounded, though RBC casts are atypical for classic polyarteritis nodosa. |
| `medmcqa_train_040096` | B | medmcqa | PASS | WARN | RBC casts atypical for PAN | The answer matches the expected choice and reasoning is mostly sound, though RBC casts suggest glomerulonephritis and are atypical for classic polyarteritis nodosa. |
| `medmcqa_train_040770` | A | medmcqa | PASS | WARN | minor ungrounded ECG detail | The answer and core HFpEF reasoning are correct, but it slightly overstates the ECG findings by saying there are no ischemic changes when only absence of Q waves is specified. |
| `medmcqa_train_078108` | B | medmcqa | PASS | WARN | ungrounded imaging findings | The answer is correct and medically plausible, but the reasoning refers to characteristic CT findings that are not provided in the question text. |
| `medmcqa_train_119821` | B | medmcqa | PASS | WARN | references unstated CT findings | The answer is correct and medically plausible, but the reasoning relies on classic CT features that are not provided in the text. |
| `medmcqa_train_152272` | B | medmcqa | PASS | FAIL | ungrounded_ecg_interpretation, invented_ecg_findings | The final answer is correct and facts are reasonable, but the reasoning invents specific ECG findings not present in the provided text. |
| `medmcqa_train_167584` | B | medmcqa | PASS | FAIL | febuxostat-azathioprine interaction omitted, medically unsafe reasoning | Although the final letter matches, febuxostat is also contraindicated or should be avoided with azathioprine due to xanthine oxidase inhibition and risk of severe toxicity. |
| `medmcqa_train_177801` | B | medmcqa | PASS | FAIL | ungrounded ECG findings | The answer is correct, but it cites specific ECG features that are not provided in the text input. |
| `medqa_train_008364` | A | medqa | PASS | WARN | c-peptide physiology imprecise | The answer letter matches, but exogenous insulin classically causes low rather than normal C-peptide, making the medical reasoning imprecise. |
