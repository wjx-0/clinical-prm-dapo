# MedMCQA 学科题目总数

- generated_at_utc: `2026-06-07T06:03:07+00:00`
- note: 统计 processed MedMCQA 的 train/dev/labeled test/unlabeled test；官方 test 无答案，保存在 test_unlabeled。

## Split 总数

| split | path | 题数 | 占比 |
| --- | --- | ---: | --- |
| train | `data/processed/medmcqa_train.jsonl` | 182822 | 94.65% |
| dev | `data/processed/medmcqa_dev.jsonl` | 4183 | 2.17% |
| test_labeled | `data/processed/medmcqa_test.jsonl` | 0 | 0.00% |
| test_unlabeled | `data/processed/medmcqa_test_unlabeled.jsonl` | 6150 | 3.18% |

## 各学科总数

| subject | total | train | dev | test_labeled | test_unlabeled | total_pct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Medicine | 18554 | 17887 | 295 | 0 | 372 | 9.61% |
| Surgery | 17732 | 16862 | 369 | 0 | 501 | 9.18% |
| Pathology | 15526 | 14884 | 337 | 0 | 305 | 8.04% |
| Anatomy | 15053 | 14560 | 234 | 0 | 259 | 7.79% |
| Pharmacology | 14318 | 13758 | 243 | 0 | 317 | 7.41% |
| Social & Preventive Medicine | 12254 | 11882 | 129 | 0 | 243 | 6.34% |
| Microbiology | 11603 | 11314 | 122 | 0 | 167 | 6.01% |
| Dental | 11459 | 8938 | 1318 | 0 | 1203 | 5.93% |
| Gynaecology & Obstetrics | 10769 | 10013 | 224 | 0 | 532 | 5.58% |
| Physiology | 9389 | 8830 | 171 | 0 | 388 | 4.86% |
| Biochemistry | 8805 | 8282 | 171 | 0 | 352 | 4.56% |
| Pediatrics | 8461 | 8037 | 234 | 0 | 190 | 4.38% |
| Ophthalmology | 7167 | 6932 | 58 | 0 | 177 | 3.71% |
| Forensic Medicine | 6099 | 5900 | 67 | 0 | 132 | 3.16% |
| ENT | 5058 | 4919 | 53 | 0 | 86 | 2.62% |
| Radiology | 4583 | 4395 | 69 | 0 | 119 | 2.37% |
| Psychiatry | 4464 | 4442 | 16 | 0 | 6 | 2.31% |
| Unknown | 3729 | 3045 | 2 | 0 | 682 | 1.93% |
| Anaesthesia | 3265 | 3172 | 34 | 0 | 59 | 1.69% |
| Orthopaedics | 3019 | 2999 | 20 | 0 | 0 | 1.56% |
| Skin | 1848 | 1771 | 17 | 0 | 60 | 0.96% |

## Topic Top 30

| topic | 题数 | 占比 |
| --- | ---: | --- |
| <EMPTY> | 105523 | 54.63% |
| All India exam | 4021 | 2.08% |
| G.I.T | 2107 | 1.09% |
| Miscellaneous | 2091 | 1.08% |
| Endocrinology | 1711 | 0.89% |
| General anatomy | 1697 | 0.88% |
| C.V.S | 1114 | 0.58% |
| Cardiovascular system | 943 | 0.49% |
| General pathology | 869 | 0.45% |
| Respiratory system | 861 | 0.45% |
| Virology | 851 | 0.44% |
| Ear | 739 | 0.38% |
| C.N.S | 648 | 0.34% |
| Communicable diseases | 645 | 0.33% |
| Haematology | 643 | 0.33% |
| Immunology | 620 | 0.32% |
| Head and neck | 615 | 0.32% |
| Bacteriology | 610 | 0.32% |
| Epidemiology | 608 | 0.31% |
| Kidney | 563 | 0.29% |
| Bacteria | 536 | 0.28% |
| Nervous System | 504 | 0.26% |
| Urology | 494 | 0.26% |
| General obstetrics | 484 | 0.25% |
| Chemotherapy | 482 | 0.25% |
| Misc. | 476 | 0.25% |
| Other topics and Adverse effects | 470 | 0.24% |
| Nervous system | 463 | 0.24% |
| Infection | 436 | 0.23% |
| C.V.S. | 433 | 0.22% |
