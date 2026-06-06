# Teacher Input 候选数据统计

- seed：`42`
- max_samples：`-1`
- train 候选目标数量：200
- dev 候选目标数量：0
- 目标 A 档最小占比：75.00%
- train 实际输出数量：200
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

- `medmcqa_train`：114061
- `medqa_train`：9004
- `medmcqa_dev`：3310
- `medqa_dev`：1129

## 输出 source 分布

- `medmcqa`：140
- `medqa`：60

## 输出 split 分布

- `train`：200

## answer 分布

- `C`：58
- `D`：49
- `B`：47
- `A`：46

## explanation_quality 分布

- `high`：140
- `none`：60

## quality_tier 分布

- `A`：150
- `B`：50

## question_type 分布

- `clinical_vignette`：150
- `short_fact`：50

## quality_tier/source 分布

- `A/medmcqa`：90
- `A/medqa`：60
- `B/medmcqa`：50

## 文本质量标记

- dirty_text 数量：0
- option_duplicate 过滤数量：688
- duplicate_question 过滤数量：20841

## filter reason 数量

- `tier_c_ambiguous_true_except`：23448
- `duplicate_question`：20841
- `tier_c_too_short_for_teacher`：16036
- `tier_c_composite_answer`：4276
- `short_question`：3959
- `tier_c_image_dependent`：2012
- `tier_c_exam_artifact`：1045
- `tier_c_dirty_text`：1035
- `option_duplicate`：688
- `empty_option_A`：43
- `empty_option_B`：43
- `empty_option_C`：42
- `empty_option_D`：30

## MedMCQA subject Top 20

- `Medicine`：56
- `Pathology`：18
- `Gynaecology & Obstetrics`：13
- `Surgery`：10
- `Unknown`：9
- `Anatomy`：8
- `Microbiology`：8
- `Pharmacology`：6
- `Psychiatry`：4
- `Pediatrics`：2
- `Physiology`：2
- `Radiology`：1
- `Anaesthesia`：1
- `Orthopaedics`：1
- `Biochemistry`：1

## 前 10 条 teacher input 预览

```json
{
  "id": "medmcqa_train_014781",
  "source": "medmcqa",
  "split": "train",
  "question": "A 19-year-old G2P1 woman at 9 weeks' gestation presents to the obstetrics and gynaecology clinic for her second prenatal visit. She reports no complaints other than occasional nausea. She had her first child by spontaneous vaginal delivery without complications. She is taking no medications and denies ethanol, tobacco, or current drug use. While she does admit to a history of intravenous drug abuse, she denies using them since the birth of her first child. Over the past several months she has had multiple sexual partners and does not use contraception. On physical examination she is in no acute distress. Lungs are clear to auscultation bilaterally. Her heart has a regular rate and rhythm, with no murmurs, rubs, or gallops. She is informed that she will need the routine prenatal tests, including an HIV test. The physician informs her of the risks and benefits of the HIV test.1What else should the physician inform the patient before performing the test",
  "answer": "A",
  "answer_text": "Despite the potential for fetal infection , she may opt out from the test",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 682,
    "explanation_quality": "high",
    "question_len": 964,
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
  "id": "medmcqa_train_113356",
  "source": "medmcqa",
  "split": "train",
  "question": "A 28-year-old graduate student presents with complaints of headache. She has had multiple episodes of severe headache over the past three years. She describes the headache as a pounding pain behind her eyes and along the lateral aspects of her head. Prior to the headaches, she almost always sees small flashes of bright light that form enlarging patterns, then clear over time. She often feels nauseated during the headache and occasionally vomits. She has tried multiple over-the-counter pain medications with minimal relief. She has no other medical problems and takes no other medications. She denies fever, weakness, or loss of sensation. Her vital signs are normal. Physical examination, including a full neurologic examination, is normal. The patient's headache is interrupted using sumatriptan. This drug acts by activation of which of the following?",
  "answer": "D",
  "answer_text": "Serotonin receptors",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 531,
    "explanation_quality": "high",
    "question_len": 858,
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
  "id": "medqa_train_003388",
  "source": "medqa",
  "split": "train",
  "question": "A 48-year-old woman presented to the hospital with a headache, intermittent fevers and chills, generalized arthralgias, excessive thirst, increased fluid intake, and a progressive rash that developed on her back. Three days before seeking evaluation at the hospital, she noticed a small, slightly raised lesion appearing like a spider or insect bite on her back, which she considered to be a scab covering the affected region. The patient's fever reached 39.4°C (102.9°F) 2 days before coming to the hospital, with an intensifying burning sensation on the affected site. When a family member examined the bite, it was noticed that the bump had transformed into a circular rash. The patient took over-the-counter ibuprofen for intense pain so she could sleep through the night. The day before her hospital visit, the patient felt exhausted but managed to complete a normal workday. On the day of the hospital visit, she awoke feeling very ill, with shooting joint pains, high fevers, and excessive thirst, which led to her to seek medical attention. On physical examination, her temperature was 40.1°C (104.2°F), and there was a large circular red rash with a bulls-eye appearance (17 × 19 cm in diameter) on her back. The rest of the physical examination was unremarkable. Her past medical and surgical histories were not significant apart from a history of anaphylaxis when taking a tetracycline. She recalled a walk in the woods 3 weeks before this exam but denied finding a tick or any other ectoparasite on her body. She denied any nutritional or inhalational allergies, although she emphasized that she is allergic to tetracyclines. Based on her symptoms, medical history, and physical examination findings, the attending physician decides to institute antimicrobial therapy immediately. Which antimicrobial drug did the physician prescribe?",
  "answer": "B",
  "answer_text": "Amoxicillin",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1846,
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
  "id": "medmcqa_train_103274",
  "source": "medmcqa",
  "split": "train",
  "question": "A 24-year-old African American woman presents with mild dyspnea on exertion, fever, and a rash on her legs. Her symptoms have come on gradually and she reports no pleuritic chest pain, hemoptysis or sputum production. She has no significant past medical history, smokes 10 cigarettes/day and is not taking any medications. Physical examination reveals generalized lymphadenopathy and tender erythematous nodules on her legs. CXR shows bilateral symmetric hilar adenopathy and reticulonodular changes in both lungs. She has a restrictive lung disease pattern on pulmonary function testing. Which of the following is the most likely diagnosis?",
  "answer": "D",
  "answer_text": "sarcoidosis",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 228,
    "explanation_quality": "high",
    "question_len": 641,
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
  "id": "medmcqa_train_036423",
  "source": "medmcqa",
  "split": "train",
  "question": "A 38-year-old pregnant woman is admitted to the emergency department with severe vaginal bleeding. Ultrasound examination confirms the initial diagnosis of ectopic pregnancy. Which of the following is the most common site of an ectopic pregnancy?",
  "answer": "A",
  "answer_text": "Uterine tubes",
  "quality_tier": "B",
  "question_type": "short_fact",
  "clinical_score": 7,
  "expected_step_range": "2-3",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 344,
    "explanation_quality": "high",
    "question_len": 246,
    "option_duplicate": false,
    "dirty_text": false,
    "quality_tier": "B",
    "question_type": "short_fact",
    "clinical_score": 7,
    "tier_reasons": [
      "short_fact"
    ]
  }
}
```

```json
{
  "id": "medmcqa_train_159870",
  "source": "medmcqa",
  "split": "train",
  "question": "A 30-year-old man presents with coughing up blood and sputum. There is no associated dyspnea, fever, or pleuritic chest pain. His past medical history is significant for recurrent pneumonias and a chronic cough productive of foul-smelling purulent sputum. The sputum production is usually worse when lying down and in the morning. He quit smoking 5 years ago and started when he was 18 years old. On physical examination, he appears chronically ill with clubbing of the fingers. Wet inspiratory crackles are heard at the lung bases posteriorly. CXR shows scaring in the right lower lobe, which on chest CT scan is identified as airway dilatation, bronchial wall thickening, and grapelike cysts. Which of the following is the most likely diagnosis?",
  "answer": "A",
  "answer_text": "bronchiectasis",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 321,
    "explanation_quality": "high",
    "question_len": 747,
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
  "id": "medqa_train_002883",
  "source": "medqa",
  "split": "train",
  "question": "A 50-year-old man is brought to the emergency department because of a 3-day history of left flank pain. The patient has had two episodes of urolithiasis during the last year. He initially had pain with urination that improved with oxycodone. Over the past day, the pain has worsened and he has additionally developed fever and chills. He has hypertension and type 2 diabetes mellitus. He has smoked one pack of cigarettes daily for 20 years. He does not drink alcohol. His current medications include metformin and lisinopril. The patient appears ill and uncomfortable. His temperature is 39.1°C (102.3°F), pulse is 108/min, respirations are 22/min, and blood pressure is 90/62 mm Hg. The lungs are clear to auscultation. Cardiac examination shows no murmurs, rubs, or gallops. Examination of the back shows left costovertebral angle tenderness. Physical and neurologic examinations show no other abnormalities. Laboratory studies show: Hemoglobin 14.2 g/dL Leukocyte count 13,900/mm3 Hemoglobin A1c 8.2% Serum Na+ 138 mEq/L K+ 3.8 mEq/L Cl- 98 mEq/L Calcium 9.3 mg/dL Glucose 190 mg/dL Creatinine 2.1 mg/dL Urine pH 8.3 Urine microscopy Bacteria moderate RBC 6–10/hpf WBC 10–15/hpf WBC casts numerous Ultrasound shows enlargement of the left kidney with a dilated pelvis and echogenic debris. CT scan shows a 16-mm stone at the left ureteropelvic junction, dilation of the collecting system, thickening of the wall of the renal pelvis, and signs of perirenal inflammation. Intravenous fluid resuscitation and intravenous ampicillin, gentamicin, and morphine are begun. Which of the following is the most appropriate next step in the management of this patient?\"",
  "answer": "A",
  "answer_text": "Percutaneous nephrostomy",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1662,
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
  "id": "medqa_train_004081",
  "source": "medqa",
  "split": "train",
  "question": "A 45-year-old woman presents to her physician with a four-month history of headache. Her headache is nonfocal but persistent throughout the day without any obvious trigger. She was told that it was a migraine but has never responded to sumatriptan, oxygen, or antiemetics. She takes amlodipine for hypertension. She does not smoke. She denies any recent weight loss or constitutional symptoms. Her temperature is 98°F (36.7°C), blood pressure is 180/100 mmHg, pulse is 70/min, and respirations are 15/min. She is obese with posterior cervical fat pads and central abdominal girth. Her neurological exam is unremarkable. In her initial laboratory workup, her fasting blood glucose level is 200 mg/dL. The following additional lab work is obtained and is as follows: Serum: Na+: 142 mEq/L Cl-: 102 mEq/L K+: 4.1 mEq/L HCO3-: 24 mEq/L BUN: 20 mg/dL Glucose: 135 mg/dL Creatinine: 1.3 mg/dL Ca2+: 10.0 mg/dL AST: 8 U/L ALT: 8 U/L 24-hour urinary cortisol: 500 µg (reference range < 300 µg) Serum cortisol: 25 µg/mL (reference range 5-23 µg/dL) 24-hour low dose dexamethasone suppression test: Not responsive High dose dexamethasone suppression test: Responsive Adrenocorticotropin-releasing hormone (ACTH): 20 pg/mL (5-15 pg/mL) Imaging reveals a 0.5 cm calcified pulmonary nodule in the right middle lobe that has been present for 5 years but an otherwise unremarkable pituitary gland, mediastinum, and adrenal glands. What is the best next step in management?",
  "answer": "B",
  "answer_text": "Inferior petrosal sinus sampling",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1457,
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
  "id": "medmcqa_train_157487",
  "source": "medmcqa",
  "split": "train",
  "question": "A 25 year old nulliparous woman at 35 weeks' gestation comes to the labor and delivery ward complaining of contractions, a headache, and flashes of light in front of her eyes. Her pregnancy has been uncomplicated except for an episode of first trimester bleeding that completely resolved. She has no medical problems. Her temperature is 37 C (98.6 F), blood pressure is 160/110 mm Hg, pulse is 88/minute, and respirations are 12/minute. Examination shows that her cervix is 2 centimeters dilated and 75% effaced, and that she is contracting every 2 minutes. The fetal hea tracing is in the 140s and reactive. Urinalysis shows 3+ proteinuria. Laboratory values are as follows: leukocytes 9,400/mm3, hematocrit 35%, platelets 101,000/mm3. Aspaate aminotransferase (AST) is 200 U/L, and ALT 300 U/L. Which of the following is the most appropriate next step in management?",
  "answer": "D",
  "answer_text": "Sta magnesium sulfate",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 1869,
    "explanation_quality": "high",
    "question_len": 868,
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
