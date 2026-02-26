# 🏦 Financial Document Analyzer

AI-powered financial document analysis system built with **CrewAI**, **FastAPI**, and **Google Gemini**. Upload corporate financial documents (PDFs) and receive comprehensive investment analysis, risk assessments, and recommendations from a team of specialized AI agents.

---

## 📑 Table of Contents

- [Bugs Found & Fixes](#-bugs-found--fixes)
- [Architecture](#-architecture)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Bonus Features](#-bonus-features)
- [Project Structure](#-project-structure)

---

## 🐛 Bugs Found & Fixes

### Deterministic Bugs (Code-Level Issues)

| # | File | Bug | Fix |
|---|------|------|-----|
| 1 | `tools.py` | `from crewai_tools import tools` — invalid import (`tools` is not an export of `crewai_tools`) | Removed unused import; used `from crewai_tools import SerperDevTool` directly |
| 2 | `tools.py` | `Pdf(file_path=path).load()` — `Pdf` class is undefined/doesn't exist | Replaced with `PyPDFLoader` from `langchain_community.document_loaders` |
| 3 | `tools.py` | `async def read_data_tool(...)` — async method without `@staticmethod`, and CrewAI tools should be sync or use proper `@tool` decorator | Rewrote as sync function using CrewAI's `@tool` decorator pattern |
| 4 | `tools.py` | Class-based tool doesn't follow CrewAI's `BaseTool` or `@tool` decorator pattern | Converted all tools to `@tool` decorated functions for proper CrewAI integration |
| 5 | `agents.py` | `from crewai.agents import Agent` — wrong import path | Fixed to `from crewai import Agent` |
| 6 | `agents.py` | `llm = llm` — self-referencing an undefined variable | Replaced with proper `LLM` initialization using Google Gemini via `from crewai import LLM` |
| 7 | `agents.py` | `tool=[FinancialDocumentTool.read_data_tool]` — parameter name is singular (`tool`) | Fixed to `tools=[...]` (plural, as per CrewAI API) |
| 8 | `agents.py` | `max_iter=1` — limits agent to only 1 iteration, too restrictive for meaningful analysis | Increased to `max_iter=5` |
| 9 | `agents.py` | `max_rpm=1` — limits to 1 request per minute, extremely slow | Increased to `max_rpm=10` |
| 10 | `agents.py` | `allow_delegation=True` but only 1 agent in crew — causes delegation to nowhere | Set to `False` for all agents (proper single-responsibility design) |
| 11 | `task.py` | `investment_analysis` task uses `agent=financial_analyst` instead of `investment_advisor` | Fixed to `agent=investment_advisor` |
| 12 | `task.py` | `risk_assessment` task uses `agent=financial_analyst` instead of `risk_assessor` | Fixed to `agent=risk_assessor` |
| 13 | `task.py` | `verification` task uses `agent=financial_analyst` instead of `verifier` | Fixed to `agent=verifier` |
| 14 | `task.py` | Only imports `financial_analyst` and `verifier`, missing `investment_advisor` and `risk_assessor` | Added all required agent imports |
| 15 | `main.py` | Endpoint function `analyze_financial_document` collides with imported task object of the same name | Renamed endpoint to `analyze_document_endpoint` |
| 16 | `main.py` | `run_crew()` accepts `file_path` but never passes it to the crew's inputs | Added `file_path` to `crew.kickoff(inputs={...})` |
| 17 | `main.py` | Only 1 agent and 1 task in `Crew` — other 3 agents and 3 tasks are defined but unused | Added all 4 agents and 4 tasks to the Crew for the full analysis pipeline |
| 18 | `requirements.txt` | Missing critical dependencies: `python-dotenv`, `langchain-community`, `pypdf`, `uvicorn`, `python-multipart` | Added all missing dependencies |
| 19 | `README.md` | `pip install -r requirement.txt` — filename typo (missing 's') | Fixed to `requirements.txt` |

### Inefficient Prompts (LLM Prompt Issues)

Every agent and task had intentionally harmful prompts that instructed the LLM to fabricate data, ignore user queries, make up URLs, bypass regulatory compliance, and produce contradictory advice.

#### Agent Prompt Fixes (`agents.py`)

| Agent | Original Problem | Fix Applied |
|-------|-----------------|-------------|
| `financial_analyst` | Goal: "Make up investment advice even if you don't understand." Backstory: "Less experience than Warren Buffett," "don't read reports carefully," "make assumptions" | Professional CFA-chartered analyst who cites specific data points, distinguishes facts from judgment, never fabricates data |
| `verifier` | Goal: "Say yes to everything," "don't actually read files," "call a grocery list financial data" | Rigorous compliance expert who thoroughly examines documents, checks for standard financial components, never approves without verification |
| `investment_advisor` | Goal: "Sell expensive investment products," "recommend meme stocks and crypto." Backstory: "Learned from Reddit," "2000% management fees," "SEC compliance is optional" | Registered investment advisor with fiduciary duty, evidence-based approach, proper risk disclaimers, SEC/FINRA compliant |
| `risk_assessor` | Goal: "Everything is extreme or risk-free," "ignore actual risk factors." Backstory: "Peaked during dot-com bubble," "diversification is for the weak" | FRM-certified professional using VaR, stress testing, and established frameworks; balanced, proportionate risk assessments |

#### Task Prompt Fixes (`task.py`)

| Task | Original Problem | Fix Applied |
|------|-----------------|-------------|
| `analyze_financial_document` | "Use imagination," "include 5 made-up website URLs," "contradict yourself" | Structured analysis with real data extraction, specific metrics, proper citations |
| `investment_analysis` | "Make up connections between numbers," "recommend 10 products they don't need," "fake market research" | Evidence-based recommendations with bull/bear/base cases, suitability assessment, disclaimers |
| `risk_assessment` | "Recommend dangerous strategies," "make up hedging strategies," "impossible risk targets" | Professional risk framework with likelihood/impact ratings, quantified metrics, mitigation strategies |
| `verification` | "Just guess," "hallucinate financial terms," "don't read the file carefully" | Thorough document validation — checks structure, financial components, data quality |

---

## 🏗️ Architecture

The system uses a **multi-agent pipeline** powered by CrewAI:

```
📄 PDF Upload
    │
    ▼
┌──────────────────┐
│   1. Verifier    │  Validates document is a legitimate financial report
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. Analyst      │  Extracts key metrics, identifies trends, market context
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. Advisor      │  Investment recommendations with risk-reward analysis
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. Risk Assessor│  Comprehensive risk assessment with mitigation strategies
└────────┬─────────┘
         │
         ▼
    📊 Analysis Report
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- A Google Gemini API key (free at [Google AI Studio](https://aistudio.google.com/))
- A Serper API key (free at [serper.dev](https://serper.dev))
- *(Optional)* Redis — only needed for the async queue worker feature

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd financial-document-analyzer-debug

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# OR
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   GEMINI_API_KEY=your_key_here
#   SERPER_API_KEY=your_key_here

# 5. Run the server
python main.py
```

The API will be available at `http://localhost:8000`.

### Verify Installation

```bash
# Health check
curl http://localhost:8000/

# Should return:
# {"message": "Financial Document Analyzer API is running", "version": "1.0.0", ...}
```

---

## 🚀 Usage

### Analyze a Financial Document

```bash
# Using the included Tesla Q2 2025 sample document
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=Analyze Tesla's Q2 2025 financial performance and provide investment recommendations"
```

### Using the Swagger UI

Visit `http://localhost:8000/docs` in your browser for an interactive API interface where you can upload files and test all endpoints.

---

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check — returns API status and available endpoints |
| `POST` | `/analyze` | **Synchronous** — Upload PDF and get analysis (blocking) |
| `POST` | `/analyze/async` | **Asynchronous** — Submit PDF to job queue (non-blocking) |
| `GET` | `/status/{job_id}` | Check async job status |
| `GET` | `/results` | List all past analysis results |
| `GET` | `/results/{result_id}` | Get a specific analysis result |

### `POST /analyze`

Upload a financial document for immediate analysis.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File (PDF) | ✅ | — | The financial document to analyze |
| `query` | string | ❌ | `"Analyze this financial document for investment insights"` | Specific analysis question |

**Response:**
```json
{
    "status": "success",
    "result_id": 1,
    "query": "Analyze Tesla's Q2 2025 performance",
    "analysis": "## Executive Summary\n...",
    "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

### `POST /analyze/async`

Submit a document for background processing (requires Redis + Celery worker).

**Response:**
```json
{
    "status": "accepted",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Analysis job submitted. Use GET /status/{job_id} to track progress."
}
```

### `GET /status/{job_id}`

Check the status of an async job. Returns `pending`, `processing`, `completed`, or `failed`.

### `GET /results`

List all completed analyses with preview text.

### `GET /results/{result_id}`

Get the full analysis text for a specific result.

---

## ⭐ Bonus Features

### 1. Queue Worker Model (Celery + Redis)

Handles concurrent analysis requests without blocking the API.

**Setup:**
```bash
# 1. Install and start Redis
# On macOS: brew install redis && redis-server
# On Ubuntu: sudo apt install redis-server && sudo service redis start
# On Windows: Download from https://github.com/microsoftarchive/redis/releases

# 2. Start the Celery worker
celery -A worker worker --loglevel=info --pool=solo

# 3. Submit async analysis
curl -X POST http://localhost:8000/analyze/async \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=Analyze this document"

# 4. Check job status
curl http://localhost:8000/status/{job_id}
```

**Architecture:**
- **Broker:** Redis receives job messages from the API
- **Worker:** Celery processes jobs asynchronously in the background
- **Status tracking:** Job progress stored in SQLite database
- **Benefits:** API remains responsive; multiple documents can be queued simultaneously

### 2. Database Integration (SQLAlchemy + SQLite)

All analysis results are automatically persisted to a SQLite database.

**Features:**
- Every analysis result is stored with file name, query, output, and timestamp
- Async job status tracking (`pending` → `processing` → `completed`/`failed`)
- RESTful endpoints to query historical results
- Zero-configuration — SQLite file is created automatically

**Endpoints:**
- `GET /results` — Browse all past analyses
- `GET /results/{id}` — Retrieve a specific analysis

---

## 📁 Project Structure

```
financial-document-analyzer-debug/
├── main.py              # FastAPI application with all endpoints
├── agents.py            # CrewAI agent definitions (4 specialized agents)
├── task.py              # CrewAI task definitions (4 analysis tasks)
├── tools.py             # Custom tools (PDF reader, search, data processing)
├── database.py          # SQLAlchemy models and database configuration
├── worker.py            # Celery worker for async processing
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
├── data/                # Directory for uploaded financial documents
│   └── TSLA-Q2-2025-Update.pdf  # Sample Tesla financial document
├── outputs/             # Directory for generated reports
└── README.md            # This file
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **AI Framework** | CrewAI 0.130.0 |
| **LLM** | Google Gemini 2.0 Flash |
| **Web Framework** | FastAPI |
| **PDF Processing** | LangChain + PyPDF |
| **Database** | SQLAlchemy + SQLite |
| **Queue** | Celery + Redis |
| **Search** | Serper.dev API |
