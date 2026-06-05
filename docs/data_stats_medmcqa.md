# MedMCQA 数据处理统计

- 数据集来源：`openlifescienceai/medmcqa`
- 随机种子：`42`
- max_samples：`-1`

## 原始 split 样本数

- train：182822
- test：6150
- validation：4183

## 输出 split 过滤后样本数

- train：182822
- dev：4183
- test：0

## 无答案样本输出数

- train_unlabeled：0
- dev_unlabeled：0
- test_unlabeled：6150

## 过滤原因统计

- 无

## Subject 分布 Top 20

- Medicine：18182
- Surgery：17231
- Pathology：15221
- Anatomy：14794
- Pharmacology：14001
- Social & Preventive Medicine：12011
- Microbiology：11436
- Dental：10256
- Gynaecology & Obstetrics：10237
- Physiology：9001
- Biochemistry：8453
- Pediatrics：8271
- Ophthalmology：6990
- Forensic Medicine：5967
- ENT：4972
- Radiology：4464
- Psychiatry：4458
- Anaesthesia：3206
- Unknown：3047
- Orthopaedics：3019

## 前 3 条样本预览

### 样本 1

```json
{
  "id": "medmcqa_train_000001",
  "source": "medmcqa",
  "split": "train",
  "language": "en",
  "question": "Chronic urethral obstruction due to benign prismatic hyperplasia can lead to the following change in kidney parenchyma",
  "options": {
    "A": "Hyperplasia",
    "B": "Hyperophy",
    "C": "Atrophy",
    "D": "Dyplasia"
  },
  "answer": "C",
  "answer_text": "Atrophy",
  "explanation": "Chronic urethral obstruction because of urinary calculi, prostatic hyperophy, tumors, normal pregnancy, tumors, uterine prolapse or functional disorders cause hydronephrosis which by definition is used to describe dilatation of renal pelvis and calculus associated with progressive atrophy of the kidney due to obstruction to the outflow of urine Refer Robbins 7yh/9,1012,9/e. P950",
  "subject": "Anatomy",
  "topic": "Urinary tract",
  "choice_type": "single",
  "original_choice_type": "single"
}
```

### 样本 2

```json
{
  "id": "medmcqa_train_000002",
  "source": "medmcqa",
  "split": "train",
  "language": "en",
  "question": "Which vitamin is supplied from only animal source:",
  "options": {
    "A": "Vitamin C",
    "B": "Vitamin B7",
    "C": "Vitamin B12",
    "D": "Vitamin D"
  },
  "answer": "C",
  "answer_text": "Vitamin B12",
  "explanation": "Ans. (c) Vitamin B12 Ref: Harrison's 19th ed. P 640* Vitamin B12 (Cobalamin) is synthesized solely by microorganisms.* In humans, the only source for humans is food of animal origin, e.g., meat, fish, and dairy products.* Vegetables, fruits, and other foods of nonanimal origin doesn't contain Vitamin B12 .* Daily requirements of vitamin Bp is about 1-3 pg. Body stores are of the order of 2-3 mg, sufficient for 3-4 years if supplies are completely cut off.",
  "subject": "Biochemistry",
  "topic": "Vitamins and Minerals",
  "choice_type": "single",
  "original_choice_type": "single"
}
```

### 样本 3

```json
{
  "id": "medmcqa_train_000003",
  "source": "medmcqa",
  "split": "train",
  "language": "en",
  "question": "All of the following are surgical options for morbid obesity except -",
  "options": {
    "A": "Adjustable gastric banding",
    "B": "Biliopancreatic diversion",
    "C": "Duodenal Switch",
    "D": "Roux en Y Duodenal By pass"
  },
  "answer": "D",
  "answer_text": "Roux en Y Duodenal By pass",
  "explanation": "Ans. is 'd' i.e., Roux en Y Duodenal Bypass Bariatric surgical procedures include:a. Vertical banded gastroplastyb. Adjustable gastric bandingc. Roux-en Y gastric bypass (Not - Roux-en Y Duodenal Bypass)d. Biliopancreatic diversione. Duodenal switcho The surgical treatment of morbid obesity is known as bariatric surgery.o Morbid obesity is defined as body mass index of 35 kg/m2 or more with obesity related comorbidity, or BMI of 40 kg/m2 or greater without comorbidity.o Bariatric operations produce weight loss as a result of 2 factors. One is restriction of oralintake. The other is malabsorbtion of ingested food.o Gastric restrictive procedures include Vertical banded gastroplasty & Adjustable gastric bandingo Malabsorbtive procedures include Biliopancreatic diversion, and Duodenal switcho Roux-en Y gastric bypass has features of both restriction and malabsorptionBariatric Operations: Mechanism of ActionRestrictiveVertical banded gastroplastyLaparoscopic adjustable gastric bandingLargely Restrictive/Mildly MalabsorptiveRoux-en-Y gastric bypassLargely Malabsorptive/Mildly RestrictiveBiliopancreatic diversionDuodenal switch",
  "subject": "Surgery",
  "topic": "Surgical Treatment Obesity",
  "choice_type": "single",
  "original_choice_type": "multi"
}
```
