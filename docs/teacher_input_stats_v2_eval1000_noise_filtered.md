# Teacher Input 候选数据统计

- seed：`42`
- max_samples：`-1`
- train 候选目标数量：1000
- dev 候选目标数量：0
- 目标 A 档最小占比：75.00%
- train 实际输出数量：1000
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

- `medmcqa`：700
- `medqa`：300

## 输出 split 分布

- `train`：1000

## answer 分布

- `A`：263
- `C`：262
- `D`：240
- `B`：235

## explanation_quality 分布

- `high`：700
- `none`：300

## quality_tier 分布

- `A`：750
- `B`：250

## question_type 分布

- `clinical_vignette`：750
- `short_fact`：250

## quality_tier/source 分布

- `A/medmcqa`：450
- `A/medqa`：300
- `B/medmcqa`：250

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

- `Medicine`：232
- `Pathology`：156
- `Surgery`：61
- `Anatomy`：38
- `Gynaecology & Obstetrics`：37
- `Unknown`：31
- `Pediatrics`：26
- `Pharmacology`：22
- `Microbiology`：22
- `Psychiatry`：15
- `Radiology`：12
- `Orthopaedics`：9
- `Biochemistry`：9
- `Physiology`：7
- `Anaesthesia`：7
- `Ophthalmology`：6
- `ENT`：6
- `Dental`：2
- `Skin`：2

## 前 10 条 teacher input 预览

```json
{
  "id": "medmcqa_train_042962",
  "source": "medmcqa",
  "split": "train",
  "question": "A 56-year-old woman has had weight loss accompanied by abdominal enlargement for the past 5 months. There is a family history of breast and ovarian carcinoma. On physical examination, there are no lesions of the cervix, and the uterus is normal in size, but there is a left adnexal mass. An abdominal ultrasound scan shows a 10-cm cystic mass in the left adnexal region, with scattered 1-cm peritoneal nodules, and ascites. Cytologic studies of peritoneal fluid show malignant cells. Which of the following mutated genes is most likely a factor in the development of this neoplasm?",
  "answer": "A",
  "answer_text": "BRCA1",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 695,
    "explanation_quality": "high",
    "question_len": 581,
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
  "id": "medqa_train_002863",
  "source": "medqa",
  "split": "train",
  "question": "A 36-year-old woman presents with a whitish vaginal discharge over the last week. She also complains of itching and discomfort around her genitals. She says her symptoms are getting progressively worse. She has been changing her undergarments frequently and changed the brand of detergent she uses to wash her clothes, but it did not resolve her problem. Additionally, she admits to having painful urination and increased urinary frequency for the past one month, which she was told are expected side effects of her medication. The patient denies any recent history of fever or malaise. She has 2 children, both delivered via cesarean section in her late twenties. Past medical history is significant for hypertension and diabetes mellitus type 2. Current medications are atorvastatin, captopril, metformin, and empagliflozin. Her medications were changed one month ago to improve her glycemic control, as her HbA1c at that time was 7.5%. Her vital signs are a blood pressure of 126/84 mm Hg and a pulse of 78/min. Her fingerstick glucose is 108 mg/dL. Pelvic examination reveals erythema and mild edema of the vulva. A thick, white, clumpy vaginal discharge is seen. The vaginal pH is 4.0. Microscopic examination of a KOH-treated sample of the discharge demonstrates lysis of normal cellular elements with branching pseudohyphae. Which of the following is the next best step in the management of this patient?",
  "answer": "D",
  "answer_text": "Start fluconazole.",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1411,
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
  "id": "medmcqa_train_179426",
  "source": "medmcqa",
  "split": "train",
  "question": "20 year old patient presents with hypokalemia, alkalosis with normal blood pressure and no edema. the diagnosis is",
  "answer": "A",
  "answer_text": "Bartter syndrome",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 6,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 211,
    "explanation_quality": "high",
    "question_len": 114,
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
  "id": "medmcqa_train_171978",
  "source": "medmcqa",
  "split": "train",
  "question": "A 35-year-old male with history of 4 weeks of immobilization for fracture femur developed sudden onset of chest pain and hemoptysis. ECG shows SI Q3 T3 pattern. Diagnosis?",
  "answer": "C",
  "answer_text": "Pulmonary embolism",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 6,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 485,
    "explanation_quality": "high",
    "question_len": 171,
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
  "id": "medmcqa_train_063833",
  "source": "medmcqa",
  "split": "train",
  "question": "A 57 year old woman presents to her family physician complaining of numbness and tingling in her right thumb, index and long finger for the past four weeks. She repos that she wakes up in the middle of the night with these symptoms and needs to shake her hands to \"wake\" them up. She denies numbness or tingling in her other hand or either leg. She has no neck or upper arm pain. On physical examination, her symptoms are reproduced by Tinel testing. Her symptoms are also exacerbated by hyperflexion of the wrist. There is decreased sensation over the palmar aspects of the thumb, index and middle fingers. There is no apparent motor weakness. Which of the following is the most likely diagnosis?",
  "answer": "B",
  "answer_text": "Carpal tunnel syndrome",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 949,
    "explanation_quality": "high",
    "question_len": 697,
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
  "id": "medqa_train_007309",
  "source": "medqa",
  "split": "train",
  "question": "A 57-year-old woman is brought to the emergency department by her husband with complaints of sudden-onset slurring for the past hour. She is also having difficulty holding things with her right hand. She denies fever, head trauma, diplopia, vertigo, walking difficulties, nausea, and vomiting. Past medical history is significant for type 2 diabetes mellitus, hypertension, and hypercholesterolemia for which she takes a baby aspirin, metformin, ramipril, and simvastatin. She has a 23-pack-year cigarette smoking history. Her blood pressure is 148/96 mm Hg, the heart rate is 84/min, and the temperature is 37.1°C (98.8°F). On physical examination, extraocular movements are intact. The patient is dysarthric, but her higher mental functions are intact. There is a right-sided facial weakness with preserved forehead wrinkling. Her gag reflex is weak. Muscle strength is mildly reduced in the right hand. She has difficulty performing skilled movements with her right hand, especially writing, and has difficulty touching far objects with her index finger. She is able to walk without difficulty. Pinprick and proprioception sensation is intact. A head CT scan is within normal limits. What is the most likely diagnosis?",
  "answer": "A",
  "answer_text": "Dysarthria-clumsy hand syndrome",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1221,
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
  "id": "medmcqa_train_175343",
  "source": "medmcqa",
  "split": "train",
  "question": "A 53-year-old woman with ovarian tumor presents with breathlessness and right-sided chest pain. The chest X-ray shows obliteration of the right costophrenic angle. Diagnosis?",
  "answer": "A",
  "answer_text": "Pleurisy",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 6,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 242,
    "explanation_quality": "high",
    "question_len": 174,
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
  "id": "medqa_train_000120",
  "source": "medqa",
  "split": "train",
  "question": "A 74-year-old female is brought to the emergency department because of a 2-week history of increasing weakness and chills. She also notes difficulty breathing for the last three days. Eight weeks ago, she underwent left hemicolectomy for adenocarcinoma of the colon. She subsequently developed a severe urinary tract infection, was treated in the intensive care unit for four days, and was discharged from the hospital three weeks ago. She has type 2 diabetes mellitus, osteoporosis with lumbar pain, hypertension, and atrial fibrillation. She has smoked one pack of cigarettes daily for 50 years. She does not drink alcohol and has never used illicit drugs. Current medications include warfarin, metformin, lisinopril, and aspirin. She appears lethargic and has a large conjunctival hemorrhage in her left eye. Her temperature is 39.3°C (102.7°F), pulse is 112/min, respirations are 25/min, and blood pressure is 126/79 mm Hg. Cardiac auscultation reveals a new holosystolic murmur over the apex. Abdominal examination shows mild, diffuse tenderness throughout the upper quadrants and a well-healed 12-cm paramedian scar. There are multiple tender nodules on the palmar surface of her fingertips. Funduscopic examination shows retinal hemorrhages with pale centers. An ECG shows atrial fibrillation and right bundle branch block. Which of the following is the most likely underlying etiology of this patient's condition?",
  "answer": "D",
  "answer_text": "Enterococcus faecalis infection",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1421,
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
  "id": "medqa_train_002942",
  "source": "medqa",
  "split": "train",
  "question": "A 73-year-old woman presents to the emergency department with diffuse abdominal pain, nausea, and vomiting. Her daughter who accompanies her says she was in her usual state of health until two days ago when she started to complain of abdominal pain and was unable to tolerate oral intake. She has hypertension, congestive heart failure, atrial fibrillation, and osteoarthritis. She underwent an exploratory laparotomy for an ovarian mass a year ago where a mucinous cystadenoma was excised. Her medications include aspirin, nifedipine, lisinopril, metoprolol, warfarin, and Tylenol as needed for pain. She does not drink alcohol or smoke cigarettes. She appears ill and disoriented. Her temperature is 37.9°C (100.3°F), blood pressure is 102/60 mm Hg, pulse is 110/min and irregular, and respirations are 16/min. Examination shows diffuse tenderness to palpation of the abdomen. The abdomen is tympanitic on percussion. Bowel sounds are hyperactive. The lungs are clear to auscultation bilaterally. There is a soft crescendo-decrescendo murmur best auscultated in the right second intercostal space. Laboratory studies show: Hemoglobin 10.2 g/dL Leukocyte count 14,000/mm3 Platelet count 130,000/mm3 Prothrombin time 38 seconds INR 3.2 Serum Na+ 132 mEq/dL K+ 3.6 mEq/dL Cl- 102 mEq/dL HCO3- 19 mEq/dL Urea nitrogen 36 mg/dl Creatinine 2.3 mg/dL Lactate 2.8 mEq/dL (N= 0.5-2.2 mEq/dL) An x-ray of the abdomen shows multiple centrally located dilated loops of gas filled bowel. There is no free air under the diaphragm. A nasogastric tube is inserted and IV fluids and empiric antibiotic therapy are started. Emergent exploratory laparotomy is planned. Which of the following is the next best step in management?\"",
  "answer": "B",
  "answer_text": "Administer fresh frozen plasma and Vitamin K",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1712,
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
  "id": "medqa_train_002667",
  "source": "medqa",
  "split": "train",
  "question": "A 53-year-old man is brought to the clinic by his son for the evaluation of unusual behavior. He is a shopkeeper by profession and sometimes behaves very rudely to the customers. Recently, he accused one of the customers of using black magic over his shop. He has been increasingly irritable, forgetting things, and having problems managing his finances over the past 8 months. He is also having difficulty finding words and recalling the names of objects during the conversation. There is no history of recent head trauma, fever, hallucinations, or abnormal limb movements. Past medical history is significant for a well-controlled type 2 diabetes mellitus. Family history is unremarkable. He does not smoke or use illicit drugs. Vital signs are stable with a blood pressure of 134/76 mm Hg, a heart rate of 88/min, and a temperature of 37.0°C (98.6°F). On physical examination, he has problems naming objects and planning tasks. Mini-mental state examination (MMSE) score is 26/30. Cranial nerve examination is normal. Muscle strength is normal in all 4 limbs with normal muscle tone and deep tendon reflexes. Sensory examination is also normal. What is the most likely diagnosis?",
  "answer": "D",
  "answer_text": "Pick’s disease",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1182,
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
