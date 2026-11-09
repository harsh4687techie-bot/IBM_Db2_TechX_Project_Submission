# DRISHTI — See Beyond Data

**An Agentic Data Intelligence Platform powered by IBM Db2**

DRISHTI transforms financial market volume data into meaningful intelligence through data processing, anomaly detection, sector analysis and AI-assisted insights.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [IBM Db2 Integration](#ibm-db2-integration)
4. [AI Architecture](#ai--llm-architecture)
5. [Technology Stack](#technology-stack)
6. [Prerequisites](#prerequisites)
7. [Setup and Installation](#setup--installation)
8. [Configuration](#configuration)
9. [Running the Project](#running-the-project)
10. [Testing and Verification](#testing--verification)
11. [Screenshots](#screenshots)
12. [Limitations and Future Roadmap](#known-limitations--future-roadmap)
13. [Team and Credits](#team-members--credits)

## Problem Statement

Financial market data is often distributed across spreadsheets and datasets, making it difficult to identify unusual trading activity, understand sector-level movements and generate actionable insights.

Manual analysis can be time-consuming and may overlook important patterns.

DRISHTI addresses these challenges by providing an integrated platform for financial data ingestion, analysis, anomaly detection and AI-assisted interpretation.

## Solution Overview

DRISHTI is an intelligent financial data analysis platform that combines backend processing, IBM Db2 data management and an interactive dashboard.

### Key Features

- **Data Ingestion:** Upload and process financial datasets.
- **Data Validation:** Validate records and handle duplicate entries.
- **Volume Intelligence:** Analyse daily, weekly and monthly stock volume trends.
- **Anomaly Detection:** Identify unusual volume movements and patterns.
- **Sector Intelligence:** Compare stock activity across sectors.
- **AI Copilot:** Generate conversational assistance and analytical insights.
- **Reports and History:** Access analysis results and generated reports.
- **Db2 Status:** Monitor database connectivity through the application.

## IBM Db2 Integration

IBM Db2 is the relational database component of DRISHTI.

It supports structured financial data storage and retrieval for the platform's analytical workflows.

The integration covers:

- Database connectivity and configuration.
- Structured financial data management.
- Data retrieval for analytical operations.
- Database-backed application workflows.
- Connectivity status monitoring.

**Database configuration:** See `.env.example` for the configuration template.

*The exact Db2 edition, Python driver and implemented schema details should be documented from the actual backend implementation.*

## AI / LLM Architecture

DRISHTI incorporates an agentic AI workflow to support financial data analysis and conversational insights.

The platform is designed around:

- Financial data analysis.
- Anomaly interpretation.
- Sector-level intelligence.
- AI-assisted question answering.
- Contextual analytical responses.

The AI orchestration framework and model provider should be identified from the actual backend dependencies and configuration before final submission.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Database | IBM Db2 |
| Visualization | Recharts |
| AI | Agentic AI integration |
| API | REST API |

## Prerequisites

- Python 3.10 or later.
- Node.js and npm.
- IBM Db2 instance.
- Git.
- Required AI provider API key, if applicable.

## Setup & Installation

Clone the repository:

```bash
git clone https://github.com/harsh4687techie-bot/IBM_Db2_TechX_Project_Submission.git
```

Navigate to the project:

```bash
cd IBM_Db2_TechX_Project_Submission/submissions/drishti
```

### Backend Setup

```bash
cd src
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies listed in the project's dependency file once added.

### Frontend Setup

Open another terminal:

```bash
cd submissions/drishti/src/frontend
npm install
```

## Configuration

Use `.env.example` as the configuration reference.

1. Configure the IBM Db2 connection.
2. Add the required AI provider credentials.
3. Configure the backend host and port.
4. Keep actual credentials in a local `.env` file.
5. Never commit passwords, API keys or private credentials.

## Running Project

### Start Backend

From the `submissions/drishti/src` directory:

```bash
python -m uvicorn backend.main:app --reload
```

### Start Frontend

From `submissions/drishti/src/frontend`:

```bash
npm run dev
```

Open the local frontend URL displayed by Vite in your browser.

## Testing & Verification

The project contains backend test modules covering areas such as:

- Financial calculation logic.
- Data ingestion edge cases.
- API endpoints.
- Report exports.
- Security checks.
- Startup and API behaviour.
- Path portability.

Run the backend tests from the appropriate project directory:

```bash
pytest backend/tests
```

Additional test files are located in the backend source directory.

## Screenshots

Project screenshots are available in:

`docs/screenshots/`

They demonstrate the dashboard, volume intelligence, anomaly detection, sector analysis, AI copilot, reports, data ingestion and responsive layouts.

## Known Limitations & Future Roadmap

Potential future improvements include:

- Integration with additional financial data sources.
- Expanded financial forecasting capabilities.
- More advanced anomaly detection.
- Improved explainability of AI-generated insights.
- Additional reporting and visualization capabilities.
- Enhanced deployment and monitoring support.

## Team Members & Credits

**Project:** DRISHTI — See Beyond Data

**Developer:** Harshvardhan Shinde

**GitHub:** [harsh4687techie-bot](https://github.com/harsh4687techie-bot)

**Submission Repository:** [IBM Db2 TechX Project Submission](https://github.com/harsh4687techie-bot/IBM_Db2_TechX_Project_Submission)

Built for the IBM Db2 TechX competition.