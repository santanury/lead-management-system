# 🎯 Lead Management System (AI Qualifier)

> An AI-powered Lead Management System designed to qualify, score, and enrich leads in real-time using Agentic AI workflows.

![AI Powered](https://img.shields.io/badge/AI-Powered-purple) ![Status](https://img.shields.io/badge/Status-Prototype-green) ![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%20%7C%20Gemini-blue)

## 🚀 Overview

This project is a functional MVP demonstrating **AI Readiness** in CRM workflows. It moves beyond simple data entry by acting as an intelligent agent that:

1.  **Enriches** incoming leads with real-time company data (using Google Search & Clearbit/Google Favicons).
2.  **Qualifies** leads using a Multi-Factor Scoring Model (BANT, Authority, Intent, Risks).
3.  **Reasons** about the lead's potential and generates strategic, context-aware follow-up questions for sales agents.

## ✨ Key Features

- **🤖 Agentic Lead Scoring**: Uses **Google Gemini 2.5** to analyze lead notes and emails against a strict scoring framework.
- **🌍 Live Enrichment**: Automatically fetches company size, industry, and logos using a custom **Web-RAG** implementation (Google Search Tool).
- **📊 Visual Dashboard**: A modern, dark-mode capability dashboard built with **Next.js** and **Tailwind CSS**.
- **🛡️ Verification Guardrails**: Detects impersonation risks and verifies authority tiers (e.g., matching "Delivery Head" to company size).
- **🖼️ Visual Assets**: Auto-fetches company logos via Google Favicons Service (`www.google.com/s2/favicons`).
- **🔗 n8n Integration**: Built-in **Webhook Support** to trigger external workflows (e.g., email alerts, CRM sync) automatically upon lead analysis.

## 🛠️ Tech Stack

### Backend

- **Framework**: FastAPI (Python)
- **AI/LLM**: Google Generative AI (Gemini Pro) via `google-generativeai`
- **Database**: PostgreSQL (via `sqlmodel` and `psycopg2-binary`)
- **Validation**: Pydantic v2
- **Server**: Uvicorn
- **Key Modules**:
  - `app/api`: REST Endpoints.
  - `app/services`: Business logic for AI Scoring (`ai_scoring.py`), Routing (`routing.py`), and Enrichment.
  - `app/models`: Pydantic data models.

### Frontend

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS v4
- **UI Components**: Shadcn/UI (based on Radix UI)
- **State Management**: Redux Toolkit (and React Context)
- **Icons**: Lucide React
- **Charts**: Recharts
- **HTTP Client**: Axios

## 🏁 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Google Cloud API Key (with Gemini & Search enabled)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GOOGLE_API_KEY and DATABASE_URL in .env

# Run Server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install

# Run Development Server
npm run dev
```

The app will be available at `http://localhost:3000`.

## 🧠 AI Architecture

1.  **Ingestion**: Lead data is received via API.
2.  **Enrichment Agent**:
    - Extracts domain from email.
    - Uses **Google Search Tool** to find company details (Industry, Size).
    - Fetches logo via Google Favicons.
3.  **Scoring Agent**:
    - Constructs a reasoning prompt with the enriched context.
    - Evaluates BANT (Budget, Authority, Need, Timeline).
    - Calculates a weighted score (0-100).
    - Generates JSON output with specific risk flags and follow-up questions.

## 🤝 Contribution

This project is part of an internal AI Hackathon. Contributions to improve the scoring logic or add new integrations are welcome!

## 📄 License

MIT
