# SFT Clean 10k Sample50 Audit v2_11k

## Summary

- source file: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_public.jsonl`
- sample public file: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_sample50_public.jsonl`
- sample with metadata: `data/sft/v2_11k/medical_cot_sft_train.clean_10k_sample50_with_meta.jsonl`
- sample size: 50
- seed: `20260606`
- sampling: stratified by `(source, quality_tier)` with largest-remainder allocation

## Sample Distribution

### Source / Tier

- `medqa/A`: 19
- `medmcqa/A`: 16
- `medmcqa/B`: 15

### Source

- `medmcqa`: 31
- `medqa`: 19

### Quality Tier

- `A`: 35
- `B`: 15

### Answer

- `C`: 15
- `B`: 14
- `D`: 11
- `A`: 10

### Step Count

- `5`: 32
- `3`: 15
- `6`: 3

## Hard Audit

- `missing_think`: 0
- `missing_answer_tag`: 0
- `answer_mismatch`: 0
- `bad_a_step_count`: 0
- `bad_b_step_count`: 0
- `source_noise`: 0
- `visual_dependency`: 0
- `internal_trace_in_output`: 0
- `public_has_clinical_score`: 0
- `public_has_cot_source`: 0
- `public_has_expected_step_range`: 0
- `public_has_quality_tier`: 0
- `public_has_question_type`: 0

## Rows For Review

| # | source_index | id | source | tier | answer | answer_text | steps | question preview |
|---:|---:|---|---|---|---|---|---:|---|
| 1 | 157 | `medqa_train_005220` | medqa | A | B | Increased pulmonary capillary permeability | 5 | Question: A 60-year-old man comes to the emergency department because of a 3-day history of fever and shortness of breath. He has a history of COPD treated with inhaled albuterol. ... |
| 2 | 898 | `medmcqa_train_166366` | medmcqa | A | D | Medulloblastoma | 5 | Question: A 5 year old child is admitted with headache, vomitting and diffifculty in walking. Physical findings include truncal ataxia, papilloedema and left lateral recuts palsy. ... |
| 3 | 1206 | `medmcqa_train_115641` | medmcqa | A | D | There is no evidence for meningitis | 5 | Question: A 22 year old male military recruit complains of a headache and stiff neck. He is examined, blood is drawn, and a lumbar puncture performed. The glucose in the CSF is 100... |
| 4 | 1218 | `medmcqa_train_033523` | medmcqa | A | C | Phrenic nerve | 5 | Question: A 35-year-old woman with a history of cholecystectomy arrives in the emergency room with intractable hiccups most likely caused by an abdominal abscess secondary to surgi... |
| 5 | 1577 | `medqa_train_003903` | medqa | A | D | Normal saline and intravenous calcitonin therapy | 6 | Question: A 35-year-old man is brought to the emergency department because of a 2-week history of abdominal cramps, vomiting, and constipation. He also reports having to urinate fr... |
| 6 | 1592 | `medmcqa_train_059259` | medmcqa | A | C | Wolff-Parkinson-White syndrome | 5 | Question: A 4-year-old girl is brought to the pediatrician's office. Her father reports that she suddenly became pale and stopped running while he had been playfully chasing her an... |
| 7 | 1751 | `medqa_train_004139` | medqa | A | C | Urethra | 5 | Question: A 43-year-old man comes to the physician for a follow-up examination. Four months ago, he was treated conservatively for ureteric colic. He has noticed during micturition... |
| 8 | 1858 | `medqa_train_008942` | medqa | A | A | Subepithelial immune complex deposition | 6 | Question: A 7-year-old girl is brought to the physician because of generalized fatigue and dark urine for 1 week. Four weeks ago, she was treated with topical mupirocin for a skin ... |
| 9 | 1969 | `medqa_train_003752` | medqa | A | C | Intravesical Bacille Calmette-Guérin (BCG) | 5 | Question: A 75-year-old man presents to the physician because of bloody urine, which has occurred several times over the past month. He has no dysuria or flank pain. He has no hist... |
| 10 | 2041 | `medqa_train_010035` | medqa | A | A | Decrease in arterial compliance | 5 | Question: An otherwise healthy 65-year-old man comes to the physician for a follow-up visit for elevated blood pressure. Three weeks ago, his blood pressure was 160/80 mmHg. Subseq... |
| 11 | 2125 | `medqa_train_004932` | medqa | A | B | Surgical exploration of the scrotum | 5 | Question: A 13-year-old boy is brought to the emergency department by his mother because of vomiting and severe testicular pain for 3 hours. The boy has had 4–5 episodes of vomitin... |
| 12 | 2152 | `medmcqa_train_054500` | medmcqa | A | A | Varicocele | 5 | Question: A 54-year-old male is admitted to the hospital with severe back pain. Radiographic examination reveals carcinoma of the left kidney blocking the drainage of the testicula... |
| 13 | 2483 | `medmcqa_train_126688` | medmcqa | B | B | 6.50% | 3 | Question: The threshold of hemoglobin A1c for Diagnosis of Ove diabetes in Pregnancy?  Options: A. 6% B. 6.50% C. 7% D. 7.50% |
| 14 | 2590 | `medqa_train_001095` | medqa | A | B | Colonoscopy | 5 | Question: A 72-year-old man presents to his primary care physician complaining of increasing difficulty sleeping over the last 3 months. He reports waking up frequently during the ... |
| 15 | 2637 | `medqa_train_001530` | medqa | A | B | Neutrophilic infiltration of the pericardium | 5 | Question: A 51-year-old woman comes to the physician because of a 3-day history of worsening shortness of breath, nonproductive cough, and sharp substernal chest pain. The chest pa... |
| 16 | 3006 | `medqa_train_003751` | medqa | A | A | Assess the patient's pain medication history | 5 | Question: A 67-year-old man comes to the clinic for establishment of care. He recently retired and moved to Florida with his wife. His past medical history includes hypertension, d... |
| 17 | 3254 | `medmcqa_train_159914` | medmcqa | A | D | Spinal motor nerves | 5 | Question: An 18 year old male comes to the university clinic suppoed by his roommates because he cannot walk. He describes a rapidly evolving weakness affecting his legs and feet s... |
| 18 | 3458 | `medmcqa_train_088587` | medmcqa | B | C | Red degeneration of Fibroid | 3 | Question: A pregnant woman with fibroid uterus develops acute pain in abdomen with low grade fever and mild leucocytosis at 28 weeks. The most likely diagnosis is?  Options: A. Pre... |
| 19 | 3833 | `medmcqa_train_165816` | medmcqa | B | A | EDTA | 3 | Question: A child is brought with drowsiness, decreased deep tendon reflexes and seizures. On examination, the child has a line on gums. There is a history of constipation. Which w... |
| 20 | 4018 | `medmcqa_train_066411` | medmcqa | B | B | Villous adenoma | 3 | Question: A 63-year-old man undergoes a screening colonoscopy and is found to have a polyp in his sigmoid colon. Which type of polyp is most associated with malignancy?  Options: A... |
| 21 | 4106 | `medmcqa_train_166992` | medmcqa | B | C | Treat the patient with clarithromycin, ethambutol and rifabutin | 3 | Question: A patient with AIDS and a CD4 cell count of 100/ml, has a persistent fever and a weight loss associated with invasive pulmonary disease due to M avium complex. Optimal ma... |
| 22 | 4167 | `medmcqa_train_144809` | medmcqa | A | D | Helicobacter pylori | 5 | Question: A patient with a burning epigastric pain is admitted to the hospital, and a gastric biopsy is performed. The tissue is cultured on chocolate agar incubated in a microaero... |
| 23 | 4352 | `medmcqa_train_044100` | medmcqa | B | A | Penicillin | 3 | Question: Red cells are caught as innocent bystanders in the reaction between drug and antibodies against that drug, and develops hemolysis. Which drug is responsible for such a re... |
| 24 | 4496 | `medqa_train_002911` | medqa | A | A | Increased pressure in the distal esophageal vein due to increased pressure in the left gastric vein | 5 | Question: A 54-year-old man presents to the emergency department after vomiting blood an hour ago. He says this happens to him occasionally but denies feeling pain in these episode... |
| 25 | 4497 | `medmcqa_train_054030` | medmcqa | B | C | Delayed carotid upstroke | 3 | Question: A 68-year old man who has had a recent syncopal Episode is hospitalized with congestive hea failure failure. His blood pressure is 160/80 mm Hg. His pulse rate is 80 Beat... |
| 26 | 4523 | `medmcqa_train_088737` | medmcqa | B | A | Corticosteroids | 3 | Question: A 26-yr girl at 31 weeks gestation C/O a 4-week H/O a pustular eruption that developed initially on the periumbilical skin. Subsequently the eruption spread to involve th... |
| 27 | 4753 | `medqa_train_001235` | medqa | A | B | Microthrombi within glomerular vessels on kidney biopsy | 5 | Question: An 8-year-old boy is brought to the pediatric emergency department by his parents with a complaint of abdominal pain and diarrhea for the past week. He states that for th... |
| 28 | 5073 | `medqa_train_004803` | medqa | A | D | Renal cell carcinoma | 5 | Question: An obese 63-year-old man comes to the physician because of 3 episodes of red urine over the past week. He has also had recurrent headaches and intermittent blurry vision ... |
| 29 | 5150 | `medmcqa_train_175442` | medmcqa | A | A | Positive hepatitis B surface antigen | 5 | Question: A 21-year-old medical student suffered a needle stick injury. The patient has a history of illicit intravenous drugs abuse. One month later, the medical student develops ... |
| 30 | 5309 | `medmcqa_train_038226` | medmcqa | B | C | Bronchiectasis | 3 | Question: A patient presents with haemoptysis, copious sputum and 'tram lines' (abnormal air bronchogram) pattern on the chest X-ray. What is the most likely diagnosis?  Options: A... |
| 31 | 5515 | `medmcqa_train_027430` | medmcqa | B | B | Colposcopy and LEEP | 3 | Question: 40 year old woman presents with abnormal cervical cytology on PAP smear suggestive of CIN III (HSIL). The next best step in management is  Options: A. Hysterectomy B. Col... |
| 32 | 5713 | `medmcqa_train_178640` | medmcqa | B | D | Tetracycline | 3 | Question: The drug of choice for chempprophylaxis in contacts of a patient of penumonic plague is  Options: A. Penicillin B. Rifampicin C. Erythromycin D. Tetracycline |
| 33 | 6029 | `medmcqa_train_101906` | medmcqa | A | B | Use of a cane for ambulating, restriction of knee-bending activities, and implementation of muscle-strengthening exercises | 5 | Question: A 70-year-old man has had a long-term "bowlegged" condition but recently his right knee has become warm, swollen, and tender. He reports no recent trauma and gets no reli... |
| 34 | 6121 | `medmcqa_train_018891` | medmcqa | B | C | hemarthrosis | 3 | Question: A 9-year-old boy presents to the clinic for evaluation of easy bruising. Investigations confirm the diagnosis of hemophilia A. Which of the following is the most common p... |
| 35 | 6262 | `medmcqa_train_175479` | medmcqa | B | B | Right fasciculus gracilis | 3 | Question: A 54 year old man is evaluated by a neurologist because of a gait disorder. When the physician passively moves the patient's right great toe upward or downward, the patie... |
| 36 | 6702 | `medqa_train_004935` | medqa | A | C | Enterococcus | 5 | Question: A 75-year-old man presents to his primary care provider with malaise and low-grade fever after he underwent a cystoscopy for recurrent cystitis and pyelonephritis two wee... |
| 37 | 6827 | `medqa_train_008647` | medqa | A | D | Gender | 5 | Question: A 70-year-old caucasian woman presents to her primary care provider complaining of a heavy cough with blood-tinged sputum. Her cough has bothered her for the last 2 weeks... |
| 38 | 7450 | `medmcqa_train_042368` | medmcqa | B | C | Pityriasis rubra pilaris | 3 | Question: A child was brought to OPD with red follicular hyperkeratotic papules over knee.These are areas of normal skin in between.The child also has thickening of palms & soles.T... |
| 39 | 7599 | `medmcqa_train_069008` | medmcqa | A | B | HOCM | 5 | Question: A 22-year-old woman with no past medical history is found to have a systolic ejection murmur on routine physical examination. She has no symptoms and feels well. The murm... |
| 40 | 7656 | `medmcqa_train_006298` | medmcqa | A | B | Nucleus pulposus | 5 | Question: \|A 65-year-old male complains of severe back pain and inability to move his left lower limb. Radiographic studies demonstrate the compression of nerve elements at the int... |
| 41 | 7889 | `medmcqa_train_002166` | medmcqa | A | C | Omission | 5 | Question: A 6 year old female patient complains of pain due to a decayed lower right 2nd molar. During the treatment, patient becomes uncooperative and throws a tantrum. The dentis... |
| 42 | 8086 | `medmcqa_train_051237` | medmcqa | B | C | Epiglottitis | 3 | Question: A 4-year-old child presents to the emergency department with respiratory difficulty and noisy breathing. On examination, X-ray shows thumb sign. The most probable diagnos... |
| 43 | 8468 | `medmcqa_train_125135` | medmcqa | A | C | Ethanol | 5 | Question: A 56-year-old man has experienced increased fatigue and decreased exercise tolerance for the past 2 years. On physical examination, his temperature is 37deg C, pulse is 7... |
| 44 | 8907 | `medqa_train_002964` | medqa | A | A | Ampicillin and gentamicin | 5 | Question: A 48-hour-old newborn presents in respiratory distress. He is gasping for breath in the neonatal intensive care unit (NICU) and has had a fever for the past 2 days with a... |
| 45 | 8925 | `medqa_train_001370` | medqa | A | B | Urethral hypermobility | 6 | Question: A 72-year-old multiparous woman comes to the physician for the evaluation of episodes of involuntary urine leakage for the past 6 months. She loses small amounts of urine... |
| 46 | 8951 | `medmcqa_train_074690` | medmcqa | A | C | Thyroglossal duct cyst | 5 | Question: A 5-year-old boy is taken to his pediatrician for a laceration on his right knee. A mass on his neck is noticed; his mother states it has been there for several months an... |
| 47 | 9138 | `medqa_train_007967` | medqa | A | D | Pulmonary hypoplasia | 5 | Question: A 38-year-old woman, gravida 2, para 1, at 32 weeks' gestation comes to the physician for a prenatal visit. Pregnancy and delivery of her first child were uncomplicated. ... |
| 48 | 9460 | `medmcqa_train_163890` | medmcqa | A | D | Myotonic dystrophy | 5 | Question: A 40-year-old man presents with muscle weakness. He cannot open his hand for a handshake and cannot extend his arm after flexing it. On physical examination, he has marke... |
| 49 | 9770 | `medqa_train_003362` | medqa | A | D | Increased LDL and decreased HDL | 5 | Question: A 24-year-old woman presents to the emergency department with abdominal pain that started while she was at the gym. The patient competes as a power lifter and states that... |
| 50 | 9874 | `medmcqa_train_135608` | medmcqa | A | B | Add antifungal therapy | 5 | Question: A patient of acute leukemia is admitted with febrile neutropenia. On day four of being treated with broad-spectrum antibiotics, his fever increases. X-ray chest shows bil... |
