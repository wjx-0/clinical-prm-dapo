# SFT Suspicious 隔离报告

## 样本数

- input train 样本数：4395
- input dev 样本数：0
- clean_core train 样本数：3086
- clean_core dev 样本数：0
- clean_plus_short_fact train 样本数：4100
- clean_plus_short_fact dev 样本数：0
- 纯 short_fact_question 放回扩量集样本数：1014
- 高风险 suspicious 总数：295
- 高风险 suspicious rate：6.71%

## 输出文件

- clean_core train：`data/sft/medical_cot_sft_train.clean.jsonl`
- clean_core dev：`data/sft/medical_cot_sft_dev.clean.jsonl`
- clean_plus_short_fact train：`data/sft/medical_cot_sft_train.clean_plus_short_fact.jsonl`
- clean_plus_short_fact dev：`data/sft/medical_cot_sft_dev.clean_plus_short_fact.jsonl`

## Suspicious Reason 分布

- `image_dependent`：151
- `composite_answer`：101
- `short_fact_question`：52
- `external_standard`：34
- `dirty_input`：6
- `date_artifact`：5
- `manual_blacklist`：4

## Suspicious Source 分布

- `medmcqa`：159
- `medqa`：136

## Suspicious Answer 分布

- `D`：125
- `C`：60
- `A`：57
- `B`：53

## Suspicious Subject Top 20

- `<EMPTY>`：136
- `Surgery`：14
- `Anatomy`：13
- `Microbiology`：13
- `Pathology`：13
- `Social & Preventive Medicine`：12
- `Medicine`：12
- `Pediatrics`：11
- `Biochemistry`：11
- `Dental`：10
- `Pharmacology`：8
- `Unknown`：8
- `Forensic Medicine`：7
- `Gynaecology & Obstetrics`：6
- `ENT`：4
- `Ophthalmology`：3
- `Physiology`：3
- `Anaesthesia`：3
- `Skin`：2
- `Psychiatry`：2

## 前 20 条 suspicious 样本预览

```json
{
  "id": "medqa_train_009274",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "A",
  "answer_text": "Cholecystectomy",
  "question": "A 64-year-old man presents to the outpatient clinic because of abdominal pain. He reports that for the last few months, he has had postprandial pain that is worsened by spicy foods. He states that the pain is often located in the right upper portion of his abdomen and feels like it's traveling to his shoulder blade. These episodes are sporadic and unpredictable. He denies any fevers. Physical examination shows no abnormalities. Abdominal ultrasound is shown. Which of the following is the best treatment for this condition?"
}
```

```json
{
  "id": "medqa_train_003720",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "B",
  "answer_text": "Administer heparin",
  "question": "A 30-year-old woman presents to her primary care provider with blood in her urine and pain in her left flank. She has a 5-year history of polycystic ovarian syndrome managed with oral contraceptives and metformin. She is single and is not sexually active and denies a history of kidney stones or abdominal trauma. She has a 15-pack-year smoking history but denies the use of other substances. Her family history is significant for fatal lung cancer in her father at age 50, who also smoked, and recently diagnosed bladder cancer in her 45-year-old brother, who never smoked. On review of systems, she denies weight loss, fever, fatigue, paresthesia, increased pain with urination, or excessive bleeding or easy bruising. She is admitted to the hospital for a workup and observation. Her vital signs and physical exam are within normal limits. A urine pregnancy test is negative. PT is 14 sec and PTT is 20 sec. The rest of the laboratory results including von Willebrand factor activity and lupus anticoagulant panel are pending. A CT angiogram is ordered and is shown in the picture. What is indicated at this time to prevent a potential sequela of this patient’s condition?"
}
```

```json
{
  "id": "medqa_train_003838",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "A",
  "answer_text": "Antibiotics + CT-guided drainage",
  "question": "A 72-year-old man is brought to the emergency department with increasing fever and abdominal pain over the past week. The pain is constant and limited to the lower right part of his abdomen. He has nausea but no vomiting or diarrhea. His past medical history is unremarkable for any serious illnesses. He takes acetaminophen for knee arthritis. He is fully alert and oriented. His temperature is 39.5°C (103.1°F), pulse is 89/min, respirations are 15/min, and blood pressure is 135/70 mm Hg. Abdominal examination shows a tender mass in the right lower quadrant. CT shows obstruction of the appendiceal neck with a fecalith and the appendiceal tip leading to an irregular walled-off fluid collection. Stranding of the surrounding fat planes is also noted. Intravenous hydration is initiated. Which of the following is the most appropriate next step in management?"
}
```

```json
{
  "id": "medmcqa_train_120077",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "external_standard",
    "short_fact_question"
  ],
  "answer": "D",
  "answer_text": "24 months",
  "question": "MDR/XDR treatment given for"
}
```

```json
{
  "id": "medqa_train_008968",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "B",
  "answer_text": "Endoscopy",
  "question": "A 14-year-old boy is brought to the emergency department because of abdominal swelling and vomiting over the past 24 hours. He has generalized abdominal pain. He has no history of any serious illnesses and takes no medications. His temperature is 36.7°C (98.1°F), blood pressure is 115/70 mm/Hg, pulse is 88/min, and respirations are 16/min. Abdominal examination shows diffuse swelling with active bowel sounds. Mild generalized tenderness without guarding or rebound is noted. His leukocyte count is 8,000/mm3. An X-ray of the abdomen is shown. Intravenous fluids have been initiated. Which of the following is the most appropriate next step in management?"
}
```

```json
{
  "id": "medqa_train_004267",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "A",
  "answer_text": "Cytomegalovirus",
  "question": "A 45-year-old man comes to the physician because of a 3-week history of progressive diarrhea and a 2.2-kg (5-lb) weight loss. During the past week, he has had six small bloody stools daily. He is employed as a sales manager and regularly flies to South America. He has HIV, gastroesophageal reflux disease, and hypertension. Current medications include chlorthalidone, omeprazole, emtricitabine, tenofovir, and efavirenz. He reports taking efavirenz irregularly. He is 175 cm (5 ft 9 in) tall and weighs 64 kg (143 lb); BMI is 22 kg/m2. His temperature is 38.1°C (100.6°F), pulse is 91/min, and blood pressure is 116/69 mm Hg. The abdomen is scaphoid. Bowel sounds are normal. His CD4+ T-lymphocyte count is 44/mm3 (N ≥ 500), leukocyte count is 6,000/mm3, and erythrocyte sedimentation rate is 12 mm/h. Colonoscopy shows areas of inflammation scattered throughout the colon with friability, granularity, and shallow linear ulcerations. The intervening mucosa between areas of inflammation appears normal. A biopsy specimen is shown. Which of the following is the most likely cause of this patient's symptoms?"
}
```

```json
{
  "id": "medmcqa_train_080321",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "composite_answer"
  ],
  "answer": "A",
  "answer_text": "ac",
  "question": "True about mesenteric cysta) Moves perpendicular to the line of attachmentb) Teratomatous is most commonc) Chylolymphatic cyst has separate blood supplyd) Surgical removal of bowel along cyst is treatment of choice in all the cyst"
}
```

```json
{
  "id": "medmcqa_train_157528",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "composite_answer"
  ],
  "answer": "C",
  "answer_text": "ab",
  "question": "Not true regarding influenza virus is -a) All types exhibit antigenic shiftb) Only type A shows antigenic driftc) Drift is accumulation of point mutationsd) None of the above"
}
```

```json
{
  "id": "medqa_train_005213",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "D",
  "answer_text": "Between the arachnoid mater and the pia mater",
  "question": "A 54-year-old man is brought to the emergency department 30 minutes after being hit by a car while crossing the street. He had a left-sided tonic-clonic seizure and one episode of vomiting while being transported to the hospital. On arrival, he is not oriented to person, place, or time. Physical examination shows flaccid paralysis of all extremities. A CT scan of the head is shown. This patient's symptoms are most likely the result of a hemorrhage in which of the following structures?"
}
```

```json
{
  "id": "medmcqa_train_006899",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "external_standard"
  ],
  "answer": "A",
  "answer_text": "Respiratory syncytial virus",
  "question": "Several antiviral compounds have been developed during the last decade. One such compound is ribavirin, a synthetic nucleoside structurally related to guanosine. Ribavirin therapy has been successfully used against"
}
```

```json
{
  "id": "medmcqa_train_041090",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "composite_answer"
  ],
  "answer": "D",
  "answer_text": "All of the above",
  "question": "Which of the following statement(s) is/are true concerning topical antimicrobials in common use today?"
}
```

```json
{
  "id": "medmcqa_train_079667",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "external_standard"
  ],
  "answer": "D",
  "answer_text": "Group D",
  "question": "Roflumilast is introduced in management of COPD in?"
}
```

```json
{
  "id": "medqa_train_001462",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "A",
  "answer_text": "Curve A",
  "question": "Scientists are developing a new non-steroidal anti-inflammatory drug for osteoarthritis. Their hope is that the new drug will have a higher potency but the same efficacy as ibuprofen in the hope of minimizing gastrointestinal side effects. If ibuprofen is curve C in the figure provided, which of the following would be the curve for the new drug based on the scientists’ specifications? The desired therapeutic effect in patients is represented by the dashed line Y."
}
```

```json
{
  "id": "medmcqa_train_141516",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "composite_answer",
    "short_fact_question"
  ],
  "answer": "D",
  "answer_text": "All of the above",
  "question": "Acanthosis nigricans is associated with?"
}
```

```json
{
  "id": "medmcqa_train_144590",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "dirty_input"
  ],
  "answer": "D",
  "answer_text": "Oxygen saturation",
  "question": "The children hospital eastern ontario pain scale (cheops) for rating post operative pain in children in cludes all except aEUR'"
}
```

```json
{
  "id": "medqa_train_008584",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "D",
  "answer_text": "Mycoplasma pneumoniae",
  "question": "A 43-year-old woman comes to the physician because of a fever, nausea, and a nonproductive cough for 7 days. During this period, she has had headaches, generalized fatigue, and muscle and joint pain. She has also had increasing shortness of breath for 2 days. She has type 2 diabetes mellitus and osteoarthritis of her left knee. Current medications include insulin and ibuprofen. She had smoked two packs of cigarettes daily for 20 years but stopped 10 years ago. Her temperature is 38.1°C (100.6°F), pulse is 94/min, respirations are 18/min, and blood pressure is 132/86 mm Hg. The lungs are clear to auscultation. There are multiple skin lesions with a blue livid center, pale intermediate zone, and a dark red peripheral rim on the upper and lower extremities. Laboratory studies show: Hemoglobin 14.6 g/dL Leukocyte count 11,100/mm3 Serum Na+ 137 mEq/L K+ 4.1 mEq/L Cl- 99 mEq/L Urea nitrogen 17 mg/dL Glucose 123 mg/dL Creatinine 0.9 mg/dL An x-ray of the chest is shown. Which of the following is the most likely causal organism?\""
}
```

```json
{
  "id": "medmcqa_train_156677",
  "source": "medmcqa",
  "split": "train",
  "suspicious_reasons": [
    "composite_answer"
  ],
  "answer": "D",
  "answer_text": "All of the above",
  "question": "The fetus (which is paly foreign to the mother) is not rejected by mother due to"
}
```

```json
{
  "id": "medqa_train_009035",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "C",
  "answer_text": "Vitamin C deficiency",
  "question": "A 6-year-old boy presents with bleeding gums. His past medical history reveals a recent supracondylar fracture of the right humerus as the result of a fall while playing. On physical examination, petechiae are seen all over the patient’s body. The patient’s tongue is shown in the image. Which of the following is the most likely cause of this patient’s condition?"
}
```

```json
{
  "id": "medqa_train_002500",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "C",
  "answer_text": "Medium-chain acyl-CoA dehydrogenase deficiency",
  "question": "A 2-year-old girl is brought to the emergency room by her parents for seizure-like activity earlier today. Her mother describes that she was napping when both of her arms began to twitch and she started foaming at the mouth. She was unresponsive during this time and the episode lasted a total of 30 seconds. The mother denies any fever, pain, recent trauma, changes in feeding, or gastrointestinal changes in her daughter. She states her daughter has recently been lethargic and is currently receiving antibiotics for an ear infection. The patient was born vaginally at home via a midwife without any complications. A physical examination is unremarkable. Results of her laboratory studies are shown below. Hemoglobin: 13 g/dL Hematocrit: 38% Leukocyte count: 7,600/mm^3 with normal differential Platelet count: 170,000/mm^3 Serum: Na+: 136 mEq/L Cl-: 101 mEq/L K+: 3.9 mEq/L HCO3-: 20 mEq/L BUN: 25 mg/dL Glucose: 34 mmol/L Creatinine: 0.8 mg/dL Thyroid-stimulating hormone: 3.2 µU/mL Ca2+: 9.3 mg/dL AST: 183 U/L ALT: 220 U/L What is the most likely explanation for this patient’s symptoms?"
}
```

```json
{
  "id": "medqa_train_009383",
  "source": "medqa",
  "split": "train",
  "suspicious_reasons": [
    "image_dependent"
  ],
  "answer": "B",
  "answer_text": "Actinic keratosis",
  "question": "A 68-year-old man comes to the physician 3 months after noticing skin changes on his scalp. When he scrapes off the crust of the lesion, it reappears after a few days. Occasionally, his scalp itches or he notices a burning sensation. He had a mole removed on his right forearm 5 years ago. He is a retired winemaker. His vital signs are within normal limits. Examination shows multiple rough patches on his scalp. A photograph is shown. Which of the following is the most likely diagnosis?"
}
```

## 是否建议用 clean 文件进入 SFT

- PASS：建议 clean_core 用于高质量 CoT SFT，clean_plus_short_fact 用于扩量 SFT；suspicious 暂不参与训练。

## 使用建议

- `clean_core`：高质量 CoT 训练优先使用，排除短事实题、缺图题、脏输入、组合答案、外部标准题等。
- `clean_plus_short_fact`：在 `clean_core` 基础上加入纯短事实题，适合数据量不足时扩量 SFT。
- `suspicious`：只保留存在非短事实高风险原因的样本，建议暂不进入训练。
