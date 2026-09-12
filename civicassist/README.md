# CivicAssist AI

### AI-Powered Civic Assistance for Government Schemes, Legal Information, and Citizen Services

CivicAssist AI is an intelligent, multilingual civic-assistance platform designed to make government schemes, legal information, and public services easier for citizens to understand and access.

The platform combines **AI-powered guidance, authoritative-source retrieval, document intelligence, multilingual interaction, and citizen-controlled application assistance** into a unified system.

Instead of requiring citizens to search through multiple government websites, understand complex terminology, determine eligibility, identify required documents, and navigate application procedures independently, CivicAssist AI guides them through the process from **understanding their situation to taking the appropriate next action**.

---

## Table of Contents

* [Overview](#overview)
* [Problem Statement](#problem-statement)
* [Our Solution](#our-solution)
* [Key Capabilities](#key-capabilities)
* [Core Workflow](#core-workflow)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [AI and Retrieval Architecture](#ai-and-retrieval-architecture)
* [Application Assistance](#application-assistance)
* [Security and Privacy](#security-and-privacy)
* [Installation](#installation)
* [Environment Configuration](#environment-configuration)
* [Running the Application](#running-the-application)
* [API Overview](#api-overview)
* [Testing](#testing)
* [Limitations](#limitations)
* [Future Enhancements](#future-enhancements)
* [Contributing](#contributing)
* [License](#license)

---

## Overview

Citizens frequently face difficulties when accessing public services because information is distributed across different portals, written in complex language, available in different formats, and often requires citizens to understand eligibility rules and documentation requirements.

CivicAssist AI addresses this accessibility gap through a conversational interface that allows citizens to ask questions in natural language and receive practical, structured guidance.

### Core Concept

> **Citizen Situation → Policy → Eligibility → Evidence → Service → Action**

The objective is not simply to provide information, but to help citizens understand:

* What applies to their situation
* Whether they may be eligible
* What benefits or protections may be available
* Which documents are required
* Where and how to apply
* What action they should take next

---

# Problem Statement

Citizens often struggle to access government schemes, legal information, and public services due to:

* Complex government terminology
* Information distributed across multiple portals
* Limited regional-language accessibility
* Difficulty understanding eligibility criteria
* Uncertainty about required documents
* Lack of awareness of available legal protections
* Difficult and lengthy application procedures
* Limited digital literacy
* Difficulty identifying the appropriate government service or authority

These barriers can prevent eligible citizens from effectively accessing essential government benefits and services.

---

# Our Solution

CivicAssist AI provides a unified AI-powered civic assistance layer that connects citizens with relevant government schemes, legal information, and public services.

The platform:

1. Understands the citizen's request.
2. Classifies the request into the appropriate domain.
3. Retrieves authoritative information where required.
4. Extracts relevant information from official webpages or documents.
5. Provides source-grounded guidance.
6. Determines relevant eligibility and requirements where supported by available information.
7. Identifies required documents and next steps.
8. Assists citizens with application workflows where supported.
9. Keeps sensitive authentication and final decisions under citizen control.

---

# Key Capabilities

## 1. Government Scheme Discovery

Citizens can describe their situation in natural language and discover potentially relevant government schemes.

The platform can provide information such as:

* Scheme name
* Purpose
* Benefits
* Eligibility requirements
* Required documents
* Application procedure
* Official source
* Relevant next steps

Example:

> "I am a small farmer. What government schemes can I apply for?"

---

## 2. Legal Information Assistance

CivicAssist AI helps citizens understand general legal information in simple language.

Example scenarios include:

* Tenant and eviction issues
* Consumer disputes
* Property-related issues
* Workplace concerns
* Police complaints
* Domestic-violence-related assistance
* Legal-aid availability
* General rights and procedures

The system is designed to provide **general legal information**, not replace qualified legal professionals.

---

## 3. Source-Grounded Responses

For scheme and legal queries, CivicAssist AI can retrieve information from authoritative sources and extract relevant content before generating the response.

The intended flow is:

```text
Citizen Query
      ↓
Query Classification
      ↓
Official Source Search
      ↓
Official Website / Document
      ↓
Content Extraction
      ↓
Relevant Context
      ↓
LLM
      ↓
Grounded Response
```

This reduces reliance on unsupported or potentially outdated generated information.

---

## 4. Multilingual Support

Citizens can interact with the platform in supported languages.

The multilingual layer is designed to make civic information more accessible to:

* Regional-language users
* Rural communities
* Elderly citizens
* Citizens with limited digital literacy

---

## 5. Eligibility and Document Guidance

CivicAssist AI can explain:

### Eligibility

* Age requirements
* Occupation/category requirements
* Income-related requirements
* Location requirements
* Other scheme-specific conditions

### Required Documents

Depending on the service or scheme, the platform can identify documents such as:

* Identity documents
* Address proof
* Income certificates
* Educational certificates
* Bank-related documents
* Property documents
* Other scheme-specific evidence

The system does not assume that a document is required unless the available authoritative information supports it.

---

## 6. Application Assistance

For supported government services, CivicAssist AI can assist citizens with application preparation and workflow navigation.

The intended process includes:

```text
Identify Service
      ↓
Find Official Portal
      ↓
Understand Procedure
      ↓
Identify Required Documents
      ↓
Collect Documents
      ↓
OCR / Data Extraction
      ↓
Prepare Application Data
      ↓
Validate Information
      ↓
Citizen Review
      ↓
Citizen-Controlled Final Action
```

The system does **not** request or handle sensitive authentication information such as:

* OTPs
* CAPTCHA answers
* Passwords
* Digital signatures
* Payment credentials

Final declarations, payments, and submission remain under citizen control.

---

# Core Workflow

The complete CivicAssist workflow can be summarized as follows:

```text
                    Citizen
                       │
                       ▼
              Natural Language Query
                       │
                       ▼
               Query Classifier
                 /     |      \
                /      |       \
               ▼       ▼        ▼
           General   Scheme    Legal
               │       │        │
               │       ▼        ▼
               │   Official   Official
               │    Source     Source
               │       │        │
               │       ▼        ▼
               │   Web/PDF Content Extraction
               │       │        │
               └───────┼────────┘
                       ▼
                Context / RAG
                       │
                       ▼
                     LLM
                       │
                       ▼
             Structured Civic Guidance
                       │
                       ▼
        Eligibility / Documents / Procedure
                       │
                       ▼
                Next Best Action
```

---

# System Architecture

CivicAssist AI follows a modular backend architecture.

```text
┌───────────────────────────────┐
│          Citizen              │
│   Web / Touchscreen Interface │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Frontend Layer         │
│        HTML / CSS / JS        │
└───────────────┬───────────────┘
                │ HTTP / REST
                ▼
┌───────────────────────────────┐
│        FastAPI Backend        │
│                               │
│  Chat | Schemes | Legal       │
│  Documents | Applications    │
└───────────────┬───────────────┘
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
┌──────────┐ ┌────────┐ ┌─────────────┐
│ Query    │ │  RAG   │ │ Web Research│
│Classifier│ │ Engine │ │   Service   │
└────┬─────┘ └───┬────┘ └──────┬──────┘
     │           │             │
     │           ▼             ▼
     │       ChromaDB     Official Sources
     │
     └──────────────┬──────────────┐
                    ▼              │
              ┌───────────┐        │
              │    LLM    │◄───────┘
              └─────┬─────┘
                    │
                    ▼
             Citizen Response
```

---

# Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript

## Backend

* Python
* FastAPI
* Uvicorn

## AI / LLM

* Google Gemini API
* Configurable LLM service architecture

## Retrieval-Augmented Generation

* LangChain / retrieval components
* ChromaDB
* Sentence Transformers
* Multilingual embeddings

## Web Research

* Tavily
* HTTPX
* BeautifulSoup
* PyMuPDF

## Document Intelligence

* PyMuPDF
* OCR capabilities
* Tesseract (where required)

## Browser Automation

* Playwright for supported application workflows

## Data Layer

* ChromaDB
* PostgreSQL / SQLite depending on deployment requirements

## Hardware Interface

The system can be extended to a touchscreen-based civic-assistance terminal using:

* ESP32 or Raspberry Pi
* TFT touchscreen
* Wi-Fi connectivity

The AI and retrieval workloads remain on the backend rather than being executed directly on the microcontroller.

---

# Project Structure

```text
civicassist/
│
├── Backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── routers/
│   │   │   ├── chat.py
│   │   │   ├── schemes.py
│   │   │   ├── legal.py
│   │   │   ├── documents.py
│   │   │   ├── applications.py
│   │   │   ├── language.py
│   │   │   └── history.py
│   │   │
│   │   ├── engines/
│   │   │   ├── legal_engine.py
│   │   │   ├── scheme_engine.py
│   │   │   ├── application_engine.py
│   │   │   └── language_engine.py
│   │   │
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── document_service.py
│   │   │   ├── web_research_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── history_service.py
│   │   │   ├── query_classifier.py
│   │   │   └── tavily_service.py
│   │   │
│   │   ├── models/
│   │   ├── database/
│   │   └── config.py
│   │
│   ├── data/
│   │   ├── legal/
│   │   └── schemes/
│   │
│   ├── uploads/
│   ├── vector_db/
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
│
└── README.md
```

---

# AI and Retrieval Architecture

CivicAssist AI uses different processing paths depending on the nature of the query.

### General Query

```text
User
 ↓
Query Classifier
 ↓
General
 ↓
LLM
 ↓
Response
```

### Scheme / Legal Query

```text
User
 ↓
Query Classifier
 ↓
Scheme / Legal
 ↓
Tavily
 ↓
Official Government Source
 ↓
Web/PDF Extraction
 ↓
Temporary Context
 ↓
LLM
 ↓
Source-Grounded Response
```

### Retrieval Fallback

If an authoritative live source cannot be retrieved:

```text
Official Source Unavailable
          ↓
       ChromaDB
          ↓
   Relevant Documents
          ↓
       Context
          ↓
         LLM
```

Website content retrieved during the live research path is treated as temporary context and is not automatically inserted into the vector database.

---

# Policy-to-Action Layer

A key design principle of CivicAssist AI is moving beyond information retrieval.

The platform is designed around a **Policy-to-Action** concept:

```text
Situation
   ↓
Relevant Policy
   ↓
Eligibility
   ↓
Required Evidence
   ↓
Available Service
   ↓
Next Action
```

This allows the platform to bridge the gap between:

> "What information exists?"

and

> "What can I do next?"

---

# Application Assistance Architecture

For application workflows, CivicAssist can use specialized tools and services.

```text
                 Application Agent
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     Browser Tools  Document Tools  Validation
          │             │             │
          ▼             ▼             ▼
     Official Portal   OCR/Data      Form Checks
                       Extraction
          │
          ▼
   Citizen Review
          │
          ▼
 Citizen-Controlled Action
```

The architecture follows a human-in-the-loop model.

### The LLM acts as the reasoning layer.

### Tools act as the execution layer.

### FastAPI coordinates the workflow.

### The citizen remains the final authority.

---

# Security and Privacy

CivicAssist AI follows a security-conscious architecture.

## API Key Protection

API keys are stored in environment variables and are never intended to be committed to source control.

```text
.env              → DO NOT COMMIT
.env.example      → Safe placeholder configuration
.gitignore        → Exclude secrets
```

## Sensitive Authentication

The platform does not request citizens to provide:

* Passwords
* OTPs
* CAPTCHA responses
* Digital-signature credentials
* Payment credentials

## Citizen-Controlled Actions

Actions with legal, financial, or authentication consequences remain under citizen control.

## Source Verification

Government and legal information should be grounded in authoritative sources whenever possible.

---

# Installation

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd civicassist
```

## 2. Create a Virtual Environment

Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file inside the backend directory.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model

TAVILY_API_KEY=your_tavily_api_key

VECTOR_DB_PATH=vector_db
```

### Important

Do not commit `.env` to GitHub.

Use `.env.example` for sharing the required configuration structure:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model
TAVILY_API_KEY=your_tavily_api_key
VECTOR_DB_PATH=vector_db
```

---

# Running the Application

Navigate to the backend:

```cmd
cd Backend
```

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Start FastAPI:

```cmd
uvicorn app.main:app --reload
```

If port `8000` is unavailable:

```cmd
uvicorn app.main:app --reload --port 8001
```

The API will be available at:

```text
http://127.0.0.1:8000
```

or, when using port 8001:

```text
http://127.0.0.1:8001
```

FastAPI interactive documentation is available at:

```text
/docs
```

---

# API Overview

## Chat

```http
POST /api/chat
```

Example request:

```json
{
  "message": "My landlord is asking me to leave without notice. What are my legal rights?",
  "language": "en"
}
```

The backend classifies the query and routes it through the appropriate processing pipeline.

---

## Chat Health

```http
GET /api/chat/health
```

Example response:

```json
{
  "status": "ok",
  "service": "chat"
}
```

---

# Testing

CivicAssist should be tested across all major processing paths.

## Legal Test

```text
My landlord is asking me to leave my rented house without giving me any notice. What are my legal rights?
```

Expected flow:

```text
Legal Classification
       ↓
Official Source Search
       ↓
Content Extraction
       ↓
LLM
       ↓
Legal Guidance
```

## Scheme Test

```text
I am a small farmer. What government schemes am I eligible for and what documents do I need?
```

Expected flow:

```text
Scheme Classification
       ↓
Official Source Search
       ↓
Content Extraction
       ↓
LLM
       ↓
Scheme Guidance
```

## General Test

```text
What is the difference between a CPU and a GPU?
```

Expected flow:

```text
General Classification
       ↓
Direct LLM
       ↓
Response
```

---

# Limitations

CivicAssist AI is intended to assist citizens, not replace government authorities, lawyers, or official service providers.

The system may be affected by:

* Changes to government websites
* Temporary unavailability of official portals
* Changes in scheme eligibility rules
* Changes in legal provisions
* Incomplete or inaccessible web content
* OCR errors
* Third-party API availability and quotas
* Portal-specific restrictions on automation

Information should always be verified against the relevant official source before making important legal, financial, or administrative decisions.

---

# Future Enhancements

Planned and potential improvements include:

### Policy Change Detection

Automatically detect significant changes in schemes, rules, eligibility criteria, and procedures.

### Policy-Impact Propagation

When a policy changes:

```text
Policy Change
     ↓
Affected Scheme / Rule
     ↓
Affected Eligibility Logic
     ↓
Affected Citizen Guidance
     ↓
Updated Recommendations
```

### Expanded Multilingual Support

Support additional Indian regional languages and improve conversational quality.

### Citizen Service Agent

Expand supported application workflows while maintaining human-in-the-loop safeguards.

### Location-Based Services

Connect citizens with nearby:

* Government offices
* e-Sevai centres
* Legal-aid centres
* Public service facilities

### Improved Document Intelligence

Enhance OCR, document classification, structured data extraction, and document validation.

### Touchscreen Civic Terminal

Deploy CivicAssist through a dedicated low-cost touchscreen terminal for citizens with limited access to conventional digital devices.

---

# Responsible AI Principles

CivicAssist AI is designed around the following principles:

### Accuracy

Prefer authoritative information and clearly communicate uncertainty.

### Transparency

Expose the source used for scheme and legal information whenever available.

### Privacy

Protect API keys and sensitive citizen information.

### Human Control

Keep consequential actions under citizen control.

### Accessibility

Support simple language, multilingual interaction, and accessible interfaces.

### Safety

Do not fabricate legal provisions, eligibility rules, documents, or application completion status.

---

# Contributing

Contributions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Test the implementation.
5. Commit your changes.

```bash
git commit -m "Add your feature"
```

6. Push the branch.

```bash
git push origin feature/your-feature
```

7. Open a Pull Request.

Please avoid committing:

* API keys
* `.env` files
* User documents
* Authentication credentials
* Personally identifiable information

---

# License

This project is currently intended for educational, research, and hackathon development purposes.

A formal open-source license can be added when the project's distribution terms are finalized.

---

# Project Vision

CivicAssist AI aims to make civic information **understandable, accessible, and actionable**.

The long-term vision is to create a trusted digital civic assistant that helps citizens move from:

> **"I don't know what applies to me."**

to:

> **"I understand my options, I know what I need, and I know what to do next."**

---

## CivicAssist AI

**Understand. Verify. Act.**

A citizen-centric AI layer connecting **people, policies, services, and action**.
