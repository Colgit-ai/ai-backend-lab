# AI Backend Lab

Production-oriented backend application for experimenting
with LLM integrations and modern backend engineering.

## Features

- FastAPI REST API
- Gemini LLM integration
- Pydantic request validation
- Environment-based configuration
- Service-layer architecture
- Dependency injection
- Custom exception handling
- Automated API testing
- Mocked external dependencies

## Architecture

Client
  ↓
FastAPI
  ↓
Pydantic Schema
  ↓
LLMService
  ↓
Gemini API

## Project Structure

app/
├── core/
├── schemas/
├── services/
└── main.py

tests/
notes/

## Setup

1. Clone repository
```git clone <repository-url>```
```cd ai-backend-lab```
```python -m venv .venv```
2. Create virtual environment
Windows
```.venv\Scripts\activate```
3. Install dependencies
```pip install -r requirements.txt```
4. Configure environment variables
## Environment Variables
LLM_API_KEY=
LLM_MODEL="Gemini 3.6 flash"
5. Start application
## Running
```uvicorn app.main:app --reload```

## API Documentation

/docs

## Testing

```python -m pytest -v```

## Current API

| Method | Endpoint  | Purpose                  |
| ------ | --------- | ------------------------ |
| GET    | `/health` | Check API health         |
| POST   | `/chat`   | Generate an LLM response |

## Roadmap

- PostgreSQL persistence
- Conversation history
- Redis caching
- Authentication
- Docker
- RAG
- Observability
- Agentic workflows


## Architecture
 ┌──────────────┐
 │    Client    │
 └──────┬───────┘
        │
  POST /chat
        │
        ▼
 ┌──────────────┐
 │   FastAPI    │
 │   main.py    │
 └──────┬───────┘
        │
   ChatRequest
        │
        ▼
 ┌──────────────┐
 │  LLMService  │
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │    Gemini    │
 └──────┬───────┘
        │
     response
        │
        ▼
  ChatResponse
        │
        ▼
      Client

## Failure-Path

Gemini
   │   │
Exception
   ↓
LLMService
   ↓
LLMServiceError
   ↓
main.py
   ↓
HTTPException
   ↓
HTTP 500

## Tech Stack

- Python
- FastAPI
- Pydantic
- Gemini
- pytest