# DocBrief - AI-Assisted Clinical Evidence Synthesis

A clinical decision support application that helps physicians surface relevant evidence-based guidelines instantly. The doctor enters patient symptoms, lab values, and medical history — DocBrief retrieves the most relevant clinical guidelines from its knowledge base and synthesizes an evidence-backed clinical assessment using LLM.

**Stack:** React · TypeScript · FastAPI · Groq (Llama 3) · ChromaDB · sentence-transformers · Python

---

## What It Does

Doctors spend an average of 16 hours per week searching for and reviewing medical literature. DocBrief reduces this to seconds by:

1. **Doctor enters** patient symptoms, lab values, age, medical history, and current medications
2. **RAG pipeline retrieves** the most relevant clinical guidelines from a pre-loaded knowledge base using semantic vector search
3. **LLM synthesizes** the retrieved evidence into a structured clinical assessment with inline citations
4. **Doctor receives** a structured synthesis covering clinical considerations, diagnostic criteria, evidence-based treatment options, drug interaction flags, and suggested next steps

---

## Architecture

```
Patient Presentation (React UI)
        │
        ▼
FastAPI Backend
        │
        ├── sentence-transformers (all-MiniLM-L6-v2)
        │   Embeds patient query into vector
        │
        ├── ChromaDB Vector Store
        │   Retrieves top-5 most relevant clinical guidelines
        │
        └── Groq (Llama 3.3 70B)
            Synthesizes retrieved guidelines with patient data
            Returns structured clinical evidence synthesis
```

---

## Knowledge Base

Pre-loaded with 18 clinical guideline entries across 8 medical domains:

| Domain | Guidelines |
|---|---|
| Cardiovascular | ACC/AHA Hypertension 2017, ACC/AHA AFib 2023, ACC/AHA Heart Failure 2022 |
| Cardiovascular Emergency | ACC/AHA STEMI 2022, AHA Chest Pain 2021 |
| Endocrine | ADA Diabetes Standards 2024, ATA Hypothyroidism 2014 |
| Pulmonary/Infectious | IDSA/ATS CAP 2019, IDSA HAP/VAP 2016, GINA Asthma 2024 |
| Infectious Disease | IDSA UTI Guidelines 2024 |
| Critical Care | Surviving Sepsis Campaign 2021 |
| Psychiatry | APA MDD Guidelines 2023 |

---

## Sample Output

**Input:** 65-year-old male, chest pain radiating to left arm, diaphoresis, Troponin 0.8, BP 160/95

**Output includes:**
- Clinical considerations (ACS, PE, aortic dissection differential)
- Diagnostic criteria (ECG within 10 min, serial troponins, STEMI criteria)
- Evidence-based treatment (aspirin 325mg immediately, PCI within 90 min for STEMI)
- Drug interaction flags (ACE inhibitor + ARB contraindication)
- Suggested next steps (cardiology consult, repeat troponin at 3-6 hours)
- Inline citations from ACC/AHA, AHA, and IDSA guidelines

---

## Responsible AI Design

DocBrief is designed as a **clinical reference tool, not a diagnostic system:**
- Every recommendation cites the specific guideline it came from
- Prominent disclaimer on every response: *"All clinical decisions require physician judgment and direct patient evaluation"*
- The LLM is explicitly prompted to surface evidence, not make clinical decisions
- Consistent with how production clinical decision support systems (Epic, Microsoft DAX) are designed and regulated

---

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React 18 + TypeScript |
| Backend | FastAPI (Python) |
| LLM | Groq API — Llama 3.3 70B Versatile |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | ChromaDB (persistent local storage) |
| Markdown Rendering | react-markdown |

---

## Local Setup

**Prerequisites:** Python 3.12+, Node.js 18+, Groq API key (free at console.groq.com)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn groq chromadb sentence-transformers python-dotenv
cp .env.example .env  # Add your GROQ_API_KEY
python -m uvicorn main:app --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

Open **http://localhost:3000**

---

## Project Structure

```
docbrief/
├── backend/
│   ├── main.py          # FastAPI app, RAG pipeline, Groq integration
│   ├── .env.example     # Environment variable template
│   └── .gitignore
├── frontend/
│   └── src/
│       ├── App.tsx      # Main React component
│       └── App.css      # Styling
└── README.md
```
