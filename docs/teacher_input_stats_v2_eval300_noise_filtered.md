# Teacher Input 候选数据统计

- seed：`42`
- max_samples：`-1`
- train 候选目标数量：300
- dev 候选目标数量：0
- 目标 A 档最小占比：75.00%
- train 实际输出数量：300
- dev 实际输出数量：0
- train A 档占比：75.00%
- dev A 档占比：0.00%
- 是否达到目标数量：是

## 原始输入样本数

- `medmcqa_train.jsonl`：182822
- `medqa_train.jsonl`：10178
- `medmcqa_dev.jsonl`：4183
- `medqa_dev.jsonl`：1272

## 清洗后候选池样本数

- `medmcqa_train`：111795
- `medqa_train`：8979
- `medmcqa_dev`：3263
- `medqa_dev`：1127

## 输出 source 分布

- `medmcqa`：210
- `medqa`：90

## 输出 split 分布

- `train`：300

## answer 分布

- `A`：85
- `C`：77
- `B`：72
- `D`：66

## explanation_quality 分布

- `high`：210
- `none`：90

## quality_tier 分布

- `A`：225
- `B`：75

## question_type 分布

- `clinical_vignette`：225
- `short_fact`：75

## quality_tier/source 分布

- `A/medmcqa`：135
- `A/medqa`：90
- `B/medmcqa`：75

## 文本质量标记

- dirty_text 数量：0
- option_duplicate 过滤数量：688
- duplicate_question 过滤数量：20568

## filter reason 数量

- `tier_c_ambiguous_true_except`：23453
- `duplicate_question`：20568
- `tier_c_too_short_for_teacher`：16037
- `tier_c_composite_answer`：4276
- `short_question`：3959
- `tier_c_source_noise`：3105
- `tier_c_image_dependent`：2131
- `tier_c_exam_artifact`：1045
- `tier_c_dirty_text`：1039
- `option_duplicate`：688
- `empty_option_A`：43
- `empty_option_B`：43
- `empty_option_C`：42
- `empty_option_D`：30

## MedMCQA subject Top 20

- `Medicine`：76
- `Pathology`：41
- `Gynaecology & Obstetrics`：17
- `Surgery`：16
- `Unknown`：11
- `Anatomy`：9
- `Microbiology`：9
- `Radiology`：7
- `Pediatrics`：5
- `Pharmacology`：5
- `Physiology`：4
- `Psychiatry`：3
- `Biochemistry`：2
- `Orthopaedics`：2
- `Ophthalmology`：2
- `Anaesthesia`：1

## 前 10 条 teacher input 预览

```json
{
  "id": "medmcqa_train_030361",
  "source": "medmcqa",
  "split": "train",
  "question": "A 40 year old male with history of alcohol abuse for 20 years is brought to the hospital emergency with complaints of fearfulness, talking to self, aggressive behavior, tremulousness and saying that there insects crawling under his skin. Physical examination shows tachycardia, palpitations, sweating, and high grade fever. He is unable to recognize few of his family members. There is history of drinking alcohol two days prior to the onset of the present complaints. He is most likely suffering from?",
  "answer": "A",
  "answer_text": "Delirium tremens",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 1173,
    "explanation_quality": "high",
    "question_len": 502,
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
  "id": "medqa_train_009359",
  "source": "medqa",
  "split": "train",
  "question": "A 72-year-old woman presents to her primary care provider complaining of fatigue for the last 6 months. She can barely complete her morning chores before having to take a long break in her chair. She rarely climbs the stairs to the second floor of her house anymore because it is too tiring. Past medical history is significant for Hashimoto's thyroiditis, hypertension, and hyperlipidemia. She takes levothyroxine, chlorthalidone, and atorvastatin. Her daughter developed systemic lupus erythematosus. She is retired and lives by herself in an old house build in 1945 and does not smoke and only occasionally drinks alcohol. She eats a well-balanced diet with oatmeal in the morning and some protein such as a hardboiled egg in the afternoon and at dinner. Today, her blood pressure is 135/92 mm Hg, heart rate is 110/min, respiratory rate is 22/min, and temperature is 37.0°C (98.6°F). On physical exam, she appears frail and her conjunctiva are pale. Her heart is tachycardic with a regular rhythm and her lungs are clear to auscultation bilaterally. A complete blood count (CBC) shows that she has macrocytic anemia. Peripheral blood smear shows a decreased red blood cell count, anisocytosis, and poikilocytosis with occasional hypersegmented neutrophils. An endoscopy and colonoscopy are performed to rule out an occult GI bleed. Her colonoscopy was normal. Endoscopy shows thin and smooth gastric mucosa without rugae. Which of the following is the most likely cause of this patient’s condition?",
  "answer": "B",
  "answer_text": "Pernicious anemia",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1502,
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
  "id": "medqa_train_000797",
  "source": "medqa",
  "split": "train",
  "question": "A 35-year-old man presents with acute onset of chest pain, trouble breathing, and abdominal pain. He says he had recently been training for a triathlon competition when, over the past week, he noticed that he was getting more tired than usual. He figured that it was due to his age since most of the people training with him were in their 20s. However, after completing a particularly difficult workout over this last weekend he noticed left-sided chest pain that did not radiate, and abdominal pain, worse on the right side. The pain persisted after he stopped exercising. This morning he noticed red urine. The patient reports similar past episodes of red urine after intense exercise or excessive alcohol intake for the past 5 years, but says it has never been accompanied by pain. Past medical history is significant for a urinary tract infection last week, treated with trimethoprim-sulfamethoxazole. Physical examination is significant for a systolic flow murmur loudest at the right upper sternal border and right upper quadrant tenderness without guarding or rebound. Laboratory findings are significant for the following: Hemoglobin 8.5 g/dL Platelets 133,000/µL Total bilirubin 6.8 mg/dL LDH 740 U/L Haptoglobin 25 mg/dL An abdominal MRI with contrast is performed which reveals hepatic vein thrombosis. Which of the following laboratory tests would most likely to confirm the diagnosis in this patient?",
  "answer": "B",
  "answer_text": "Flow cytometry",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1413,
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
  "id": "medmcqa_train_088319",
  "source": "medmcqa",
  "split": "train",
  "question": "A 65-year-old woman with a history of breast cancer and a recent melanoma presents to the emergency room following a tonic-clonic seizure. Blood chemistry values are within normal limits. There is no history of drug or alcohol use. MRI of the brain shows bilateral cerebral edema and a cystic, frontal lobe lesion. Frozen section obtained from a CT-guided biopsy reveals a hemorrhagic nodule of neoplastic cells. Immunohistochemical stains for which of the following antigens would be most helpful in making your diagnosis definitive for melanoma?",
  "answer": "B",
  "answer_text": "HMB-45",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 693,
    "explanation_quality": "high",
    "question_len": 547,
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
  "id": "medmcqa_train_163127",
  "source": "medmcqa",
  "split": "train",
  "question": "An 8 year old boy with a history of fall from 10 feet height complains of pain in the right ankle. X-ray taken at that time is normal without any fracture line. But after 2 years, he developed a calcaneovalgus deformity. The diagnosis is",
  "answer": "C",
  "answer_text": "Tibial epiphyseal injury",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 6,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 1030,
    "explanation_quality": "high",
    "question_len": 237,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "B",
    "question_type": "short_fact",
    "clinical_score": 6,
    "tier_reasons": [
      "short_fact"
    ]
  }
}
```

```json
{
  "id": "medqa_train_003950",
  "source": "medqa",
  "split": "train",
  "question": "A 48-year-old woman presents to her family practitioner complaining of tremulousness of both hands for the past few years that have deteriorated over the past 7 months. She sometimes spills coffee while holding a full cup. She is a receptionist and her symptoms have led to difficulties with typing at work. She denies weight loss, diarrhea, fatigue, blurring of vision, walking difficulties, and heat intolerance. The past medical history is significant for well-controlled bronchial asthma. She does not smoke or use illicit drugs, but she drinks one cup of coffee daily. She drinks alcohol only socially and has noticed a decrease in her tremors afterward. She reports that her father had a head tremor, and her mother had hyperthyroidism. The patient is oriented to person, place, time and situation. On physical examination, the eye movements are normal and there is no nystagmus. She has a prominent rhythmic tremor of both hands that increase when hands are stretched with abducted fingers. The muscle strength, tone, and deep tendon reflexes are normal in all 4 limbs. The sensory examination and gait are normal. The laboratory test results are as follows: Hemoglobin 14.8 g/dL Leukocytes 5,500/mm3 Platelets 385,000/mm3 BUN 18 mg/dL Creatinine 0.9 mg/dL Na+ 143 mmol/L K+ 4.2 mmol/L Which of the following is the most appropriate management for this patient?",
  "answer": "B",
  "answer_text": "Primidone",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1368,
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
  "id": "medqa_train_002792",
  "source": "medqa",
  "split": "train",
  "question": "A 65-year-old obese woman presents with changes in her left breast. The patient states that, about a month ago, she noticed that she was able to feel a hard mass in the upper outer quadrant of her left breast, which has not gone away. In addition, her nipple and skin overlying the breast have started to look different. Past medical history is significant for the polycystic ovarian syndrome (PCOS) and hypertension, well-managed with lisinopril. The patient has never been pregnant. Menopause was at age 53. Family history is significant for breast cancer in her mother at age 55, and her father who died of lung cancer at age 52. A review of systems is significant for a 13.6 kg (30 lb) weight loss in the last 2 months despite no change in diet or activity. Vitals include: temperature 37.0°C (98.6°F), blood pressure 120/75 mm Hg, pulse 97/min, respiratory rate 16/min, and oxygen saturation 99% on room air. The physical exam is significant for a palpable, hard, fixed mass in the upper outer quadrant of the left breast, as well as nipple retraction and axillary lymphadenopathy. Mammography of the left breast reveals a spiculated mass in the upper outer quadrant. A biopsy confirms invasive ductal carcinoma. Molecular analysis reveals that the tumor cells are positive for a receptor that is associated with a poor prognosis. Which of the following are indicated as part of this patient’s treatment?",
  "answer": "B",
  "answer_text": "Trastuzumab",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1409,
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
  "id": "medmcqa_train_052681",
  "source": "medmcqa",
  "split": "train",
  "question": "A 74-year-old woman presents to the clinic for evaluation of increasing back pain and malaise. The symptoms are insidious in onset and she reports no history of recent trauma to the back. Her past medical history is significant for hypertension and breast cancer which was diagnosed 7 years ago and treated with surgery and adjuvant therapy.On physical examination, the pertinent findings are percussion tenderness over the lower spine. An x-ray of the lumbar spine reveals lytic lesions compatible with metastatic bone disease, and her serum calcium level is elevated. Which of the following mediators is least likely to be involved?",
  "answer": "B",
  "answer_text": "ectopic parathyroid hormone (PTH)",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 369,
    "explanation_quality": "high",
    "question_len": 634,
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
  "id": "medmcqa_train_137145",
  "source": "medmcqa",
  "split": "train",
  "question": "A 45-year-old man with a long history of alcohol intake comes into the emergency room with upper gastrointestinal (UGI) bleeding. Urgent endoscopy reveals the following findings. Which of the following is the most likely diagnosis?",
  "answer": "A",
  "answer_text": "esophageal varices",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 6,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 411,
    "explanation_quality": "high",
    "question_len": 231,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "B",
    "question_type": "short_fact",
    "clinical_score": 6,
    "tier_reasons": [
      "short_fact"
    ]
  }
}
```

```json
{
  "id": "medmcqa_train_040830",
  "source": "medmcqa",
  "split": "train",
  "question": "A 30-year-old woman with a history of intravenous drug abuse is admitted to a hospital for rapidly progressive malaise, fever, and chills. On physical examination, subungual splinter hemorrhages and a systolic murmur are detected. Blood cultures are positive for Staphylococcus aureus. She died of myocardial infarction on her third hospital day. Which of the following was the underlying condition leading to the patient's demise?",
  "answer": "A",
  "answer_text": "Acute infective endocarditis",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 2687,
    "explanation_quality": "high",
    "question_len": 431,
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
