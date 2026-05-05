# ECHO — Early Care Handoff Observer

**Clinical Decision Support for Postpartum Screening**
**Team Female:** Luba Kaper · Paula · Jonel
**Program:** Pursuit AI-Native Cycle 3 | **Version:** 2.1 | **Demo Day:** May 2026

---

## What ECHO Does

A Certified Nurse Midwife (CNM) enters 8 patient parameters. ECHO dispatches 5 subagents in parallel, synthesizes their findings, and renders a one-page patient-specific postpartum screening checklist in the browser — in under 30 seconds.

ECHO is a **provider-facing clinical decision support layer**. It is not a diagnostic engine, not an EHR, and not a patient-facing tool. It surfaces federal data, clinical guidelines, SDOH risk, and hospital commitment status in a single, source-cited view at the point of care.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python 3.11+, FastAPI |
| AI | Anthropic Claude (`claude-sonnet-4-20250514`) |
| Data | CMS CSVs, NCHS NVSS, KFF, static JSON |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/jonel-richardson/echo.git
cd echo
```

### 2. Set up environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_key_here
ECHO_ENV=demo
```

Do not commit this file. It is listed in `.gitignore`.

### 4. Run the backend

```bash
uvicorn backend.main:app --reload
```

### 5. Open the frontend

Open `frontend/index.html` in your browser.

### 6. Run tests

```bash
pytest tests/
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| POST | `/generate-checklist` | Accepts PatientProfile JSON, returns ChecklistOutput JSON |
| GET | `/health` | Returns `{"status": "ok"}` — Demo Day connectivity check |

---

## Patient Input Fields (PatientProfile)

1. Age
2. Race / Ethnicity
3. Payer (Medicaid / Private / Other)
4. State
5. Hospital Name
6. Weeks Postpartum
7. Complications Flagged (multi-select)
8. Primary Language

---

## Demo Scenarios

| Scenario | Description |
|---|---|
| Maya | 28, Black, Medicaid, NY, 6 weeks postpartum |
| Janet | 41, White, private insurance, TX, 4 weeks postpartum, hypertensive |

---

## Clinical Disclaimer

ECHO is clinical decision support, not a diagnostic engine. All items are for clinical review only. Action language reflects screening guidance — not a diagnosis or treatment recommendation. Source citations are provided for every item. CNM clinical judgment governs all care decisions.

---

## Team

| Name | Role |
|---|---|
| Jonel | Backend architecture, Orchestrator (N2), Subagents N3/N6/N7, FastAPI entry point |
| Luba | Schemas, Subagents N4/N5, Fallback (N9), Risk Synthesist (N8), Scorer (N10) |
| Paula | Output Generator (N11), Frontend (N1 + N13) |
