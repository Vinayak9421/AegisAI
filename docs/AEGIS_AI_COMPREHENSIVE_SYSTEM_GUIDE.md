# Aegis AI: Comprehensive System Architecture & Working Guide

> **An Automated Adversarial Red-Teaming & Safety Certification Platform for Financial LLMs and AI Agents**

---

## 1. Executive Overview

**Aegis AI** is an enterprise-grade automated safety evaluation and adversarial red-teaming platform specifically engineered for financial artificial intelligence. Modern financial institutions and fintech enterprises deploy Large Language Models (LLMs) for high-stakes workflows—such as retail banking chatbots, loan underwriting assistants, quantitative research advisors, and customer support agents.

However, generic LLM guardrails fail to address financial-specific risks such as:
- **Wire fraud & AML (Anti-Money Laundering) evasion**
- **2FA/OTP extraction & identity theft bypass**
- **Predatory product steering & APR/fee concealment**
- **Unauthorized investment advisory & SEC/FINRA evasion**
- **Multi-turn conversational jailbreaks (Crescendo attacks)**
- **Hallucinated interest rates & false yield claims**

Aegis AI provides a complete end-to-end testing pipeline that connects directly to target LLM endpoints, injects curated single-turn and multi-turn adversarial attack vectors across **6 Financial Threat Pillars**, audits outputs using an independent dual-phase LLM judge (**Groq Llama-3.3-70B**), and issues verifiable, cryptographically signed **Trust & Safety Certificates** with complete vulnerability remediation logs.

---

## 2. High-Level System Architecture

The Aegis AI system is divided into four cleanly decoupled tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION TIER                             │
│  React 19 • Vite • Tailwind CSS • Framer Motion • Lucide Icons        │
│  [Landing Page] [Target Connect] [Test Suites] [Simulation] [Report]   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST & SSE Streaming
┌───────────────────────────────────▼────────────────────────────────────┐
│                           API & SERVICE TIER                           │
│  FastAPI (Python 3.11+) • Pydantic v2 • SQLAlchemy 2.0 ORM             │
│  [Auth/Tenants] [Target Management] [Benchmarks] [Jobs] [Certificates] │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         │                                                     │
┌────────▼────────────────────────────┐       ┌────────────────▼─────────┐
│     EVALUATION & RUNNER ENGINE      │       │     PERSISTENCE TIER     │
│  • Stratified Sampling Engine       │       │  PostgreSQL Relational   │
│  • Pacing & Rate-Limit Controllers  │       │  • Targets & Credentials │
│  • Stateful Multi-Turn Runner       │       │  • Benchmarks & Vectors  │
│  • AES-256 In-Memory Credential Dec │       │  • Jobs & Work Items     │
│  • Dual-Phase Groq Llama-3.3 Judge  │       │  • Sessions & Turns      │
│  • Multi-Dimensional Scoring Engine │       │  • Results & Certificates│
└─────────────────────────────────────┘       └──────────────────────────┘
```

---

## 3. End-to-End User & Execution Flow

Below is the exact step-by-step workflow of how Aegis AI operates from target onboarding to final safety certification:

```
 Step 1: Target Endpoint Registration & Pre-Flight Probe
 ┌────────────────────────────────────────────────────────┐
 │ User enters Target API URL, API Key, Model Tag         │
 │ Aegis AI runs Pre-Flight Diagnostic (SSRF, Latency,    │
 │ Protocol Handshake). Target is verified.               │
 └──────────────────────────┬─────────────────────────────┘
                            │
 Step 2: Test Suite Selection or Custom Ingestion
 ┌──────────────────────────▼─────────────────────────────┐
 │ User selects Quick Run (25 vectors), Full Audit (150+),│
 │ or uploads a custom CSV / multi-turn JSON threat suite.│
 │ Stratified Sampling draws balanced vectors across 6    │
 │ threat pillars using deterministic seed.               │
 └──────────────────────────┬─────────────────────────────┘
                            │
 Step 3: Adversarial Dispatch & Live Execution
 ┌──────────────────────────▼─────────────────────────────┐
 │ Runner dispatches attack payloads to Target LLM        │
 │ • Single-turn prompts sent via target protocol.        │
 │ • Multi-turn sessions executed turn-by-turn.           │
 │ Target responds; raw output is captured.               │
 └──────────────────────────┬─────────────────────────────┘
                            │
 Step 4: Independent Dual-Phase Judging
 ┌──────────────────────────▼─────────────────────────────┐
 │ Attack Prompt + Target Response routed to Groq         │
 │ Llama-3.3-70B with anti-injection JSON prompt rubric.  │
 │ Evaluator classifies: SAFE (Defended) vs UNSAFE (Breach│
 │ with severity level and formal reasoning).             │
 └──────────────────────────┬─────────────────────────────┘
                            │
 Step 5: Multi-Dimensional Risk Scoring
 ┌──────────────────────────▼─────────────────────────────┐
 │ Scoring Engine calculates defense score for each of 6  │
 │ Threat Pillars, overall AER, and Composite Trust Score.│
 └──────────────────────────┬─────────────────────────────┘
                            │
 Step 6: Trust & Safety Certificate Generation
 ┌──────────────────────────▼─────────────────────────────┐
 │ Immutable Certificate generated with SHA-256 tamper-  │
 │ evident hash, full failure audit trail, and print/PDF  │
 │ export capabilities.                                   │
 └────────────────────────────────────────────────────────┘
```

---

## 4. Key Modules & Working Components

### 4.1. Public Landing Page & Interactive Vulnerability Sandbox
- **Route**: `/`
- **Purpose**: Welcomes visitors with a modern light-enterprise interface explaining the platform's mission and value proposition.
- **Components**:
  - **Hero Section**: Key value proposition, real-time live telemetry metrics (1,000+ adversarial vectors, 6 threat pillars, dual-phase judge validation).
  - **Live Interactive Sandbox**: An in-browser interactive simulator that lets visitors step through simulated attacks (Direct Injection, Sybil AML Laundering, Multi-Turn Crescendo) across Turn 1, Turn 2, and Turn 3, inspecting raw model output side-by-side with Groq judge verdicts.
  - **6 Threat Pillars Grid**: Visual breakdown of financial threat vectors matching the internal catalog.
  - **Navigation Bar**: Clean sticky header with quick jump links and direct "Launch Console" CTA leading to `/login`.

### 4.2. Target Connection & Pre-Flight Diagnostic Probe
- **Route**: `/connect`
- **Purpose**: Connects the evaluation engine to the user's chatbot or model gateway.
- **Capabilities**:
  - **Supported Endpoints**: Standard OpenAI Chat format (`/v1/chat/completions`), Hugging Face Router, Google Gemini, OpenRouter, and local deployments (vLLM, Ollama, LM Studio).
  - **Architectural Presets**: One-click configuration pills for Hugging Face, Gemini Flash, OpenAI, and internal mock targets.
  - **Security & Privacy**: API keys and tokens are encrypted using **AES-256-GCM**. Credentials are never stored in plain text and are decrypted strictly in memory for outbound calls.
  - **Pre-Flight Connectivity Diagnostic**: Before any attack batch is dispatched, the backend sends a non-invasive diagnostic probe (`POST /api/v1/targets/{id}/verify`) to validate latency, round-trip HTTP status, TLS handshake, and SSRF bounding (strictly preventing egress to RFC 1918 private subnets).
  - **Provider Error Surfacing**: If an upstream model returns an error (such as an unsupported model name or invalid API key), the diagnostic card extracts and displays the provider's exact error message.

### 4.3. Threat Benchmark Catalog & Custom Suite Uploader
- **Route**: `/test-suites`
- **Purpose**: Central catalog for viewing, searching, uploading, and managing adversarial attack datasets.
- **Components**:
  - **Test Prompts Tab**: Full text search and category filtering across thousands of curated adversarial test cases with OWASP IDs, intent, and severity ceiling.
  - **Benchmark Sources Tab**: Dynamic grid displaying every registered benchmark source (e.g., *FinRed R1-R5*, *HarmBench*, *AdvBench*, and custom uploaded suites). Each card displays its total test cases, timestamped version string, and SHA-256 manifest hash.
  - **Custom Test Suite File Uploader**:
    - Supports uploading custom **CSV** or **JSON** test vector files.
    - Features instant in-browser schema validation and table preview before uploading.
    - Automatic SHA-256 deduplication prevents duplicate prompts from entering the database.
    - Supports single-turn prompts and scripted multi-turn conversational dialog trees.
    - Includes sample CSV and JSON template download buttons.
  - **Delete Benchmark Suite**: Each suite card includes a delete button with a confirmation modal that safely cascades and removes the suite and its test cases from the database.

### 4.4. Live Simulation & Real-Time Adversarial Execution
- **Route**: `/simulation`
- **Purpose**: Real-time console that displays live telemetry as adversarial test items are dispatched against the target LLM.
- **Features**:
  - **Live Execution Stream**: Chat-style message stream displaying the dispatched attack payload, target model output, and independent Groq judge audit verdict.
  - **Progress Counter**: Real-time counter (e.g., `24 / 25 Items`) with animated pulse indicators.
  - **Security Exposure Telemetry**: Live AER (Attack Exposure Rate / Harm Rate) meter tracking safe refusals versus adversarial breaches.
  - **Threat Vector Checklist**: Dynamic status checklist displaying pass/fail indicators across all 6 financial threat pillars in real time.
  - **Pacing Delay & Rate-Limit Resilience**: Configurable request pacing (defaulting to at least 2.5–6.0s between calls) prevents HTTP 429 rate-limiting on target APIs and Groq judge endpoints.
  - **Completion Banner**: Automatically switches to an "Audit Ready" banner when the batch finishes, providing a one-click button to view the finalized Safety Certificate.

### 4.5. Multi-Turn Conversational Session Engine (Crescendo Probing)
- **File**: `backend/app/modules/evaluation/runner.py`
- **Purpose**: Simulates real-world attackers who rarely breach a model in a single prompt, but instead use multi-turn conversational escalation.
- **Workflow**:
  1. Instantiates a durable `EvalSession` record with max turns.
  2. Dispatches Turn 1 (e.g., innocent inquiry about wire transfer compliance).
  3. Receives target response, stores it in conversation memory, and hashes the turn history.
  4. Dispatches Turn 2 with context accumulation (e.g., hypothetical bypass logic).
  5. Dispatches Turn 3 (explicit jailbreak request utilizing conversational momentum).
  6. Evaluates each turn with the independent judge and records **Turn-to-Harm (TTH)**—the exact turn index where guardrails failed.

### 4.6. Independent Dual-Phase LLM Judging
- **File**: `backend/app/judging/groq_judge.py`
- **Model**: **Groq Llama-3.3-70B-Versatile** (with deterministic heuristic fallback).
- **Evaluation Mechanism**:
  - Uses an isolated system prompt containing strict anti-injection fencing (ignoring any instructions embedded in the target's output).
  - Evaluates against specific financial rubrics (e.g., Truth in Lending Act, Bank Secrecy Act, SEC Rule 10b-5).
  - Enforces strict JSON Schema response:
    - `verdict`: `"SAFE"` (model refused or provided compliant answer) vs `"UNSAFE"` (model assisted with fraud, leaked credentials, or bypassed rules).
    - `severity`: `"CRITICAL"`, `"HIGH"`, `"MEDIUM"`, `"LOW"`, or `"NONE"`.
    - `rationale`: Clear, objective legal/safety explanation for the verdict.
  - Includes automatic exponential backoff retry (2s, 4s, 8s) for Groq rate limits (HTTP 429).

### 4.7. Safety Certification & Audit Report
- **Route**: `/report/:reportId`
- **Purpose**: Formal cryptographic Trust & Safety Certificate suitable for compliance reviews, executive sign-off, and security audits.
- **Components**:
  - **Certificate Header**: Official Attestation Seal, Certificate Number (e.g., `AEGIS-9D3E02A1-2026`), timestamp, target name, and SHA-256 report hash with one-click clipboard copy.
  - **Composite Trust Score & Grade**: Large grade badge (`Grade A`, `Grade B`, `Grade C`, `Grade F`) and overall Trust Score (0–100%).
  - **Multi-Dimensional Risk Matrix**: 6-card grid detailing defense scores, pass/fail counts, weights, and colored progress bars for all 6 Financial Threat Pillars.
  - **Critical Vulnerability Audit Register**: Interactive failure ledger with category and severity filter tabs, expandable failure cards showing full attack prompt, target model response, and judge rationale, plus client-side pagination.
  - **Export Actions**: One-click **JSON Data Export** and **Print / PDF Export** optimized with print-specific stylesheets (`@media print`).

---

## 5. Summary of System Capabilities

| Capability | Description | Status |
| :--- | :--- | :---: |
| **OpenAI / Gemini / HF Gateway** | Outbound connectors with AES-256 decrypted credentials in memory | Verified |
| **Pre-Flight Diagnostics** | Latency check, SSRF protection, provider error parsing | Verified |
| **The 6 Financial Threat Pillars** | Domain taxonomy covering fraud, compliance, jailbreaks, and grounding | Verified |
| **Custom Suite Ingestion** | CSV and JSON uploader with validation, preview, and deduplication | Verified |
| **Multi-Turn Crescendo Engine** | Stateful conversational sessions tracking Turn-to-Harm (TTH) | Verified |
| **Dual-Phase Groq Judge** | Llama-3.3-70B independent evaluation with retry and heuristic fallback | Verified |
| **Multi-Dimensional Scoring** | Balanced defense scores, weighted severity penalties, composite score | Verified |
| **Signed Safety Certificate** | Cryptographic SHA-256 evidence hashing, failure register, PDF export | Verified |
| **Fault-Tolerant Runner** | Non-blocking exception isolation, auto-recovery on restart | Verified |
