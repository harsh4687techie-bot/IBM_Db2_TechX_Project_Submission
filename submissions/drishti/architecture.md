# DRISHTI — System Architecture

## 1. Architecture Overview

DRISHTI follows a frontend-backend-database architecture with AI-assisted analytical capabilities.

```text
                USER
                  |
                  v
       React + TypeScript Frontend
                  |
             REST API
                  |
                  v
          Python FastAPI Backend
                  |
       +----------+-----------+
       |          |           |
       v          v           v
   Data       Financial     AI Agent
 Ingestion    Analysis      Workflow
       |          |           |
       +----------+-----------+
                  |
                  v
             IBM Db2
                  |
                  v
       Analytical Results
                  |
                  v
          Dashboard & Reports
```

## 2. Frontend Layer

**Technologies:** React, TypeScript, Vite.

Responsibilities:
- Provide the interactive dashboard.
- Support financial dataset uploads.
- Display volume and sector analysis.
- Visualize anomaly detection results.
- Provide the AI Copilot interface.
- Display reports and database status.

## 3. Backend Layer

**Technology:** Python with FastAPI.

Responsibilities:
- Expose REST API endpoints.
- Process uploaded financial datasets.
- Validate and prepare data.
- Coordinate financial analysis workflows.
- Connect application services with IBM Db2.
- Provide analytical results to the frontend.

## 4. Database Layer

**Database:** IBM Db2.

Responsibilities:
- Store and retrieve structured financial information.
- Support application data operations.
- Provide database-backed analytical workflows.
- Maintain persistent application data where configured.

## 5. AI Intelligence Layer

The AI layer supports conversational interaction and analytical assistance.

Intended workflow:
1. Receive a user query.
2. Identify the relevant analytical context.
3. Access the appropriate application capabilities.
4. Process the available information.
5. Return an understandable response.

The specific agent framework, model provider and tool-calling implementation must match the actual backend source code.

## 6. Data Flow

1. The user uploads a financial dataset through the frontend.
2. The backend receives and validates the uploaded data.
3. Financial records are prepared for analysis.
4. IBM Db2 provides the configured data storage and retrieval layer.
5. Analytical services calculate volume and sector insights.
6. Anomaly detection identifies unusual activity.
7. AI-assisted workflows provide contextual explanations.
8. Results are presented through the dashboard and reporting interface.

## 7. Security Considerations

- Store credentials in environment variables.
- Never commit real API keys or database passwords.
- Validate uploaded files and input data.
- Avoid exposing sensitive database connection details.
- Use appropriate access controls and secure deployment configuration.

## 8. Deployment Architecture

The frontend and backend can run as separate services during development.

- Frontend: Vite development server.
- Backend: FastAPI application served through Uvicorn.
- Database: IBM Db2 instance.

Production deployment requires suitable environment configuration, network security and service hosting.

## 9. Future Improvements

- Expanded monitoring and observability.
- More advanced financial intelligence.
- Improved AI explainability.
- Additional data integrations.
- Production deployment automation.