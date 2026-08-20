# Malaria Screening System — Interface Contract
### (Team Reference Document — সবাই এটা মেনে চলবে)

এই document-টা তিনজনের কাজের মধ্যে "সেতু" হিসেবে কাজ করবে। প্রত্যেকে নিজের module এই exact input/output format মেনে বানাবে, যাতে পরে integration করার সময় কোনো mismatch না হয়। **এই contract বদলাতে হলে তিনজন একসাথে বসে decide করবে, একা কেউ পরিবর্তন করবে না।**

---

## 1. Overall Data Flow

```
User uploads whole smear image
        │
        ▼
┌──────────────────────┐
│  MEMBER 1 MODULE      │   segment_smear(image)
│  RBC Segmentation      │──────────────────────────►  list[CellDetection]
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│  MEMBER 2 MODULE      │   predict_rbc(cell_image)
│  CNN Classification    │──────────────────────────►  PredictionResult
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│  MEMBER 3 MODULE      │   aggregate + visualize + API
│  Backend/Web           │
└──────────────────────┘
        │
        ▼
   Final JSON response → Frontend
```

---

## 2. Member 1 → Member 3 Contract (Segmentation Module)

### Function Signature

```python
def segment_smear(image: np.ndarray) -> list[dict]:
    """
    Input:
        image: np.ndarray, shape (H, W, 3), dtype=uint8, RGB format
               (পুরো blood smear image, raw upload)

    Output:
        একটা list, যেখানে প্রতিটা element একটা detected RBC represent করে।
    """
```

### Output Format (প্রতিটা cell-এর জন্য)

```python
{
    "cell_id": 1,                     # int, unique ID (1, 2, 3, ...)
    "image": <np.ndarray>,            # cropped cell image, shape (h, w, 3), RGB, uint8
    "bbox": [x, y, width, height],    # int list, original image-এর coordinate অনুযায়ী
    "center": [cx, cy]                # int list, cell-এর কেন্দ্রবিন্দু (optional কিন্তু recommended)
}
```

### সম্পূর্ণ Example Output

```python
[
    {
        "cell_id": 1,
        "image": rbc_crop_1,          # numpy array, e.g. shape (180, 180, 3)
        "bbox": [340, 120, 180, 180],
        "center": [430, 210]
    },
    {
        "cell_id": 2,
        "image": rbc_crop_2,
        "bbox": [560, 340, 175, 170],
        "center": [647, 425]
    }
    # ... N cells
]
```

### নিয়ম যা Member 1 কে মানতে হবে

| নিয়ম | বিস্তারিত |
|---|---|
| Crop-এর ভিতর শুধু ১টা cell থাকবে | একাধিক cell একটা crop-এ থাকলে classification ভুল হবে |
| bbox অবশ্যই original image-এর coordinate system-এ | Member 3 এটা দিয়ে annotation আঁকবে, তাই relative/normalized করা যাবে না |
| WBC বাদ দিতে হবে | শুধু RBC পাঠানো, WBC classifier-এর কাজ না |
| Empty list return করা যাবে | যদি কোনো cell detect না হয়, `[]` return করবে (crash না করে) |
| Output সবসময় RGB format-এ | BGR (OpenCV default) হলে Member 3-এর সাথে মিলবে না, নিশ্চিত করে RGB-তে convert করে দিতে হবে |

---

## 3. Member 2 → Member 3 Contract (Classification Module)

### Function Signature

```python
def predict_rbc(cell_image: np.ndarray) -> dict:
    """
    Input:
        cell_image: np.ndarray, shape (h, w, 3), dtype=uint8, RGB format
                    (Member 1 থেকে আসা single cropped RBC)
                    NOTE: এই function-এর ভিতরেই resize + normalize করা হবে,
                    Member 3-কে আলাদা করে preprocessing করতে হবে না।

    Output:
        একটা dict, prediction result সহ।
    """
```

### Output Format

```python
{
    "class": "Parasitized",                 # str, শুধু "Parasitized" বা "Uninfected"
    "parasitized_probability": 0.94,        # float, 0.0 - 1.0
    "uninfected_probability": 0.06          # float, 0.0 - 1.0 (দুটো যোগফল = 1.0)
}
```

### Model Metadata (Member 2 এটা document করে দেবে, কোড না — শুধু তথ্য)

Member 2 কে নিচের তথ্যগুলো একটা `model_info.md` বা comment হিসেবে Member 3-কে জানাতে হবে:

```yaml
model_file: malaria_resnet50.keras
framework: TensorFlow/Keras 2.x
input_size: [224, 224]          # model কোন resolution-এ train হয়েছে
normalization: pixel / 255.0    # exact normalization scheme
class_label_order:
  0: "Parasitized"
  1: "Uninfected"
preprocessing_required_before_predict:
  - resize to 224x224
  - convert to float32
  - normalize (pixel / 255.0)
  # এই preprocessing ইচ্ছা করলে predict_rbc() ফাংশনের ভিতরেই করে ফেলা better,
  # যাতে Member 3-কে আলাদা করে ভুল করার সুযোগ না থাকে
```

### নিয়ম যা Member 2 কে মানতে হবে

| নিয়ম | বিস্তারিত |
|---|---|
| `predict_rbc()` স্বনির্ভর হবে | ভিতরে resize/normalize সব নিজে করবে, raw cropped image নিলেই চলবে |
| Model একবারই load হবে | Function call হওয়ার সময় বারবার model load না করে, module import হওয়ার সময় একবার load করে রাখা (global variable/class) |
| Class label ভুল হলে পুরো system ভুল result দেবে | তাই label mapping (0/1 কোনটা কী) লিখিতভাবে confirm করে দেওয়া must |
| Probability sum ≈ 1.0 | Softmax output হলে এটা এমনিতেই ঠিক থাকবে |

---

## 4. Member 3 → Frontend Contract (Final API Response)

### Endpoint

```
POST /predict
Content-Type: multipart/form-data
Body: image file
```

### Response JSON Format

```json
{
    "status": "success",
    "total_cells": 127,
    "parasitized_cells": 14,
    "uninfected_cells": 113,
    "parasitized_percentage": 11.02,
    "overall_prediction": "Parasitized",
    "annotated_image_url": "/results/annotated_smear_001.jpg",
    "cell_results": [
        {
            "cell_id": 1,
            "class": "Uninfected",
            "confidence": 0.97,
            "bbox": [340, 120, 180, 180]
        },
        {
            "cell_id": 2,
            "class": "Parasitized",
            "confidence": 0.94,
            "bbox": [560, 340, 175, 170]
        }
    ]
}
```

### Error Response Format

```json
{
    "status": "error",
    "error_code": "INVALID_FILE",
    "message": "Please upload a valid JPG/PNG image."
}
```

সম্ভাব্য `error_code` গুলো:
- `INVALID_FILE` — ভুল file type/corrupt image
- `NO_CELLS_DETECTED` — segmentation কোনো cell খুঁজে পায়নি
- `PROCESSING_FAILED` — pipeline-এর মধ্যে কোথাও exception হয়েছে
- `FILE_TOO_LARGE` — size limit ছাড়িয়ে গেছে

---

## 5. Module Folder Structure (কে কোথায় নিজের কোড রাখবে)

```
backend/
├── main.py                    # Member 3 — FastAPI app entry point
├── routes/
│   └── prediction.py          # Member 3
├── services/
│   ├── segmentation.py        # Member 1 → এখানে segment_smear() থাকবে
│   ├── classification.py      # Member 2 → এখানে predict_rbc() থাকবে
│   ├── aggregation.py         # Member 3
│   └── visualization.py       # Member 3
├── models/
│   └── malaria_resnet50.keras # Member 2 এখানে trained model রাখবে
└── requirements.txt
```

**নিয়ম:** Member 1 আর Member 2 শুধু তাদের নিজের file-এ (`segmentation.py`, `classification.py`) কাজ করবে, function signature অক্ষুণ্ণ রেখে। ভিতরের implementation যেভাবে খুশি বদলাতে পারবে, কিন্তু function-এর নাম, input, output format বদলানো যাবে না বিনা আলোচনায়।

---

## 6. Development Strategy — Dummy Module দিয়ে শুরু করা

Member 2 আর Member 1-এর কাজ শেষ হওয়ার জন্য Member 3-কে বসে থাকতে হবে না। শুরুতেই dummy version বানিয়ে রাখা:

```python
# services/segmentation.py (dummy, প্রথম সপ্তাহে ব্যবহার করার জন্য)
def segment_smear(image):
    return [
        {"cell_id": 1, "image": image, "bbox": [0, 0, 100, 100], "center": [50, 50]},
        {"cell_id": 2, "image": image, "bbox": [100, 100, 100, 100], "center": [150, 150]},
    ]
```

```python
# services/classification.py (dummy, প্রথম সপ্তাহে ব্যবহার করার জন্য)
import random

def predict_rbc(cell_image):
    p = random.random()
    return {
        "class": "Parasitized" if p > 0.5 else "Uninfected",
        "parasitized_probability": round(p, 2),
        "uninfected_probability": round(1 - p, 2)
    }
```

পরে যখন real module রেডি হবে, শুধু ফাইলের ভিতরের implementation replace করে দিলেই হবে — বাকি backend-এ কোনো পরিবর্তন লাগবে না, কারণ function signature একই আছে।

---

## 7. Checklist — Week 1 এই Confirm করতে হবে

- [ ] তিনজন একসাথে বসে এই document review করেছে
- [ ] Model input size (Member 2) চূড়ান্ত হয়েছে (224×224 না অন্য কিছু)
- [ ] Class label order (0=Parasitized/1=Uninfected) নিশ্চিত হয়েছে
- [ ] Image format (RGB vs BGR) নিয়ে সবাই একমত
- [ ] `cell_id` কীভাবে generate হবে তা নিয়ে একমত (sequential integer)
- [ ] Dummy module দিয়ে end-to-end pipeline একবার test করা হয়েছে
- [ ] GitHub repo তৈরি, branch structure ঠিক করা হয়েছে (`main`, `member1-segmentation`, `member2-model`, `member3-backend`)

---

*এই document-এ কোনো পরিবর্তন লাগলে, PR/commit-এ clearly লিখতে হবে কী বদলানো হলো এবং কেন, যাতে বাকি দুইজন জানতে পারে।*
