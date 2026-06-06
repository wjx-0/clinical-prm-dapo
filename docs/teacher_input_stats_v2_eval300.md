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

- `medmcqa_train`：114061
- `medqa_train`：9004
- `medmcqa_dev`：3310
- `medqa_dev`：1129

## 输出 source 分布

- `medmcqa`：210
- `medqa`：90

## 输出 split 分布

- `train`：300

## answer 分布

- `A`：79
- `C`：77
- `B`：73
- `D`：71

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

- `Medicine`：74
- `Pathology`：38
- `Gynaecology & Obstetrics`：17
- `Surgery`：17
- `Microbiology`：10
- `Unknown`：10
- `Pharmacology`：9
- `Anatomy`：9
- `Pediatrics`：7
- `Psychiatry`：5
- `Radiology`：4
- `Physiology`：4
- `Biochemistry`：2
- `Orthopaedics`：2
- `Anaesthesia`：1
- `Ophthalmology`：1

## 前 10 条 teacher input 预览

```json
{
  "id": "medqa_train_008364",
  "source": "medqa",
  "split": "train",
  "question": "A 21-year-old nurse starts to feel ill during his evening shift. Earlier this evening, he started his shift in his normal state of health. Past medical history is significant for multiple admissions to the hospital under strange circumstances. One time he presented to the emergency department complaining of severe abdominal pain and gallstones, though no stones were identified and he was discharged after a full workup. Another time he was admitted for recurrent vomiting episodes and he was discharged after an EGD and several rounds of antiemetics. He has also visited an outpatient clinic for back pain and knee pain, though no findings were ever identified. He takes a multivitamin every day. His mother developed breast cancer at 47 and his father is healthy. Today, his blood pressure is 120/80 mm Hg, heart rate is 105/min, respiratory rate is 17/min, and temperature is 36.9°C (98.4°F). On physical exam, he appears thin and anxious. He is diaphoretic with clammy hands. His heart is tachycardic with an irregular rhythm and his lungs are clear to auscultation bilaterally. A urine toxicology test and EKG are negative. Random blood sugar is 45 mg/dL. The nurse is admitted and treated appropriately. After a thorough review of his medical records, the hospitalist assigned to this patient consults with psychiatry because she is concerned the patient may have factitious disorder. Which of the following would confirm a diagnosis of the factitious disorder in this patient?",
  "answer": "B",
  "answer_text": "Normal c-peptide levels",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1485,
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
  "id": "medmcqa_train_000439",
  "source": "medmcqa",
  "split": "train",
  "question": "A 34-year-old female has a history of intermittent episodes of severe abdominal pain. She has had multiple abdominal surgeries and exploratory procedures with no abnormal findings. Her urine appears dark during an attack and gets even darker if exposed to sunlight. The attacks seem to peak after she takes erythromycin, because of her penicillin allergy. This patient most likely has difficulty in synthesizing which one of the following?",
  "answer": "A",
  "answer_text": "Heme",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 607,
    "explanation_quality": "high",
    "question_len": 439,
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
  "id": "medmcqa_train_174935",
  "source": "medmcqa",
  "split": "train",
  "question": "A 50-year-old obese woman has long-standing type 2 diabetes mellitus inadequately controlled on metformin and pioglitazone. Insulin glargine (15 units subcutaneously at bedtime) has recently been started because of a hemoglobin A1C level of 8.4. Over the weekend, she develops nausea, vomiting, and diarrhea after exposure to family members with a similar illness. Afraid of hypoglycemia, the patient omits the insulin for 3 nights. Over the next 24 hours, she develops lethargy and is brought to the emergency room. On examination, she is afebrile and unresponsive to verbal command. Blood pressure is 84/52. Skin turgor is poor and mucous membranes dry. Neurological examination is nonfocal; she does not have neck rigidity.Laboratory results are as follows:Na: 126 mEq/LK: 4.0 mEq/LCl: 95 mEq/LHCO3: 22 mEq/LGlucose: 1100 mg/dLBUN: 84 mg/dLCreatinine: 3.0 mg/dLWhich of the following is the most likely cause of this patient's coma?",
  "answer": "B",
  "answer_text": "Hyperosmolar nonketotic state",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 1914,
    "explanation_quality": "high",
    "question_len": 935,
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
  "id": "medmcqa_train_035321",
  "source": "medmcqa",
  "split": "train",
  "question": "A 63 year old male with a 75 pack year history of smoking and marked chronic obstructive pulmonary disease (COPD) develops fevers and a persistent cough frequently tinged with blood. Chest x-ray reveals a complex cavitary lesion in the right upper lobe. Bronchoscopic examination identifies a large lung abscess from which pure Fusobacterium nucleatum is cultured. What is the most likely source of the Fusobacterium?",
  "answer": "C",
  "answer_text": "Oral cavity",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 1238,
    "explanation_quality": "high",
    "question_len": 417,
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
  "id": "medqa_train_000626",
  "source": "medqa",
  "split": "train",
  "question": "A 27-year-old man who recently emigrated as a refugee from Somalia presents with fever, weight loss, fatigue, and exertional chest pain. He says his symptoms began 3 weeks ago and that his appetite has decreased and he has lost 3 kg (6.6 lb) in the last 3 weeks. He denies any history of cardiac disease. His past medical history is unremarkable. The patient admits that he has always lived in poor hygienic conditions in overcrowded quarters and in close contact with cats. His vital signs include: blood pressure 120/60 mm Hg, pulse 90/min, and temperature 38.0°C (100.4°F). Physical examination reveals generalized pallor. A cardiac examination reveals an early diastolic murmur loudest at the left third intercostal space. Abdominal examination reveals a tender and mildly enlarged spleen. Prominent axillary lymphadenopathy is noted. Laboratory investigations reveal a WBC count of 14,500/μL with 5% bands and 93% polymorphonuclear cells. An echocardiogram reveals a 5-mm vegetation on the aortic valve with moderate regurgitation. Three sets of blood cultures are taken over 24 hours followed by empiric antibiotic therapy with gentamicin and vancomycin. The blood cultures show no growth after 5 days. Following a week of empiric therapy, the patient continues to deteriorate. Which of the following would most likely confirm the diagnosis in this patient?",
  "answer": "A",
  "answer_text": "Bartonella serology",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1363,
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
  "id": "medmcqa_train_123055",
  "source": "medmcqa",
  "split": "train",
  "question": "Meera is a 43-year-old woman with a body mass index (BMI) of 32. She presented with abnormal uterine bleeding to her gynecologist, who performed an endometrial biopsy that indicated endometrial cancer, specifically endometrial adenocarcinoma of endometrioid histology.Meera's family history is significant for colon cancer. Her mother was diagnosed with colon cancer at age 66. Her paternal aunt was diagnosed with endometrial cancer at age 67. Suspecting hereditary disease which of the following DNA repair mechanism is defective in Meera?",
  "answer": "C",
  "answer_text": "Mismatch repair",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 397,
    "explanation_quality": "high",
    "question_len": 541,
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
  "id": "medmcqa_train_033260",
  "source": "medmcqa",
  "split": "train",
  "question": "A 66-year-old man presents with shoness of breath, myalgia, headache along with multiple episodes of fever with rigors. He went to the local doctor who treated him for the flu. However, his symptoms worsened, and by the day of presentation he was complaining of a dry cough and marked shoness of breath and diarrhoea. Patient is a non-smoker. Auscultation of chest reveals bilateral crackles and bronchial breathing in both lower zones posteriorly. Lab findings, Elevated CRP level Hypocalcemia Acidosis and marked hypoxia Gram staining of sputum revealed small, pleomorphic, faint, gram negative bacilli. Chest X-ray What is the drug of choice of the above organism: -",
  "answer": "A",
  "answer_text": "Azithromycin",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 621,
    "explanation_quality": "high",
    "question_len": 669,
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
  "id": "medmcqa_train_122270",
  "source": "medmcqa",
  "split": "train",
  "question": "A 66-year-old woman with a history of chronic alcohol abuse has had headaches and nausea for the past 4 days. She has become increasingly obtunded. On physical examination, she has right upper quadrant tenderness, tachycardia, tachypnea, and hypotension. Laboratory studies show serum AST of 475 U/L, ALT of 509 U/L, alkaline phosphatase of 23 U/L, total bilirubin of 0.9 mg/dL, albumin of 3.8 g/dL, and total protein of 6.1 g/dL. She is treated with N-acetylcysteine. Which of the following drugs has she most likely ingested in excess?",
  "answer": "A",
  "answer_text": "Acetaminophen",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": true,
    "explanation_len": 572,
    "explanation_quality": "high",
    "question_len": 537,
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
  "id": "medqa_train_007895",
  "source": "medqa",
  "split": "train",
  "question": "A 27-year-old man presents to the emergency department for altered mental status. The patient was found napping in a local market and brought to the hospital. The patient has a past medical history of polysubstance abuse and is homeless. His temperature is 104°F (40.0°C), blood pressure is 100/52 mmHg, pulse is 133/min, respirations are 25/min, and oxygen saturation is 99% on room air. Physical exam is notable for an altered man. Cardiopulmonary exam reveals a murmur over the left lower sternal border. A bedside ultrasound reveals a vegetation on the tricuspid valve. The patient is ultimately started on IV fluids, norepinephrine, vasopressin, vancomycin, and piperacillin-tazobactam. A central line is immediately placed in the internal jugular vein and the femoral vein secondary to poor IV access. Cardiothoracic surgery subsequently intervenes to remove the vegetation. While recovering in the ICU, days 3-5 are notable for an improvement in the patient’s symptoms. Two additional peripheral IVs are placed while in the ICU on day 5, and the femoral line is removed. On day 6, the patient's fever and hemodynamic status worsen. Though he is currently responding and not complaining of any symptoms including headache, photophobia, neck stiffness, or pain, he states he is feeling weak. Jolt accentuation of headache is negative and his abdominal exam is benign. A chest radiograph, urinalysis, and echocardiogram are unremarkable though the patient’s blood cultures are positive when drawn. Which of the following is the best next step in management?",
  "answer": "C",
  "answer_text": "Remove the central line and send for cultures",
  "quality_tier": "A",
  "question_type": "clinical_vignette",
  "clinical_score": 7,
  "expected_step_range": "4-6",
  "input_quality": {
    "has_explanation": false,
    "explanation_len": 0,
    "explanation_quality": "none",
    "question_len": 1561,
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
  "id": "medqa_train_002517",
  "source": "medqa",
  "split": "train",
  "question": "A 33-year-old man is being evaluated for malaise and fatigability. He says that he hasn’t been able to perform at work, can’t exercise like before, and is constantly tired. He also says that his clothes have ‘become larger’ in the past few months. Past medical history is significant for gastroesophageal reflux disease, which is under control with lifestyle changes. His blood pressure is 110/70 mm Hg, the temperature is 37.0°C (98.6°F), the respiratory rate is 17/min, and the pulse is 82/min. On physical examination, an enlarged, painless, mobile, cervical lymph node is palpable. A complete blood count is performed. Hemoglobin 9.0 g/dL Hematocrit 37.7% Leukocyte count 5,500/mm3 Neutrophils 65% Lymphocytes 30% Monocytes 5% Mean corpuscular volume 82.2 μm3 Platelet count 190,000 mm3 Erythrocyte sedimentation rate 35 mm/h C-reactive protein 8 mg/dL A biopsy of the lymph node is performed which reveals both multinucleated and bilobed cells. The patient is started on a regimen of drugs for his condition. Echocardiography is performed before treatment is started and shows normal ejection fraction, ventricle function, and wall motion. After 2 rounds of chemotherapy, another echocardiography is performed by protocol, but this time all heart chambers are enlarged, and the patient is suffering from severe exertion dyspnea. Which of the drugs below is most likely responsible for these side effects?",
  "answer": "A",
  "answer_text": "Adriamycin",
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
