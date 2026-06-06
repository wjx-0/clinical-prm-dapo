# Teacher Input 候选数据统计

- seed：`42`
- max_samples：`-1`
- train 候选目标数量：12000
- dev 候选目标数量：1000
- train 实际输出数量：12000
- dev 实际输出数量：1000
- 是否达到目标数量：是

## 原始输入样本数

- `medmcqa_train.jsonl`：182822
- `medqa_train.jsonl`：10178
- `medmcqa_dev.jsonl`：4183
- `medqa_dev.jsonl`：1272

## 清洗后候选池样本数

- `medmcqa_train`：149540
- `medqa_train`：10173
- `medmcqa_dev`：4055
- `medqa_dev`：1272

## 输出 source 分布

- `medmcqa`：9700
- `medqa`：3300

## 输出 split 分布

- `train`：12000
- `dev`：1000

## answer 分布

- `A`：3622
- `B`：3364
- `C`：3207
- `D`：2807

## explanation_quality 分布

- `high`：9700
- `none`：3300

## 文本质量标记

- dirty_text 数量：0
- option_duplicate 过滤数量：688
- duplicate_question 过滤数量：28974

## filter reason 数量

- `duplicate_question`：28974
- `short_question`：3959
- `option_duplicate`：688
- `empty_option_A`：43
- `empty_option_B`：43
- `empty_option_C`：42
- `empty_option_D`：30

## MedMCQA subject Top 20

- `Medicine`：1016
- `Anatomy`：889
- `Surgery`：872
- `Pathology`：752
- `Pharmacology`：669
- `Gynaecology & Obstetrics`：591
- `Biochemistry`：564
- `Microbiology`：557
- `Social & Preventive Medicine`：547
- `Physiology`：519
- `Pediatrics`：510
- `Dental`：314
- `Ophthalmology`：306
- `ENT`：282
- `Forensic Medicine`：262
- `Psychiatry`：231
- `Radiology`：219
- `Anaesthesia`：192
- `Orthopaedics`：163
- `Unknown`：148

## 前 10 条 teacher input 预览

```json
{
  "id": "medmcqa_train_015833",
  "source": "medmcqa",
  "split": "train",
  "question": "Danbury tremors seen in which chronic poisoning",
  "answer": "C",
  "answer_text": "Mercury",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 407,
    "explanation_quality": "high",
    "question_len": 47,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medqa_train_009554",
  "source": "medqa",
  "split": "train",
  "question": "A 45-year-old woman with a history of alcoholic hepatitis returns to clinic for follow-up after being diagnosed with rheumatoid arthritis and started on NSAIDs. She complains of continued joint effusions and increasing morning stiffness. Given this patient's presentation and history, which of the following drugs presents the greatest risk when started for the management of her condition?",
  "answer": "B",
  "answer_text": "Methotrexate",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 390,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medqa_train_001041",
  "source": "medqa",
  "split": "train",
  "question": "A 59-year-old man with a history of congestive heart failure presents to his cardiologist for a follow-up visit. His past medical history is notable for diabetes mellitus, hypertension, and obesity. He takes metformin, glyburide, aspirin, lisinopril, and metoprolol. He has a 40 pack-year smoking history and drinks alcohol socially. His temperature is 99.1°F (37.2°C), blood pressure is 150/65 mmHg, pulse is 75/min, and respirations are 20/min. Physical examination reveals bilateral rales at the lung bases and 1+ edema in the bilateral legs. The physician decides to start the patient on an additional diuretic but warns the patient about an increased risk of breast enlargement. Which of the following is the most immediate physiologic effect of the medication in question?",
  "answer": "C",
  "answer_text": "Decreased sodium reabsorption in the collecting duct",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 778,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medqa_train_007516",
  "source": "medqa",
  "split": "train",
  "question": "A 62-year-old woman with a history of hypertension, hyperlipidemia, and rheumatoid arthritis presents for evaluation of elevated serum liver chemistries. She has had three months of intense, unremitting itching. Current medications include chlorthalidone, atorvastatin, and ibuprofen. Physical exam is unremarkable. Laboratory studies show aspartate aminotransferase (AST) 42 units/L, alanine aminotransferase (ALT) 39 units/L, alkaline phosphatase 790 units/L, total bilirubin 0.8 mg/dL, and antimitochondrial antibody titer 1:80. What do you expect to see on liver biopsy?",
  "answer": "B",
  "answer_text": "Intrahepatic bile duct destruction",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 574,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medmcqa_train_090564",
  "source": "medmcqa",
  "split": "train",
  "question": "Spasmolytic analgesic is",
  "answer": "A",
  "answer_text": "Dicyclomine",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 495,
    "explanation_quality": "high",
    "question_len": 24,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medqa_train_006087",
  "source": "medqa",
  "split": "train",
  "question": "A 72-year-old man with chronic lymphocytic leukemia (CLL) comes to the physician with a 2-day history of severe fatigue and dyspnea. He regularly visits his primary care physician and has not required any treatment for his underlying disease. His temperature is 36.7°C (98.1°F), pulse is 105/min, respiratory rate is 22/min, and blood pressure is 125/70 mm Hg. The conjunctivae are pale. Examination of the heart and lungs shows no abnormalities. The spleen is palpable 3 cm below the costal margin. No lymphadenopathy is palpated. Laboratory studies show: Hemoglobin 7 g/dL Mean corpuscular volume 105 μm3 Leukocyte count 80,000/mm3 Platelet count 350,000/mm3 Serum Bilirubin Total // Direct 6 mg/dL / 0.8 mg/dL Lactate dehydrogenase 650 U/L (Normal: 45–90 U/L) Based on these findings, this patient’s recent condition is most likely attributable to which of the following?",
  "answer": "A",
  "answer_text": "Autoimmune hemolytic anemia",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 874,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medqa_train_009099",
  "source": "medqa",
  "split": "train",
  "question": "A 5-year-old boy is brought to the physician by his parents for evaluation of easy bruising. He has met all developmental milestones. Vital signs are within normal limits. He is at the 50th percentile for height and weight. Physical examination shows velvety, fragile skin that can be stretched further than normal and multiple ecchymoses. Joint range of motion is increased. A defect in which of the following is the most likely cause of this patient's condition?",
  "answer": "D",
  "answer_text": "Lysine-hydroxylysine cross-linking",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 464,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medmcqa_train_005125",
  "source": "medmcqa",
  "split": "train",
  "question": "An orbital tumor has the following characteristics: Retrobulbar location within the muscle cone, well defined capsule, presents with slowly progressive proptosis, easily resectable, occurs most commonly in the 2\" to 4th decade. The diagnosis is",
  "answer": "D",
  "answer_text": "Cavernous hemangioma",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 2568,
    "explanation_quality": "high",
    "question_len": 244,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medqa_train_008867",
  "source": "medqa",
  "split": "train",
  "question": "An 18-year-old boy presents to the clinic with shortness of breath and fever for the last 2 days. He also has a cough for the same duration. He is asthmatic and uses inhaled albuterol for symptom relief when required. He used albuterol today 3 times at 10-minute intervals but has not had relief of his symptoms. On physical examination, his temperature is 38.3°C (101.0°F), pulse is 130/min, blood pressure is 116/80 mm Hg, and respirations are 28/min. Auscultation of the chest reveals bilateral crackles. Considering that he has already taken inhaled albuterol and has tachycardia, the physician nebulizes him with inhaled ipratropium bromide, which significantly improves his symptoms. Which of the following is the mechanism of action of this drug?",
  "answer": "C",
  "answer_text": "Inhibition of vagally-mediated contraction of bronchial smooth muscles",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 753,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```

```json
{
  "id": "medmcqa_train_166996",
  "source": "medmcqa",
  "split": "train",
  "question": "What is the best time to screen for neonatal hypothyroidism",
  "answer": "B",
  "answer_text": "2 - 4 days after birth",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 169,
    "explanation_quality": "high",
    "question_len": 59,
    "option_duplicate": false,
    "dirty_text": false
  }
}
```
