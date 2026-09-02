# CivicAssist AI

**Multilingual AI-Powered Legal Assistance, Government Scheme Intelligence & Assisted Application Platform**

CivicAssist AI is a multilingual citizen-assistance platform that provides source-grounded legal information, Central and State government scheme updates, eligibility guidance, and assisted application workflows through official portals.

---

## How It Works

CivicAssist AI is built around a Retrieval-Augmented Generation (RAG) architecture rather than relying only on the LLM's pretrained knowledge.

### System Architecture

```
Citizen
   │
   ▼
Multilingual Chat UI
   │
   ▼
FastAPI Backend
   │
   ▼
Query Processing
   │
┌──┴──┐
│     │
▼     ▼
Legal Query   Scheme Query
│     │
└──┬──┘
   ▼
RAG Retrieval
   │
   ▼
Vector Database
   │
   ▼
Verified Government Sources
   │
   ▼
LLM
   │
   ▼
Grounded Answer + Sources
```

### 1. Knowledge Acquisition

The system uses authoritative sources such as:

- Government scheme portals
- Central Government sources
- State Government sources
- Official notifications and documents
- India Code and other authoritative legal sources

Documents are collected and processed before being added to the knowledge base.

### 2. Document Processing

Legal documents and scheme documents are processed through an ingestion pipeline:

```
PDF / Web Source
      ↓
Text Extraction
      ↓
OCR when required
      ↓
Text Cleaning
      ↓
Document Classification
      ↓
Chunking
      ↓
Metadata Generation
      ↓
Embedding Generation
      ↓
Vector Database
```

Each chunk retains metadata such as:

- Document
- Department
- State / Central
- Category
- Publication Date
- Last Updated
- Section / Page
- Official Source

This allows the system to retrieve information while preserving its source and context.

### 3. RAG-Based Retrieval

When a citizen asks a question, the query is converted into an embedding and compared with stored document embeddings.

```
User Question
      ↓
Query Embedding
      ↓
Semantic Search
      ↓
Relevant Knowledge Chunks
      ↓
Context Construction
      ↓
LLM
      ↓
Grounded Response
```

The LLM receives the retrieved official information as context and generates the response from that information.

This reduces dependence on the model's internal knowledge and helps minimize hallucinated legal or scheme information.

### 4. Legal Assistance

For legal queries, the system retrieves relevant legal provisions and authoritative documents.

The response can contain:

- Simple explanation
- Relevant legal provision
- General guidance
- Applicable source
- Document/update information

If sufficient authoritative information cannot be retrieved, the system should avoid inventing an answer and clearly indicate that reliable information was not found.

> The platform provides general legal information and assistance, not a replacement for qualified legal professionals.

### 5. Government Scheme Intelligence

Scheme information is maintained as structured knowledge containing:

- Scheme Name
- Government Level
- Department
- Eligibility
- Benefits
- Required Documents
- Important Dates
- Official Source
- Last Updated

Users can ask questions such as:

- "What schemes are available for students?"
- "Who is eligible for this scheme?"
- "What documents are required?"
- "What are the latest scheme updates?"

The RAG system retrieves the relevant scheme information and generates a personalized response.

### 6. Scheme Update Pipeline

Government information changes frequently. Therefore, the system is designed with an automated update pipeline.

```
Official Government Sources
          ↓
Periodic Monitoring
          ↓
New / Modified Information
          ↓
Content Extraction
          ↓
Version Comparison
          ↓
Knowledge Base Update
          ↓
Updated Vector Index
```

Instead of permanently relying on a static dataset, the knowledge base can be continuously updated when official information changes.

### 7. Multilingual Processing

Citizens can interact with the system in supported Indian languages.

```
User Language
      ↓
Language Detection
      ↓
Query Processing
      ↓
Multilingual Retrieval
      ↓
RAG + LLM
      ↓
Response in User's Language
```

This allows the same knowledge base to serve citizens across different languages.

### 8. AI-Assisted Scheme Application

For supported government schemes, CivicAssist AI can extend beyond information retrieval.

```
User selects scheme
        ↓
Eligibility assessment
        ↓
Official application portal
        ↓
Identify required fields/documents
        ↓
Request required documents
        ↓
OCR / Document Processing
        ↓
Extract relevant information
        ↓
Prepare application
        ↓
Citizen reviews information
        ↓
Citizen confirms
        ↓
Official portal submission
```

The AI does not independently make sensitive decisions on behalf of the citizen.

OTP verification, CAPTCHA, digital signatures, payments, declarations, and final submission remain under citizen control wherever required by the official portal.

### 9. Core Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| LLM | Instruction-following LLM API |
| RAG | Retrieval-Augmented Generation |
| Embeddings | Multilingual embedding model |
| Vector Database | ChromaDB / Qdrant |
| Structured Database | PostgreSQL |
| Document Processing | PyMuPDF / document parsers |
| OCR | Tesseract / compatible OCR engine |
| NLP | Multilingual NLP |
| Application Assistance | Browser automation where supported |

---

## Setup

1. Clone the repository

```
git clone <repository-url>
cd civicassist-ai
```

2. Create Python environment

```
python -m venv venv
```

Windows:

```
venv\Scripts\activate
```

3. Install backend dependencies

```
pip install -r requirements.txt
```

4. Configure environment variables

Create a `.env` file:

```
LLM_API_KEY=your_api_key
DATABASE_URL=your_database_url
VECTOR_DB_PATH=./data/vector_db
```

Do not commit `.env` or API keys to the repository.

5. Start the backend

```
uvicorn app.main:app --reload
```

The FastAPI backend will be available locally.

6. Start the frontend

```
cd frontend
npm install
npm run dev
```

Open the local frontend URL displayed by Vite.

---

## How to Use

### Legal Assistance

1. Open the CivicAssist AI interface.
2. Select the preferred language.
3. Enter a legal question.
4. The system retrieves relevant authoritative information.
5. Review the generated explanation and cited sources.

### Government Scheme Discovery

1. Ask about a requirement or government benefit.
2. The system identifies relevant schemes.
3. Review eligibility, benefits, required documents, and official information.
4. Check the displayed source and update information.

### Scheme Application

For supported schemes:

1. Select the required scheme.
2. Provide the information requested by the AI.
3. Upload the required documents.
4. The system extracts relevant information using document processing/OCR.
5. Review the prepared application.
6. Complete required authentication or sensitive actions.
7. Confirm the final submission through the official government portal.
