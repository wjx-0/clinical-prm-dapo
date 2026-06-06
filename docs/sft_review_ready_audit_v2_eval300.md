# Review Ready Audit v2_eval300

## Summary

- base file: data/sft/v2_eval300/medical_cot_sft_train.external_ultra_strict_pass.jsonl
- review_ready_pass rows: 242
- review_ready_public rows: 242
- removed residual noisy rows: 6
- A tier: 186 (76.86%)
- B tier: 56 (23.14%)
- source medqa: 83
- source medmcqa: 159

## Field Checks

- answer tag mismatch: 0
- output data-trace hits: 0
- missing visual/ECG/CT context hits: 0
- tier step-range violations: 0
- step distribution: 3 steps=56, 5 steps=170, 6 steps=16

## Removed Rows

| id | tier | source | hit | answer_text | preview |
|---|---|---|---|---|---|
| `medmcqa_train_134690` | B | medmcqa | `Gestaut` | Lennox Gestaut syndrome | Question: 4 year old child presents with developmental delay and episodes of multiple seizures types. The child did not respond despite multiple drug therapy. EEG showed 1-2Hz spike and wave pattern. What is the diagnosis Options: A. Lennox Gestaut syndrome B |
| `medmcqa_train_004987` | B | medmcqa | `Aspaate` | Amylase | Question: A 27 year old man develops bilateral parotid gland swelling and orchitis, and is generally ill with fever of 102deg F. Which of the following substances is most likely to be significantly elevated in the patient's serum? Options: A. Alanine aminotra |
| `medmcqa_train_113960` | B | medmcqa | `ours a diagnosis` | Lesions without increased tracer activity on FDG-18 PET imaging | Question: A 37-year-old man with AIDS presents with confusion, lethargy and memory loss. CT of the brain demonstrates multiple supratentorial enhancing masses. Which imaging feature ours a diagnosis of toxoplasmosis rather than primary CNS lymphoma? Options:  |
| `medmcqa_train_020602` | A | medmcqa | `sta IV` | Manage hypokalemia-Repeat serum K+ levels- IV fluids and sta IV regular insulin | Question: A 45 year old male known case of diabetes presents with nausea, multiple episodes of vomiting and abdominal pain.He is stuporous, having blood glucoselevel of 402 mg% and on urine examination Ketone bodies are detected.He is having tachycardina along |
| `medmcqa_train_115417` | A | medmcqa | `aspaate` | Complete resolution | Question: A 26-year-old woman presents to her primary care physician with fever, malaise, and "yellow eyes." She denies alcohol abuse, but admits to indulging in a dozen raw oysters at happy hour 3 weeks ago. In addition to scleral icterus, physical examinatio |
| `medmcqa_train_028922` | B | medmcqa | `impairement` | Meningioma | Question: A 48-year old woman comes with bilateral progressive weakness of both lower limbs, spasticity and mild impairement of respiratory movements. MRI shows an intradural mid-dorsal midline enhancing lesion. What is the diagnosis? Options: A. Intradural l |
