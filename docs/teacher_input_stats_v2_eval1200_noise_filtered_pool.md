# Teacher Input 候选数据统计

- seed：`42`
- max_samples：`-1`
- train 候选目标数量：1200
- dev 候选目标数量：0
- 目标 A 档最小占比：75.00%
- train 实际输出数量：1200
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

- `medmcqa_train`：110796
- `medqa_train`：8978
- `medmcqa_dev`：3233
- `medqa_dev`：1127

## 输出 source 分布

- `medmcqa`：840
- `medqa`：360

## 输出 split 分布

- `train`：1200

## answer 分布

- `A`：318
- `C`：307
- `D`：299
- `B`：276

## explanation_quality 分布

- `high`：840
- `none`：360

## quality_tier 分布

- `A`：900
- `B`：300

## question_type 分布

- `clinical_vignette`：900
- `short_fact`：300

## quality_tier/source 分布

- `A/medmcqa`：540
- `A/medqa`：360
- `B/medmcqa`：300

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

- `Medicine`：263
- `Pathology`：203
- `Surgery`：83
- `Anatomy`：49
- `Gynaecology & Obstetrics`：42
- `Unknown`：33
- `Pediatrics`：33
- `Microbiology`：28
- `Pharmacology`：20
- `Orthopaedics`：15
- `Radiology`：13
- `Psychiatry`：13
- `Biochemistry`：13
- `Physiology`：6
- `ENT`：6
- `Ophthalmology`：6
- `Anaesthesia`：6
- `Dental`：5
- `Skin`：2
- `Social & Preventive Medicine`：1

## 前 10 条 teacher input 预览

```json
{
  "id": "medmcqa_train_105314",
  "source": "medmcqa",
  "split": "train",
  "question": "A 44-year-old farmer presented with high-grade fever for 4 days. On examination, an ulcer was found at the right-hand region along with painful cervical lymphadenopathy. History revealed a bite of an animal 4 days ago. A papule was formed which later progressed to form an ulcer. Erythematous, maculopapular rash all over the body along with erythema nodosum on lower limbs were present. Swabs from the ulcer and biopsy from the lymph nodes were taken and sent for examination. Gram staining was done. It showed growth on chocolate agar, BCYE agar and media supplemented with cysteine. What is the drug of choice of the above organism: -",
  "answer": "A",
  "answer_text": "Streptomycin",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 838,
    "explanation_quality": "high",
    "question_len": 637,
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
  "id": "medqa_train_005279",
  "source": "medqa",
  "split": "train",
  "question": "A 57-year-old woman with a long-standing history of liver cirrhosis presents to her primary care provider with a complaint of unintended weight loss of 8.2 kg (18.0 lb) within the last month. She has a history of intermittent right upper quadrant pain in her abdomen with decreased appetite for a few years and occasional shortness of breath. The past medical history is significant for hepatitis E infection during her first pregnancy when she was 28 years old, and a history of blood transfusion after an accident 25 years ago. She drinks about 2–3 pints of beer every week on average and does not use tobacco. The vital signs include: blood pressure 110/68 mm Hg, pulse rate 82/min, respiratory rate 11/min, and temperature 37.7 °C (99.9°F). The physical exam is normal except for moderate icterus and tender hepatomegaly. The blood tests show mild anemia with decreased iron stores. Serum electrolytes, blood sugar, and renal function are normal. The chest X-ray is normal. An ultrasound of the abdomen revealed a mass in the liver, which was confirmed with a biopsy to be hepatocellular carcinoma. Which of the following is the strongest causative factor that can be linked to her diagnosis?",
  "answer": "C",
  "answer_text": "History of blood transfusion",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1196,
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
  "id": "medmcqa_train_182685",
  "source": "medmcqa",
  "split": "train",
  "question": "A 10-year old boy presents to the pediatric emergency unit with seizures. Blood pressure in the upper extremity measured as 200/140 mm Hg. Femoral pulses were not palpable. The most likely diagnosis amongst the following is",
  "answer": "D",
  "answer_text": "Coarctation of aoa",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 5,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 1421,
    "explanation_quality": "high",
    "question_len": 223,
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
  "id": "medmcqa_train_089689",
  "source": "medmcqa",
  "split": "train",
  "question": "A 40-year-old woman presents to the clinic for evaluation of symptoms of light-headedness associated with sweating, palpitations, and hunger. The symptoms are most pronounced whenever she misses a meal.On physical examination, her vital signs are normal, as is the heart, lungs, and abdominal examination. Her past medical history is negative and she is not taking any medications. During one such episode, while in hospital, her blood glucose level was 30 mg/dL and the symptoms resolved with drinking some juice. Which of the following is the most likely diagnosis?",
  "answer": "D",
  "answer_text": "tumor of the pancreatic beta-cells",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 623,
    "explanation_quality": "high",
    "question_len": 567,
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
  "id": "medmcqa_train_179766",
  "source": "medmcqa",
  "split": "train",
  "question": "A 45-year-old man presents to the clinic for evaluation of weakness in his arms and legs. The symptoms started gradually, and are now more noticeable and interfering with his ability to work as an electrician. On physical examination, the cranial nerves are normal, but there is weakness of his left handgrip and right leg quadriceps with loss of muscle bulk. There are obvious fasciculations over the left forearm and right thigh. Tone is increased in the arms and legs and the reflexes are brisk. Which of the following is the most likely diagnosis?",
  "answer": "A",
  "answer_text": "amyotrophic lateral sclerosis (ALS)",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 190,
    "explanation_quality": "high",
    "question_len": 551,
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
  "id": "medmcqa_train_010358",
  "source": "medmcqa",
  "split": "train",
  "question": "A 25-year-old woman presents with symptoms of fatigue and weakness. On examination, there is diplopia, ptosis, weakness, and fatigability of muscles on repeated use. Which of the following is the most likely diagnosis?",
  "answer": "A",
  "answer_text": "myasthenia gravis",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 5,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 275,
    "explanation_quality": "high",
    "question_len": 218,
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
  "id": "medmcqa_train_159605",
  "source": "medmcqa",
  "split": "train",
  "question": "A 43-year-old woman presents with (RUQ) abdominal pain, and vomiting. She has had three children. The white blood cell (WBC) count is 14.3x109/L and liver function tests are normal. To establish the diagnosis in this patient, the test of choice is",
  "answer": "B",
  "answer_text": "Ultrasound",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 5,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 601,
    "explanation_quality": "high",
    "question_len": 247,
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
  "id": "medmcqa_train_147862",
  "source": "medmcqa",
  "split": "train",
  "question": "A 68 year old woman was admitted with a history of weakness for two months. On examination, cervical lymph nodes were found enlarged and spleen was palpable 2 cm below the costal margin. Her hemoglobin was 10.5 g/dl, platelet count 27 x 109/L and total leukocyte count 40 x 109/L, which included 80 % mature lymphoid cells with coarse clumped chromatin. Bone marrow revealed a nodular lymphoid infiltrate. The peripheral blood lymphoid cells were positive for CD19, CD5, CD20 and CD23 and were negative for CD79B and FMC-7. The histopathological examination of the lymph node in this patient will most likely exhibit effacement of lymph node architecture by?",
  "answer": "A",
  "answer_text": "A monomorphic lymphoid proliferation with admixed proliferation centers",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 759,
    "explanation_quality": "high",
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
  "id": "medqa_train_001054",
  "source": "medqa",
  "split": "train",
  "question": "A 71-year-old man comes to the physician because of a 2-week history of fatigue and a cough productive of a blood-tinged phlegm. Over the past month, he has had a 5.0-kg (11-lb) weight loss. He has hypertension and type 2 diabetes mellitus. Eight months ago, he underwent a kidney transplantation. The patient does not smoke. His current medications include lisinopril, insulin, prednisone, and mycophenolate mofetil. His temperature is 38.9°C (102.1°F), pulse is 88/min, and blood pressure is 152/92 mm Hg. Rhonchi are heard at the right lower lobe of the lung on auscultation. There is a small ulceration on the left forearm. An x-ray of the chest shows a right lung mass with lobar consolidation. Antibiotic therapy with levofloxacin is started. Three days later, the patient has a seizure and difficulty coordinating movements with his left hand. An MRI of the brain shows an intraparenchymal lesion with peripheral ring enhancement. Bronchoscopy with bronchoalveolar lavage yields weakly acid-fast, gram-positive bacteria with branching, filamentous shapes. Which of the following is the most appropriate initial pharmacotherapy?",
  "answer": "C",
  "answer_text": "Trimethoprim/sulfamethoxazole",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1134,
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
  "id": "medmcqa_train_108182",
  "source": "medmcqa",
  "split": "train",
  "question": "A 42-year-old woman has had menometrorrhagia for the past 2 months. She has no history of prior irregular menstrual bleeding, and she has not yet reached menopause. On physical examination, there are no vaginal or cervical lesions, and the uterus appears normal in size, but there is a right adnexal mass. An abdominal ultrasound scan shows the presence of a 7-cm solid right adnexal mass. Endometrial biopsy shows hyperplastic endometrium, but no cellular atypia. What is the most likely lesion that underlies her menstrual abnormalities?",
  "answer": "C",
  "answer_text": "Granulosa-theca cell tumor",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 6,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 714,
    "explanation_quality": "high",
    "question_len": 539,
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
