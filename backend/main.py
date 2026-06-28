from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="DocBrief API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("medical_knowledge")

# ── MEDICAL KNOWLEDGE BASE ────────────────────────────────────
MEDICAL_KNOWLEDGE = [
    # Hypertension
    {
        "id": "htn_001",
        "text": "Hypertension diagnosis: Blood pressure consistently ≥130/80 mmHg. Stage 1: 130-139/80-89. Stage 2: ≥140/90. Hypertensive crisis: >180/120. First-line treatment includes lifestyle modifications: DASH diet, sodium restriction <2.3g/day, regular aerobic exercise, weight loss.",
        "source": "JNC 8 / ACC/AHA 2017 Guidelines", "category": "Cardiovascular"
    },
    {
        "id": "htn_002",
        "text": "Antihypertensive medications: First-line agents include thiazide diuretics (hydrochlorothiazide 12.5-25mg), ACE inhibitors (lisinopril 10-40mg), ARBs (losartan 50-100mg), calcium channel blockers (amlodipine 5-10mg). ACE inhibitors preferred in diabetes with proteinuria. Avoid ACE inhibitors in pregnancy.",
        "source": "ACC/AHA Hypertension Guidelines 2017", "category": "Cardiovascular"
    },
    # Diabetes
    {
        "id": "dm_001",
        "text": "Type 2 Diabetes diagnosis criteria: Fasting glucose ≥126 mg/dL, 2-hour glucose ≥200 mg/dL during OGTT, HbA1c ≥6.5%, or random glucose ≥200 mg/dL with symptoms. Prediabetes: HbA1c 5.7-6.4%, fasting glucose 100-125 mg/dL.",
        "source": "ADA Standards of Medical Care 2024", "category": "Endocrine"
    },
    {
        "id": "dm_002",
        "text": "Type 2 Diabetes first-line treatment: Metformin 500-1000mg twice daily with meals if eGFR >30. Target HbA1c <7% for most patients. Add SGLT2 inhibitors (empagliflozin, dapagliflozin) if cardiovascular disease or heart failure. Add GLP-1 agonists (semaglutide, liraglutide) for weight loss benefit. Monitor renal function with metformin.",
        "source": "ADA Standards of Medical Care 2024", "category": "Endocrine"
    },
    {
        "id": "dm_003",
        "text": "Diabetic complications screening: Annual HbA1c, lipid panel, urine albumin-creatinine ratio, serum creatinine/eGFR. Annual dilated eye exam. Foot exam every visit. Blood pressure target <130/80 mmHg in diabetes. Statin therapy for cardiovascular risk reduction.",
        "source": "ADA Standards of Medical Care 2024", "category": "Endocrine"
    },
    # Chest Pain / ACS
    {
        "id": "acs_001",
        "text": "Acute Coronary Syndrome evaluation: ECG within 10 minutes of presentation. Troponin I or T at presentation and 3-6 hours. STEMI: ST elevation ≥1mm in 2 contiguous leads — immediate PCI within 90 minutes. NSTEMI: elevated troponin without ST elevation. Aspirin 325mg immediately, anticoagulation, cardiology consult.",
        "source": "ACC/AHA STEMI Guidelines 2013, Updated 2022", "category": "Cardiovascular Emergency"
    },
    {
        "id": "acs_002",
        "text": "Chest pain differential diagnosis: ACS, pulmonary embolism, aortic dissection, pneumothorax, pericarditis, esophageal spasm. Red flags: diaphoresis, radiation to arm/jaw, hemodynamic instability, oxygen saturation <94%, tearing pain (dissection). D-dimer for PE workup if Wells score indicates.",
        "source": "AHA Chest Pain Guidelines 2021", "category": "Cardiovascular Emergency"
    },
    # Pneumonia
    {
        "id": "pna_001",
        "text": "Community-acquired pneumonia (CAP) diagnosis: Chest X-ray infiltrate plus 2 of: fever >38°C, cough, purulent sputum, leukocytosis >10,000. PSI/PORT score or CURB-65 for severity. CURB-65 ≥2: consider hospitalization. Outpatient treatment: amoxicillin 500mg TID or doxycycline 100mg BID for 5 days if no comorbidities.",
        "source": "IDSA/ATS CAP Guidelines 2019", "category": "Pulmonary/Infectious"
    },
    {
        "id": "pna_002",
        "text": "Hospital-acquired pneumonia treatment: Broad-spectrum coverage with piperacillin-tazobactam or cefepime plus vancomycin if MRSA risk. Procalcitonin to guide antibiotic duration. Oxygen to maintain SpO2 >94%. Blood cultures before antibiotics. Legionella/pneumococcal urinary antigen if severe CAP.",
        "source": "IDSA HAP/VAP Guidelines 2016", "category": "Pulmonary/Infectious"
    },
    # Heart Failure
    {
        "id": "hf_001",
        "text": "Heart failure with reduced EF (HFrEF, EF <40%) treatment: Four pillars — ACE inhibitor/ARB/ARNI (sacubitril-valsartan preferred), beta-blocker (carvedilol, metoprolol succinate), MRA (spironolactone/eplerenone), SGLT2 inhibitor (dapagliflozin/empagliflozin). Loop diuretics for volume overload. ICD if EF <35% on optimal therapy.",
        "source": "ACC/AHA Heart Failure Guidelines 2022", "category": "Cardiovascular"
    },
    # Sepsis
    {
        "id": "sep_001",
        "text": "Sepsis-3 definition: Life-threatening organ dysfunction caused by dysregulated host response to infection. SOFA score increase ≥2. qSOFA: RR≥22, altered mentation, SBP≤100 (score ≥2 suggests sepsis). Septic shock: vasopressors needed to maintain MAP≥65 + lactate >2mmol/L despite fluids.",
        "source": "Surviving Sepsis Campaign Guidelines 2021", "category": "Critical Care"
    },
    {
        "id": "sep_002",
        "text": "Sepsis Hour-1 bundle: Blood cultures x2 before antibiotics, broad-spectrum antibiotics within 1 hour, 30mL/kg crystalloid for hypotension or lactate ≥4, vasopressors (norepinephrine first-line) for MAP <65 despite fluids, lactate measurement. Reassess fluid responsiveness. Source control within 6-12 hours.",
        "source": "Surviving Sepsis Campaign Guidelines 2021", "category": "Critical Care"
    },
    # Atrial Fibrillation
    {
        "id": "afib_001",
        "text": "Atrial fibrillation management: Rate control target HR <110 bpm at rest. Rate control agents: beta-blockers (metoprolol), calcium channel blockers (diltiazem, verapamil), digoxin. Rhythm control with cardioversion or antiarrhythmics (amiodarone, flecainide). CHA2DS2-VASc score for stroke risk — anticoagulate if score ≥2 men, ≥3 women.",
        "source": "ACC/AHA AFib Guidelines 2023", "category": "Cardiovascular"
    },
    {
        "id": "afib_002",
        "text": "Anticoagulation in AFib: DOACs preferred over warfarin — apixaban 5mg BID, rivaroxaban 20mg daily, dabigatran 150mg BID. Warfarin if mechanical heart valve or severe mitral stenosis. HAS-BLED score for bleeding risk. Avoid anticoagulation if CHA2DS2-VASc 0 (men) or 1 (women).",
        "source": "ACC/AHA AFib Guidelines 2023", "category": "Cardiovascular"
    },
    # Hypothyroidism
    {
        "id": "hypo_001",
        "text": "Hypothyroidism diagnosis: TSH >4.5 mIU/L with low free T4 = overt hypothyroidism. TSH elevated with normal free T4 = subclinical hypothyroidism. Symptoms: fatigue, cold intolerance, weight gain, constipation, bradycardia, dry skin, hair loss. Treatment: levothyroxine 1.6 mcg/kg/day, titrate to TSH 0.5-2.5 mIU/L.",
        "source": "ATA Hypothyroidism Guidelines 2014", "category": "Endocrine"
    },
    # UTI
    {
        "id": "uti_001",
        "text": "Uncomplicated UTI treatment (women): Nitrofurantoin 100mg BID x5 days (first-line), trimethoprim-sulfamethoxazole DS BID x3 days if local resistance <20%, fosfomycin 3g single dose. Avoid fluoroquinolones for uncomplicated UTI. Complicated UTI/pyelonephritis: ciprofloxacin 500mg BID x7 days or trimethoprim-sulfamethoxazole x14 days.",
        "source": "IDSA UTI Guidelines 2011, Updated 2024", "category": "Infectious Disease"
    },
    # Asthma
    {
        "id": "asthma_001",
        "text": "Asthma stepwise management: Step 1 (intermittent): SABA PRN. Step 2 (mild persistent): low-dose ICS (budesonide 200-400mcg/day). Step 3: low-dose ICS + LABA or medium ICS. Step 4: medium/high ICS + LABA. Step 5: add tiotropium, biologics (dupilumab, omalizumab). Acute exacerbation: SABA q20min x3, systemic corticosteroids if no improvement.",
        "source": "GINA Asthma Guidelines 2024", "category": "Pulmonary"
    },
    # Depression
    {
        "id": "dep_001",
        "text": "Major depressive disorder treatment: First-line SSRIs — sertraline 50-200mg, escitalopram 10-20mg, fluoxetine 20-60mg. SNRIs: venlafaxine 75-225mg, duloxetine 30-60mg. Allow 4-6 weeks for response. If inadequate response, augment with bupropion, buspirone, or atypical antipsychotic. Psychotherapy (CBT) equally effective for mild-moderate depression.",
        "source": "APA Practice Guidelines for MDD 2023", "category": "Psychiatry"
    },
]


def index_knowledge_base():
    """Index medical knowledge into ChromaDB on startup."""
    existing = collection.count()
    if existing >= len(MEDICAL_KNOWLEDGE):
        print(f"Knowledge base already indexed: {existing} entries")
        return

    print("Indexing medical knowledge base...")
    texts = [item["text"] for item in MEDICAL_KNOWLEDGE]
    embeddings = embedding_model.encode(texts).tolist()

    collection.upsert(
        ids=[item["id"] for item in MEDICAL_KNOWLEDGE],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": item["source"], "category": item["category"]} for item in MEDICAL_KNOWLEDGE]
    )
    print(f"Indexed {len(MEDICAL_KNOWLEDGE)} clinical guidelines")


# Index on startup
index_knowledge_base()


# ── MODELS ────────────────────────────────────────────────────
class PatientQuery(BaseModel):
    symptoms: str
    lab_values: str = ""
    age: int = 0
    weight: str = ""
    medical_history: str = ""
    current_medications: str = ""


class ClinicalResponse(BaseModel):
    synthesis: str
    retrieved_sources: list
    disclaimer: str


# ── ENDPOINTS ─────────────────────────────────────────────────
@app.get("/")
def health_check():
    return {"status": "DocBrief API running", "knowledge_entries": collection.count()}


@app.post("/query", response_model=ClinicalResponse)
async def clinical_query(query: PatientQuery):
    """Main endpoint: takes patient data, retrieves relevant guidelines, returns synthesis."""

    # Build search query from patient data
    search_text = f"{query.symptoms} {query.lab_values} {query.medical_history}"

    # Embed and retrieve relevant guidelines
    query_embedding = embedding_model.encode([search_text]).tolist()[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    retrieved_docs = results["documents"][0]
    retrieved_metadata = results["metadatas"][0]

    # Format context for LLM
    context = "\n\n".join([
        f"[Source: {meta['source']} | Category: {meta['category']}]\n{doc}"
        for doc, meta in zip(retrieved_docs, retrieved_metadata)
    ])

    # Build patient profile
    patient_info = f"Symptoms: {query.symptoms}"
    if query.lab_values:
        patient_info += f"\nLab Values: {query.lab_values}"
    if query.age:
        patient_info += f"\nAge: {query.age}"
    if query.weight:
        patient_info += f"\nWeight: {query.weight}"
    if query.medical_history:
        patient_info += f"\nMedical History: {query.medical_history}"
    if query.current_medications:
        patient_info += f"\nCurrent Medications: {query.current_medications}"

    # Groq LLM synthesis
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1500,
        messages=[
            {
                "role": "system",
                "content": """You are DocBrief, a clinical decision support assistant that helps physicians by synthesizing relevant medical literature.

Your role is to:
1. Identify the most likely clinical considerations based on the patient presentation
2. Surface relevant evidence-based guidelines from the provided sources
3. Highlight key diagnostic criteria and treatment considerations
4. Flag important drug interactions or contraindications
5. Always cite your sources

Important: You are providing clinical reference information to support physician decision-making, not making diagnoses or prescribing medications. Always maintain appropriate clinical boundaries."""
            },
            {
                "role": "user",
                "content": f"""Patient Presentation:
{patient_info}

Relevant Clinical Guidelines Retrieved:
{context}

Please provide a structured clinical evidence synthesis covering:
1. **Clinical Considerations** — What conditions should be considered based on this presentation?
2. **Relevant Diagnostic Criteria** — What diagnostic thresholds or criteria apply?
3. **Evidence-Based Treatment Options** — What does the literature support for this presentation?
4. **Important Flags** — Drug interactions, contraindications, or red flags to consider
5. **Suggested Next Steps** — What additional workup or referrals may be warranted?

Cite the specific guideline source for each recommendation."""
            }
        ]
    )

    # Format sources for response
    sources = [
        {"source": meta["source"], "category": meta["category"], "excerpt": doc[:200] + "..."}
        for doc, meta in zip(retrieved_docs, retrieved_metadata)
    ]

    return ClinicalResponse(
        synthesis=message.choices[0].message.content,
        retrieved_sources=sources,
        disclaimer="DocBrief provides clinical reference information to support physician decision-making. All clinical decisions require physician judgment and direct patient evaluation. This tool does not replace clinical expertise."
    )


@app.get("/knowledge-base")
def get_knowledge_base():
    """Returns summary of loaded clinical guidelines."""
    categories = {}
    for item in MEDICAL_KNOWLEDGE:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "total_entries": len(MEDICAL_KNOWLEDGE),
        "categories": categories
    }
