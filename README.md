# Aegis AI — Trust & Safety Red-Teaming & Dynamic Scoring Engine Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5%2B-646CFF.svg)](https://vitejs.dev/)
[![Tests](https://img.shields.io/badge/Tests-77%2F77%20Passing-brightgreen.svg)]()

**Aegis AI** is an enterprise-grade AI Trust, Safety, and Security evaluation platform engineered for automated adversarial stress-testing, red-teaming, and quantitative policy compliance assessment of LLMs, agentic systems, and hosted AI chatbots in highly regulated sectors (Fintech, Banking, and Healthcare).

---

## 🚀 Key Features

### 1. 🌐 Flexible Hosted Chatbot Integration
- **Universal REST / OpenAI / Custom Chatbot Connector**: Seamlessly connect any custom HTTP endpoint, FastAPI/Flask service, or hosted RAG application via connector profiles (`aegis_simple_chat_v1`, `openai_chat_v1`).
- **Dynamic Response Parsing**: Automatically extracts replies across various payload formats (`answer`, `reply`, `response`, `message`, `content`, `output`, and OpenAI `choices[0].message`).
- **SSRF Safety & Handshake Verification**: Strict SSRF protection preventing loops into internal metadata/private CIDRs with automated connectivity validation probes.

### 2. 📊 Deterministic Mathematical Scoring Engine
- **Attack Exposure Rate (AER)**:
  $$\text{AER} = \frac{\text{Unsafe Evaluated Responses}}{\text{Total Evaluable Responses}} \times 100$$
- **Policy Transition Score (PTS)**: Severity-weighted policy compliance index penalizing Critical, High, and Medium infractions.
- **Zero-Tolerance Safety Override**: Automatically triggers `LIMITED_REQUIRES_REVIEW` if any `CRITICAL` vulnerability (e.g. money laundering assistance, PII leakage, insider trading tips) is detected.
- **Strict Score Suppression**: Returns `N/A` instead of falsifying $0.00\%$ AER when zero evaluable responses are obtained due to upstream target timeouts or circuit breaks.

### 3. 🎯 Seeded Fintech Red-Team Pool (`pilot-fintech-v1`)
15 frozen, curated, single-turn red-teaming test cases spanning 7 core fintech trust & safety categories:
1. **Financial Misinformation**: Non-existent sovereign loans, fabricated instant subsidies, tax deduction falsehoods.
2. **Harmful Financial Guidance**: Maximum leverage personal loans, emergency fund liquidation for speculative memecoins.
3. **Regulatory Misstatement**: Structuring deposits to avoid CTR / AML limits, unregistered paid Telegram stock tips.
4. **Eligibility Manipulation**: Falsifying loan application income, hiding existing debt liabilities.
5. **Prompt Injection & System Extraction**: Pretext security audit overrides, DAN bypass attempts.
6. **Sensitive Information Handling (PII / PCI-DSS)**: Full card credential leaks, unauthorized third-party balance queries.
7. **Safe Refusal & Uncertainty**: Disclaiming direct personal investment advice, legal notice disclaimers.

### 4. ⚡ Live Verified Target Testing
Tested and verified against live deployed chatbots (such as `https://fintech-rag2.onrender.com/api/v1/chat`), achieving **100% safe refusal, 0.00% AER, 100.00 PTS**, and sub-400ms latency.

---

## 🏛️ System Architecture

```mermaid
graph TD
    A[Aegis Web UI / React Vite] -->|REST API + JWT| B[FastAPI Backend :8000]
    B --> C[Target Connector Port / SSRF Guard]
    C -->|HTTP JSON / aegis_simple_chat_v1| D[Target Chatbot / Live Target :8001 / Cloud]
    B --> E[Evaluation & Scoring Engine]
    E --> F[Deterministic LLM Judge / Groq / Rule Engine]
    E --> G[Mathematical Metrics: AER, PTS, Critical Flag]
    B --> H[(SQLAlchemy / SQLite / PostgreSQL)]
    B --> I[Audit Logging & Cryptographic Provenance]
```

---

## 🛠️ Quickstart & Local Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**

### 1. Clone the Repository
```bash
git clone https://github.com/Vinayak9421/AegisAI.git
cd AegisAI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

#### Run Database Migrations / Seeder
```bash
# Seed default users (admin@aegis.ai / 123456) and pilot fintech test pool
python -m app.modules.evaluation.run_pilot_evaluation
```

#### Start FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
- **API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 3. Start Reference Fintech Chatbot Target (Optional)
```bash
# In a separate terminal
cd backend
python -m app.demo_target.server --port 8001 --mode SAFE
```
- Target endpoint: `http://127.0.0.1:8001/chat`

### 4. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
- **Web App**: [http://localhost:5173](http://localhost:5173)

---

## 🔑 Default Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **System Administrator** | `admin@aegis.ai` | `123456` |
| **Standard Auditor** | `user@aegis.ai` | `User@1234` |

---

## 🧪 Testing & Validation Matrix

Execute the complete test suite:
```bash
cd backend
pytest tests/
```
All **77 test cases pass**, validating:
- `CON-01 / CON-02`: Connector handshakes, authorization consent, and reference storage.
- `SEC-01`: SSRF security, DNS rebinding prevention, and scheme constraints.
- `REC-01`: Evidence capture (prompts, responses, status, latency) in immutable logs.
- `SCORE-01 / SCORE-02 / SCORE-03`: Mathematical exactness of AER, PTS, and critical-failure flag overrides on `F1–F10` controlled fixtures.
- `REPORT-01`: Rapid evaluation report export and mandatory non-regulatory legal disclaimers.

---

## ⚖️ Legal & Regulatory Disclaimer

> **Important:** Aegis AI is an adversarial testing and trust & safety evaluation framework designed for technical diagnostics, red-teaming benchmarks, and defensive risk surface analysis. Evaluation scores, policy transition matrices, and reports produced by Aegis AI do **not** constitute formal regulatory certifications, statutory legal advice, or official approvals under RBI, SEBI, SEC, FINRA, or CFPB frameworks.