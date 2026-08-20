# Malaria Screening System

An AI-assisted screening tool that analyzes thin blood-smear images to
detect *Plasmodium*-parasitized red blood cells (RBCs), based on the
transfer-learning approach studied in Rajaraman et al. (2018),
*"Pre-trained convolutional neural networks as feature extractors toward
improved malaria parasite detection in thin blood smear images,"* PeerJ.

> **Disclaimer:** This is a research/academic prototype for AI-assisted
> screening. It is **not** a substitute for professional medical diagnosis.

---

## Architecture

```
User → React Frontend → FastAPI Backend
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
        RBC Segmentation  CNN Classifier  Aggregation
          (Member 1)        (Member 2)     + Visualization
                                              (Member 3)
```

See [`docs/interface_contract.md`](docs/interface_contract.md) for the
exact function signatures and JSON formats each module must follow.

## Team Responsibilities

| Member | Responsibility | Main file(s) |
|---|---|---|
| Member 1 | RBC detection & segmentation | `backend/services/segmentation.py` |
| Member 2 | CNN model training & inference | `backend/services/classification.py`, `backend/models/` |
| Member 3 | Web app, integration, deployment | `backend/`, `frontend/` |

---

## Project Structure

```
malaria-screening-system/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── routes/prediction.py    # POST /predict endpoint
│   ├── services/
│   │   ├── segmentation.py     # Member 1's module
│   │   ├── classification.py   # Member 2's module
│   │   ├── aggregation.py      # Result summary logic
│   │   └── visualization.py    # Annotated image generation
│   ├── models/                 # Trained model files go here (gitignored)
│   ├── results/                # Generated annotated images (gitignored)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # ImageUploader, ResultCard, etc.
│   │   ├── pages/Home.jsx
│   │   └── services/api.js     # Backend API calls
│   └── package.json
├── docs/
│   └── interface_contract.md   # Shared contract between all 3 members
├── .github/workflows/          # CI/CD (auto-deploy frontend)
└── render.yaml                 # Backend deployment config
```

---

## Local Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API runs at `http://localhost:8000`
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`

Currently `segmentation.py` and `classification.py` contain **dummy
implementations** so the full pipeline can be developed and tested
before the real modules are ready. See the comments inside each file.

### Frontend

```bash
cd frontend
cp .env.example .env          # then edit if needed
npm install
npm start
```

- App runs at `http://localhost:3000`
- Make sure `REACT_APP_API_BASE_URL` in `.env` points to your running backend

---

## Deployment

### Backend → Render (free tier)

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint** → connect this repo.
   Render will auto-detect `render.yaml` and configure everything.
3. Once deployed, copy your live backend URL (e.g. `https://malaria-screening-backend.onrender.com`).

### Frontend → GitHub Pages (auto via GitHub Actions)

1. In your GitHub repo: **Settings → Secrets and variables → Actions →
   New repository secret**
   - Name: `REACT_APP_API_BASE_URL`
   - Value: your Render backend URL from above
2. In **Settings → Pages**, set source to **GitHub Actions**.
3. Push to `main` (or edit anything inside `frontend/`) — the workflow
   in `.github/workflows/deploy-frontend.yml` will build and deploy
   automatically.
4. Your site will be live at `https://<username>.github.io/<repo-name>/`.

---

## Integrating the Real Modules

When Member 1's segmentation and Member 2's trained model are ready:

1. Replace the body of `segment_smear()` in `backend/services/segmentation.py`
   — keep the function name and return format unchanged.
2. Replace the body of `predict_rbc()` in `backend/services/classification.py`,
   and load the real trained model in `_load_model()`.
3. Place the trained model file in `backend/models/` (update `requirements.txt`
   to include `tensorflow` or `torch` as needed).
4. Test locally with real smear images before redeploying.

Full contract details: [`docs/interface_contract.md`](docs/interface_contract.md)

---

## Limitations

- Model performance reported in the source paper (Accuracy ~0.96, AUC ~0.99)
  was measured on a specific research dataset; real-world performance can
  vary with different microscopes, staining, and image quality.
- This system is a screening aid, not a diagnostic device.
