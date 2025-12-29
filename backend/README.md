# AI-Powered Lead Management System Backend

This repository contains the backend for an AI-powered lead management system, built for a hackathon. The system analyzes new leads using the BANT framework, enriches their data, assigns a dynamic score, and routes them to the appropriate team.

## Features

- **AI-Powered BANT Analysis**: Uses Google's Gemini Pro to analyze a lead's notes for **B**udget, **A**uthority, **N**eed, and **T**imeline.
- **Dynamic Lead Scoring**: Assigns a numeric score (0-100), a category (**Hot**, **Warm**, **Cold**), and provides a human-readable AI-generated explanation.
- **Data Enrichment**: Includes a modular service to validate emails and enrich company data (currently uses mock data).
- **Configurable Lead Routing**: Automatically routes leads to **Sales**, **Presales**, or **Nurture** queues based on their score.
- **API-First Design**: A clean REST API built with Python and FastAPI for easy integration with any frontend.
- **Scalable Architecture**: Built with a modular service-oriented architecture that is easy to maintain and extend.

## Architecture

The backend follows a clean, service-oriented architecture:

- `main.py`: The main FastAPI application entry point.
- `config.py`: Manages environment variables and settings using Pydantic.
- `api/leads.py`: Defines the main API endpoint for lead analysis.
- `models/lead.py`: Contains all Pydantic data models, defining the API contracts.
- `services/`: Contains the core business logic, separated into:
    - `ai_scoring.py`: Interacts with the Gemini API to analyze and score leads.
    - `enrichment.py`: A modular service for validating and enriching lead data.
    - `routing.py`: Implements the logic for routing leads to queues.
- `utils/gemini_client.py`: A client to encapsulate all communication with the Gemini API.

## API Documentation

### Analyze Lead

Submits a new lead for analysis, scoring, and routing.

- **Endpoint**: `POST /api/v1/analyze`
- **Request Body**:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@startup.io",
  "company_name": "Innovative Startup LLC",
  "notes": "We've just secured our Series A funding and have a budget of around $50,000 for a new CRM. I'm the Head of Operations and I need to find a solution we can implement by the end of next quarter."
}
```

- **Success Response (200 OK)**:

```json
{
  "lead_input": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@startup.io",
    "company_name": "Innovative Startup LLC",
    "notes": "We've just secured our Series A funding and have a budget of around $50,000 for a new CRM. I'm the Head of Operations and I need to find a solution we can implement by the end of next quarter."
  },
  "bant_analysis": {
    "budget": "The lead has explicitly mentioned a budget of around $50,000.",
    "authority": "The lead is the 'Head of Operations', indicating strong authority or decision-making power.",
    "need": "There is a clear need for a new CRM system.",
    "timeline": "The lead has a specific timeline: 'by the end of next quarter'."
  },
  "enrichment_data": {
    "company_info": {
      "company_name": "Startup LLC",
      "industry": "Software",
      "size": "11-50 employees",
      "website": "www.startup.io"
    },
    "email_valid": true
  },
  "lead_score": {
    "score": 95,
    "category": "Hot",
    "explanation": "This is a very strong lead with a clear budget, authority, need, and timeline."
  },
  "routing_decision": {
    "queue": "Sales",
    "reason": "Lead is Hot with a score of 95. Assigned directly to sales team."
  }
}
```

## How to Run Locally (macOS)

### 1. Prerequisites

- Python 3.8+
- An API key for Google Gemini.

### 2. Setup

**Clone the repository and navigate to the `backend` directory.**

**Create and activate a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Install the required dependencies:**

```bash
pip install -r requirements.txt
```

**Configure your environment variables:**

Create a `.env` file in the `backend` directory by copying the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual Gemini API key.

```
# .env
GOOGLE_API_KEY="AIzaxxxxxxxxxxxxxxxxxxxxx"
```

### 3. Run the Application

With your virtual environment active and the `.env` file configured, run the application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://127.0.0.1:8000`. You can access the interactive API documentation (powered by Swagger UI) at `http://127.0.0.1:8000/docs`.

## Logic Explained

### Lead Scoring

The lead score is a combination of AI-driven analysis and deterministic rules:

1.  **AI Analysis**: The lead's notes are sent to Gemini, which provides a BANT analysis and a preliminary score (0-100) based on its interpretation.
2.  **Deterministic Adjustments**: The application can apply its own rules. For example, in the current implementation, leads from companies with "Big Corp" in their name get a small +5 point boost.
3.  **Final Score**: The final score is clamped between 0 and 100.

### Lead Routing

Routing is based on simple, configurable score thresholds:

- **Hot (Score >= 85)**: Routed to the `Sales` queue for immediate follow-up.
- **Warm (Score >= 60)**: Routed to the `Presales` queue for more technical qualification.
- **Cold (Score < 60)**: Routed to the `Nurture` queue to be included in marketing campaigns.

These thresholds are defined in `app/services/routing.py` and can be easily externalized to `app/config.py` to be controlled via environment variables.

## Post-Hackathon Extensibility

This project is built to be easily extended:

- **Plugging in Real Enrichment**: The `EnrichmentService` in `app/services/enrichment.py` is a placeholder. To use a real service like Clearbit or Hunter.io, you would simply update the `_validate_email` and `_enrich_company_info` methods to call the third-party API. No other code changes would be needed.
- **Adding More Routing Rules**: The `RoutingService` can be expanded with more complex logic, such as routing based on industry, company size, or geographic location.
- **Improving the AI Prompt**: The prompt sent to Gemini in `ai_scoring.py` can be further refined to improve the accuracy and consistency of the AI's analysis.
- **Asynchronous Processing**: For high-volume applications, the lead analysis process could be moved to a background task using a job queue like Celery or ARQ to avoid blocking the API response.
