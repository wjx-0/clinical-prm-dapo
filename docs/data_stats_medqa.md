# MedQA 数据处理统计

- 数据集来源：`openlifescienceai/medqa`
- 随机种子：`42`
- max_samples：`-1`
- 原始样本数：12723
- 本次处理样本数：12723
- 过滤后样本数：12723
- 被过滤样本数量：0

## 各 split 样本数

- train：10178
- dev：1272
- test：1273

## 过滤原因

- 无

## 前 3 条样本预览

### 样本 1

```json
{
  "id": "medqa_train_000001",
  "source": "medqa",
  "split": "train",
  "language": "en",
  "question": "A 23-year-old pregnant woman at 22 weeks gestation presents with burning upon urination. She states it started 1 day ago and has been worsening despite drinking more water and taking cranberry extract. She otherwise feels well and is followed by a doctor for her pregnancy. Her temperature is 97.7°F (36.5°C), blood pressure is 122/77 mmHg, pulse is 80/min, respirations are 19/min, and oxygen saturation is 98% on room air. Physical exam is notable for an absence of costovertebral angle tenderness and a gravid uterus. Which of the following is the best treatment for this patient?",
  "options": {
    "A": "Ampicillin",
    "B": "Ceftriaxone",
    "C": "Doxycycline",
    "D": "Nitrofurantoin"
  },
  "answer": "D",
  "answer_text": "Nitrofurantoin",
  "explanation": "",
  "subject": "",
  "topic": "",
  "choice_type": "single"
}
```

### 样本 2

```json
{
  "id": "medqa_train_000002",
  "source": "medqa",
  "split": "train",
  "language": "en",
  "question": "A 3-month-old baby died suddenly at night while asleep. His mother noticed that he had died only after she awoke in the morning. No cause of death was determined based on the autopsy. Which of the following precautions could have prevented the death of the baby?",
  "options": {
    "A": "Placing the infant in a supine position on a firm mattress while sleeping",
    "B": "Keeping the infant covered and maintaining a high room temperature",
    "C": "Application of a device to maintain the sleeping position",
    "D": "Avoiding pacifier use during sleep"
  },
  "answer": "A",
  "answer_text": "Placing the infant in a supine position on a firm mattress while sleeping",
  "explanation": "",
  "subject": "",
  "topic": "",
  "choice_type": "single"
}
```

### 样本 3

```json
{
  "id": "medqa_train_000003",
  "source": "medqa",
  "split": "train",
  "language": "en",
  "question": "A mother brings her 3-week-old infant to the pediatrician's office because she is concerned about his feeding habits. He was born without complications and has not had any medical problems up until this time. However, for the past 4 days, he has been fussy, is regurgitating all of his feeds, and his vomit is yellow in color. On physical exam, the child's abdomen is minimally distended but no other abnormalities are appreciated. Which of the following embryologic errors could account for this presentation?",
  "options": {
    "A": "Abnormal migration of ventral pancreatic bud",
    "B": "Complete failure of proximal duodenum to recanalize",
    "C": "Abnormal hypertrophy of the pylorus",
    "D": "Failure of lateral body folds to move ventrally and fuse in the midline"
  },
  "answer": "A",
  "answer_text": "Abnormal migration of ventral pancreatic bud",
  "explanation": "",
  "subject": "",
  "topic": "",
  "choice_type": "single"
}
```
