# Teacher Input 候选数据统计

- seed：`42`
- max_samples：`-1`
- train 候选目标数量：13000
- dev 候选目标数量：0
- 目标 A 档最小占比：75.00%
- train 实际输出数量：13000
- dev 实际输出数量：0
- train A 档占比：55.72%
- dev A 档占比：0.00%
- 是否达到目标数量：是

## 原始输入样本数

- `medmcqa_train.jsonl`：182822
- `medqa_train.jsonl`：10178
- `medmcqa_dev.jsonl`：4183
- `medqa_dev.jsonl`：1272

## 清洗后候选池样本数

- `medmcqa_train`：110796
- `medqa_train`：8978
- `medmcqa_dev`：3233
- `medqa_dev`：1127

## 输出 source 分布

- `medmcqa`：9100
- `medqa`：3900

## 输出 split 分布

- `train`：13000

## answer 分布

- `A`：3514
- `B`：3469
- `C`：3114
- `D`：2903

## explanation_quality 分布

- `high`：8981
- `none`：3900
- `medium`：77
- `low`：42

## quality_tier 分布

- `A`：7244
- `B`：5756

## question_type 分布

- `clinical_vignette`：7244
- `short_fact`：5756

## quality_tier/source 分布

- `B/medmcqa`：5756
- `A/medqa`：3900
- `A/medmcqa`：3344

## 文本质量标记

- dirty_text 数量：0
- option_duplicate 过滤数量：688
- duplicate_question 过滤数量：20501

## filter reason 数量

- `tier_c_ambiguous_true_except`：23456
- `duplicate_question`：20501
- `tier_c_too_short_for_teacher`：16038
- `tier_c_source_noise`：4395
- `tier_c_composite_answer`：4276
- `short_question`：3959
- `tier_c_image_dependent`：2131
- `tier_c_exam_artifact`：1045
- `tier_c_dirty_text`：1039
- `option_duplicate`：688
- `empty_option_A`：43
- `empty_option_B`：43
- `empty_option_C`：42
- `empty_option_D`：30

## MedMCQA subject Top 20

- `Medicine`：1624
- `Pathology`：1232
- `Surgery`：1149
- `Pediatrics`：669
- `Gynaecology & Obstetrics`：648
- `Anatomy`：589
- `Microbiology`：483
- `Pharmacology`：434
- `Psychiatry`：316
- `Unknown`：286
- `Dental`：254
- `ENT`：210
- `Ophthalmology`：208
- `Radiology`：180
- `Orthopaedics`：168
- `Biochemistry`：158
- `Skin`：144
- `Anaesthesia`：134
- `Physiology`：87
- `Social & Preventive Medicine`：68

## 前 10 条 teacher input 预览

```json
{
  "id": "medmcqa_train_125729",
  "source": "medmcqa",
  "split": "train",
  "question": "A 50-year-old man is brought to the emergency department by ambulance. His respirations are shallow and infrequent, his pupils are constricted, and he is stuporous. He was noted to have suffered a grandmal seizure in the ambulance. Which of the following drugs is this man likely to have overdosed on?",
  "answer": "C",
  "answer_text": "Meperidine",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 5,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 543,
    "explanation_quality": "high",
    "question_len": 301,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 5,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medqa_train_002946",
  "source": "medqa",
  "split": "train",
  "question": "A 28-year-old woman, gravida 1, para 0, at 10 weeks' gestation comes to the physician for her initial prenatal visit. She has no history of serious illness, but reports that she is allergic to penicillin. Vital signs are within normal limits. The lungs are clear to auscultation, and cardiac examination shows no abnormalities. Transvaginal ultrasonography shows an intrauterine pregnancy with no abnormalities. The fetal heart rate is 174/min. Routine prenatal laboratory tests are drawn. Rapid plasma reagin (RPR) test is 1:128 and fluorescent treponemal antibody absorption test (FTA-ABS) is positive. Which of the following is the most appropriate next step in management?",
  "answer": "C",
  "answer_text": "Administer penicillin desensitization dose",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 676,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 6,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medqa_train_004150",
  "source": "medqa",
  "split": "train",
  "question": "A 59-year-old female presents to your office with complaints of progressive numbness and tingling in her fingers and toes over the last several months. She also reports \"feeling weak\" in her arms and legs. The patient's past medical history is significant for hypertension and Crohn's disease, which has been well-controlled since undergoing an ileocolectomy 7 years ago. Physical examination is significant for the following findings: decreased sensation to light touch, temperature, and vibration in the bilateral lower extremities; ataxia; positive Romberg sign. Deficiency of which of the following is most likely responsible for this patient's symptoms?",
  "answer": "D",
  "answer_text": "Vitamin B12",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 658,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 6,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medmcqa_train_169461",
  "source": "medmcqa",
  "split": "train",
  "question": "Nine days following splenectomy, a 13-year- old patient presents with fever and leukocytosis. The chest x-ray shows free air under the diaphragm. What is the most likely diagnosis?",
  "answer": "D",
  "answer_text": "Left colon perforation",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 5,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 367,
    "explanation_quality": "high",
    "question_len": 180,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "B",
    "question_type": "short_fact",
    "clinical_score": 5,
    "tier_reasons": [
      "short_fact"
    ]
  }
}
```

```json
{
  "id": "medqa_train_008927",
  "source": "medqa",
  "split": "train",
  "question": "A 5-year-old child presents with lower-extremity edema for the past 4 days. Three weeks ago, he experienced several days of cough and fever that was treated with acetaminophen. His medical history is unremarkable; he was born after an uneventful term pregnancy. His vaccinations are up to date. At presentation, his blood pressure is 81/42 mm Hg, and heart rate is 111/min. The child is playful and in no acute distress. Physical examination is remarkable only for ocular 'puffiness' and lower-extremity edema. Chest auscultation is clear, and there are no abnormalities during abdominal inspection. A urinalysis shows the presence of proteinuria, but there is no hematuria. What is the most appropriate treatment for this patient?",
  "answer": "A",
  "answer_text": "Oral prednisone",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 731,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 7,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medmcqa_train_093024",
  "source": "medmcqa",
  "split": "train",
  "question": "A 35-year-old woman, on hemodialysis for chronic renal disease, complains of pain in the hands. On examination, the joints are normal with no inflammation or tenderness on palpation. Lab values reveal a low calcium, high phosphate, and high PTH level. What is the most likely diagnosis?",
  "answer": "C",
  "answer_text": "secondary hyperparathyroidism",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 5,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 536,
    "explanation_quality": "high",
    "question_len": 286,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 5,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medqa_train_007276",
  "source": "medqa",
  "split": "train",
  "question": "A 70-year-old man comes to the physician because of episodes of watery stools for the past 6 weeks. During this period, he has also had recurrent episodes of reddening of the face, neck, and chest that last up to 30 minutes, especially following alcohol consumption. He has hypertension. He smoked one pack of cigarettes daily for 20 years but quit 8 years ago. He drinks two glasses of wine daily. Current medications include enalapril. He appears pale. He is 185 cm (6 ft 1 in) tall and weighs 67 kg (147.7 lb); BMI is 19.6 kg/m2. His temperature is 36.7°C (98°F), pulse is 85/min, and blood pressure is 130/85 mm Hg. Scattered expiratory wheezing is heard throughout both lung fields. Cardiac examination shows no abnormalities. The abdomen is soft and mildly tender. The remainder of the physical examination shows no abnormalities. A complete blood count and serum concentrations of urea nitrogen and creatinine are within the reference range. Which of the following is the most likely diagnosis in this patient?",
  "answer": "D",
  "answer_text": "Carcinoid syndrome",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1017,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 6,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medqa_train_002136",
  "source": "medqa",
  "split": "train",
  "question": "A 16-year-old boy comes to the physician with a 4-day history of sore throat and mild fever. He is on the varsity soccer team at his high school, but has been unable to go to practice for the last few days because he has been very tired and is easily exhausted. He has no history of serious illness and takes no medications. His mother has type 2 diabetes mellitus. He appears weak and lethargic. His temperature is 38.7°C (101.7°F), pulse is 84/min, and blood pressure is 116/78 mm Hg. Examination shows enlarged, erythematous, and exudative tonsils; posterior cervical lymphadenopathy is present. Abdominal examination shows no abnormalities. His hemoglobin concentration is 14.5 g/dL and leukocyte count is 11,200/mm3 with 48% lymphocytes. A heterophile antibody test is positive. In addition to supportive therapy, which of the following is the most appropriate next step in management?",
  "answer": "A",
  "answer_text": "Write a medical note that excuses from soccer events",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 890,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 7,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```

```json
{
  "id": "medmcqa_train_004148",
  "source": "medmcqa",
  "split": "train",
  "question": "A child presents with pigmentation of one half of the face along with a history of multiple episodes of seizures. His X ray skull revealed the following finding. What could be the underlying diagnosis?",
  "answer": "D",
  "answer_text": "Sturge Weber syndrome",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 3,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 343,
    "explanation_quality": "high",
    "question_len": 201,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "B",
    "question_type": "short_fact",
    "clinical_score": 3,
    "tier_reasons": [
      "short_fact"
    ]
  }
}
```

```json
{
  "id": "medmcqa_train_106986",
  "source": "medmcqa",
  "split": "train",
  "question": "A 60-year-old man with diabetes mellitus complains of deep burning pain and sensitivity to touch over his hands and fingers. Nerve conduction studies show slow transmission of impulses and diminished muscle stretch reflexes in ankles and knees. Sensations to vibrations and light touch are also markedly diminished. The development of polyneuropathy in this patient correlates best with which of the following conditions?",
  "answer": "B",
  "answer_text": "Hyperglycemia",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 5,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 478,
    "explanation_quality": "high",
    "question_len": 421,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "A",
    "question_type": "clinical_vignette",
    "clinical_score": 5,
    "tier_reasons": [
      "clinical_vignette"
    ]
  }
}
```
