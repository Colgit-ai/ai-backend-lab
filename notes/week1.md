# AI Backend Lab

## Days 1-9 Engineering Notes

---

# Day 1 - FastAPI Fundamentals

## 1. What is FastAPI?

FastAPI is a modern Python web framework for building APIs.

Key characteristics:

* High performance
* Python type hints
* Automatic request validation
* Automatic OpenAPI documentation
* Swagger UI
* Dependency Injection
* Async support

Basic application:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}
```

Run:

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 2. HTTP Basics

### Common HTTP methods

```text
GET     → Retrieve data
POST    → Create/process data
PUT     → Replace data
PATCH   → Partially update data
DELETE  → Delete data
```

### HTTP status code categories

```text
2xx → Success
4xx → Client-side error
5xx → Server-side error
```

Examples:

```text
200 → OK
201 → Created
400 → Bad Request
401 → Unauthorized
403 → Forbidden
404 → Not Found
422 → Validation error
500 → Internal Server Error
```

---

## 3. Health endpoint

A health endpoint is useful to determine whether the application is running.

```python
@app.get("/health")
def health():
    return {"status": "healthy"}
```

Response:

```json
{
  "status": "healthy"
}
```

---

# Day 2 - LLM Integration

## 1. External LLM integration

The application integrates with Gemini through the Google GenAI SDK.

Architecture:

```text
FastAPI
   ↓
LLM Service
   ↓
Google GenAI SDK
   ↓
Gemini
```

The API endpoint should not contain the LLM implementation directly.

---

## 2. Environment variables

Secrets such as API keys should not be hardcoded.

Bad:

```python
api_key = "my-secret-key"
```

Better:

```text
LLM_API_KEY=...
```

stored in `.env`.

`.env` should never be committed.

`.gitignore` should contain:

```text
.env
.venv/
__pycache__/
.pytest_cache/
```

---

## 3. LLM service

The responsibility of the service is to communicate with the external LLM.

Conceptually:

```python
def generate_response(message: str):
    interaction = client.interactions.create(
        model=llm_model,
        input=message
    )

    return interaction.output_text
```

The route should call the service instead of directly calling Gemini.

---

## 4. Logging

Logging is preferable to `print()` because it provides:

* Log levels
* Filtering
* Better production support
* Structured application diagnostics

Important levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Example:

```python
logger = logging.getLogger(__name__)

logger.info("Chat request received")
logger.error("LLM request failed")
logger.exception("Unexpected LLM failure")
```

`logger.exception()` automatically includes the traceback when called inside an exception handler.

---

## 5. Don't log sensitive content unnecessarily

Avoid:

```python
logger.info(f"Generated response: {response}")
```

LLM responses may contain confidential information.

Prefer:

```python
logger.info("Chat response generated successfully")
```

---

# Day 3 - Pydantic Validation and Error Handling

## 1. Pydantic

Pydantic validates and structures Python data using type hints.

Example:

```python
class ChatRequest(BaseModel):
    message: str
```

FastAPI automatically uses this model to validate incoming JSON.

---

## 2. Field validation

We added:

```python
message: str = Field(
    min_length=1,
    max_length=1000
)
```

This gives the API a contract:

```text
minimum length → 1
maximum length → 1000
```

---

## 3. Custom validator

We used:

```python
@field_validator("message", mode="before")
@classmethod
def validate_message(cls, value):
```

Purpose:

* Validate the raw input
* Ensure message is a string
* Remove surrounding whitespace
* Reject whitespace-only messages

Example:

```python
value = value.strip()

if not value:
    raise ValueError(
        "Message cannot be empty or whitespace"
    )

return value
```

---

## 4. Don't raise HTTPException inside Pydantic validators

Bad architectural approach:

```python
raise HTTPException(...)
```

inside a Pydantic model.

Better:

```python
raise ValueError(...)
```

Pydantic converts the validation failure into FastAPI's validation response.

Why?

The schema should know about:

```text
Data validation
```

not:

```text
HTTP
```

---

## 5. Validation response

Invalid input produces:

```text
422 Unprocessable Entity
```

FastAPI returns structured validation details such as:

```json
{
  "detail": [
    {
      "type": "...",
      "loc": ["body", "message"],
      "msg": "...",
      "input": "..."
    }
  ]
}
```

---

## 6. Request vs Response schemas

Request:

```python
class ChatRequest(BaseModel):
    message: str
```

Response:

```python
class ChatResponse(BaseModel):
    message: str
    response: str
```

Request schema defines what the API accepts.

Response schema defines what the API returns.

---

## 7. `response_model`

Example:

```python
@app.post(
    "/chat",
    response_model=ChatResponse
)
```

Benefits:

* Validates outgoing data
* Controls response structure
* Helps prevent accidental fields from being exposed
* Generates API documentation
* Provides a clear API contract

---

# Day 4 - Automated Testing with pytest

## 1. Why automated tests?

Without tests:

```text
Change code
   ↓
Manually test everything
```

With tests:

```text
Change code
   ↓
pytest
   ↓
All tests execute automatically
```

---

## 2. Types of tests

### Unit test

Tests a small piece of functionality.

### Integration test

Tests multiple components working together.

### End-to-end test

Tests the entire system from beginning to end.

---

## 3. pytest

Run:

```bash
python -m pytest -v
```

`-v` means verbose output.

Using:

```bash
python -m pytest
```

ensures Python finds pytest from the current environment.

---

## 4. FastAPI TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)
```

Example:

```python
def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }
```

---

## 5. Tests implemented

We tested:

```text
Health endpoint
Empty message
Whitespace message
Missing message
Wrong datatype
Message too long
Valid chat
LLM failure
```

Total:

```text
8 tests
```

---

## 6. Mocking

External APIs should generally not be called during unit/API tests.

Instead:

```python
patch(...)
```

can replace the real implementation.

Example concept:

```text
Test
 ↓
Mock
 ↓
Fake LLM response
```

Benefits:

* Faster tests
* No API cost
* No dependency on network
* Predictable results
* Can simulate failures

---

# Day 5 - Configuration and Project Structure

## 1. Why separate configuration?

Initially configuration was handled using:

```python
os.getenv()
```

We moved to:

```python
pydantic-settings
```

because configuration should be:

* Centralized
* Validated
* Typed
* Loaded consistently
* Available through one settings object

---

## 2. BaseSettings

Example:

```python
class Settings(BaseSettings):
    llm_api_key: str
    llm_model: str = "gemini-3.6-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
```

---

## 3. Benefits of BaseSettings

Compared with `os.getenv()`:

```text
os.getenv()
    ↓
raw string
```

BaseSettings:

```text
Environment
    ↓
Validation
    ↓
Typed configuration
    ↓
Settings object
```

Missing required configuration causes the application to fail early.

This is preferable to discovering a missing configuration later during a request.

---

## 4. Project structure

We separated responsibilities:

```text
app/
├── core/
│   ├── config.py
│   └── exceptions.py
│
├── schemas/
│   └── chat.py
│
├── services/
│   └── llm_service.py
│
└── main.py
```

Responsibilities:

```text
main.py
    → HTTP/API layer

schemas/
    → Request/response contracts

services/
    → Business/external service logic

core/config.py
    → Configuration

core/exceptions.py
    → Application exceptions
```

---

# Day 6 - Service Boundaries and Dependency Injection

## 1. Service boundary

We wanted:

```text
main.py
    ↓
LLMService
    ↓
Gemini
```

The service should not know that FastAPI exists.

---

## 2. Why shouldn't the service raise HTTPException?

Bad:

```python
# llm_service.py
raise HTTPException(
    status_code=500
)
```

The service shouldn't know about HTTP.

A service could later be used by:

```text
FastAPI
CLI
Background worker
Scheduled job
Another application
```

Therefore it should raise an application-level exception.

---

## 3. Custom exception

```python
class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""
    pass
```

The exception contains no:

```text
HTTP status
FastAPI
HTTPException
```

It simply represents an LLM service failure.

---

## 4. Exception translation

Architecture:

```text
Gemini error
    ↓
LLMServiceError
    ↓
main.py
    ↓
HTTPException(500)
    ↓
Client
```

The API layer translates application errors into HTTP errors.

---

## 5. Exception chaining

We used:

```python
raise LLMServiceError(
    "Unable to generate response"
) from exc
```

`from exc` preserves the relationship between the new exception and the original exception.

Conceptually:

```text
Original exception
       ↓
    caused
       ↓
LLMServiceError
```

This helps debugging while allowing the service to expose a controlled application-level error.

---

## 6. LLMService class

We moved from a standalone function to:

```python
class LLMService:

    def generate_response(
        self,
        message: str
    ) -> str:
        ...
```

The service owns:

```text
Gemini client
LLM model
LLM interaction
LLM error handling
```

---

## 7. FastAPI Dependency Injection

Route:

```python
@app.post("/chat")
def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(
        get_llm_service
    )
):
```

`Depends()` tells FastAPI:

> Resolve this dependency and provide it to the route.

Flow:

```text
Request
   ↓
FastAPI
   ↓
get_llm_service()
   ↓
LLMService
   ↓
Route
```

---

## 8. Dependency Injection benefits

DI helps with:

* Separation of concerns
* Testability
* Replacing implementations
* Managing dependencies
* Cleaner route functions

---

## 9. Dependency overrides in tests

Production:

```text
get_llm_service()
    ↓
Real LLMService
    ↓
Gemini
```

Tests:

```text
get_llm_service()
    ↓
FakeLLMService
```

Using:

```python
app.dependency_overrides[
    get_llm_service
] = get_fake_llm_service
```

This avoids calling Gemini during tests.

---

## 10. DI vs patching

Earlier:

```python
patch(...)
```

replaced a method/function.

With dependency injection:

```text
Application dependency
        ↓
Replace dependency
        ↓
Fake implementation
```

When a dependency boundary already exists, dependency overrides are often cleaner than patching internals.

---

# Day 7 - Engineering Review and Documentation

## 1. README purpose

A README should allow someone to understand:

* What the project is
* Technology stack
* Architecture
* Project structure
* Setup
* Environment variables
* Running the application
* Testing
* API endpoints
* Roadmap

---

## 2. Architecture documentation

Current request flow:

```text
Client
   ↓
FastAPI
   ↓
Pydantic Schema
   ↓
LLMService
   ↓
Gemini API
   ↓
LLMService
   ↓
ChatResponse
   ↓
Client
```

Failure flow:

```text
Gemini
   ↓
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
```

---

## 3. Engineering review principles

Production code should avoid:

* Unused imports
* Commented-out old code
* Debug prints
* Excessive tutorial comments
* Logging sensitive information
* Duplicate logic

Comments should generally explain **why**, not explain obvious syntax.

---

## 4. README should not overclaim

Avoid claims like:

```text
Enterprise-grade AI platform
```

when the project is still a learning/engineering lab.

Describe what is actually implemented.

---

# Day 8 - PostgreSQL and SQLAlchemy

## 1. Why persistence?

Before PostgreSQL:

```text
Request
   ↓
Gemini
   ↓
Response
   ↓
Data disappears
```

With PostgreSQL:

```text
Request
   ↓
Gemini
   ↓
Response
   ↓
PostgreSQL
   ↓
Persistent data
```

---

## 2. PostgreSQL

PostgreSQL is the relational database used by the project.

It stores structured persistent data.

---

## 3. SQLAlchemy

SQLAlchemy is a Python SQL toolkit and ORM.

It allows Python applications to work with relational databases.

Architecture:

```text
Python
   ↓
SQLAlchemy
   ↓
psycopg
   ↓
PostgreSQL
```

---

## 4. psycopg

`psycopg` is the PostgreSQL driver.

It provides communication between Python/SQLAlchemy and PostgreSQL.

Conceptually:

```text
SQLAlchemy
   ↓
psycopg
   ↓
PostgreSQL
```

---

## 5. Engine

The SQLAlchemy Engine is the application's main database interface.

It manages database connectivity and connection pooling.

Example:

```python
engine = create_engine(
    settings.database_url,
    echo=True
)
```

---

## 6. Connection pool

Opening a new database connection for every operation can be expensive.

A connection pool allows connections to be reused.

Conceptually:

```text
Application
    ↓
Engine
    ↓
Connection Pool
    ↓
PostgreSQL
```

---

## 7. Session

A SQLAlchemy Session represents a unit of work with the database.

Operations include:

```text
add()
query/select()
commit()
rollback()
refresh()
```

A session should have a controlled lifecycle.

Don't create one global session and share it across requests.

---

## 8. Session factory

We created:

```python
SessionLocal = sessionmaker(
    bind=engine
)
```

`SessionLocal` is a factory for creating sessions.

It is not itself an active session.

---

## 9. DeclarativeBase

We created one shared base:

```python
class Base(DeclarativeBase):
    pass
```

All SQLAlchemy models should inherit from this same Base.

Why?

Because:

```python
Base.metadata
```

contains metadata about the application's ORM tables.

---

## 10. ORM model

We created:

```python
class Conversation(Base):
    __tablename__ = "conversations"
```

Fields:

```text
id
user_message
assistant_response
created_at
```

---

## 11. SQLAlchemy 2.x typed ORM

We use:

```python
Mapped
mapped_column
```

Example:

```python
id: Mapped[int] = mapped_column(
    primary_key=True
)
```

SQLAlchemy can infer the database type from the Python type annotation.

---

## 12. Text vs String

LLM responses can be large.

Instead of:

```python
String(1000)
```

we use:

```python
Text
```

for:

```text
user_message
assistant_response
```

API validation and database storage are separate concerns.

The API can limit incoming input while the database can support larger stored responses.

---

## 13. Timestamp

We use:

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
)
```

Important concepts:

* `datetime` → Python type
* `DateTime` → database type
* `timezone=True` → timezone-aware
* `func.now()` → database-generated timestamp

A consistent timestamp strategy is important in distributed/backend systems.

---

## 14. Nullability

Typed SQLAlchemy models can infer nullability.

For clarity we explicitly used:

```python
nullable=False
```

for required text fields.

Example:

```python
user_message: Mapped[str] = mapped_column(
    Text,
    nullable=False
)
```

---

## 15. Metadata vs actual database schema

Very important distinction:

```text
SQLAlchemy Model
      ↓
Base.metadata
```

does not automatically mean the physical PostgreSQL table exists.

There are two different things:

```text
SQLAlchemy metadata
        ≠
PostgreSQL schema
```

This leads to migrations.

---

## 16. Testing database connection

We tested SQLAlchemy with:

```python
from sqlalchemy import text

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT 1")
    )
    print(result.scalar())
```

Expected:

```text
1
```

SQLAlchemy 2.x uses `text()` for explicit textual SQL.

---

# Day 9 - Alembic Migrations

## 1. What is Alembic?

Alembic is a database migration tool commonly used with SQLAlchemy.

It provides version control for the database schema.

Conceptually:

```text
Migration 001
Create conversations

        ↓

Migration 002
Add user_id

        ↓

Migration 003
Add model_name
```

---

## 2. Why migrations?

Imagine development, staging, and production databases.

Manually changing each database is unsafe and difficult to reproduce.

Migrations provide a repeatable history of schema changes.

---

## 3. Alembic initialization

Command:

```bash
alembic init alembic
```

Generated:

```text
alembic/
├── versions/
├── env.py
├── script.py.mako
└── README

alembic.ini
```

---

## 4. Important Alembic files

### `alembic.ini`

General Alembic configuration.

### `alembic/env.py`

Controls how Alembic:

* Connects to the database
* Loads SQLAlchemy metadata
* Runs migrations

### `alembic/versions/`

Stores migration files.

---

## 5. `target_metadata`

We configured:

```python
target_metadata = Base.metadata
```

This tells Alembic:

> This is the SQLAlchemy metadata that represents our application's database models.

---

## 6. Why import models in `env.py`?

We imported:

```python
from app.models.conversation import Conversation
```

Even though the name may not appear to be directly used.

Importing the module executes:

```python
class Conversation(Base):
```

which registers the table with:

```python
Base.metadata
```

Therefore Alembic can detect the table during autogeneration.

---

## 7. Alembic and application settings

Instead of hardcoding the database URL in `alembic.ini`, we reuse:

```python
settings.database_url
```

Conceptually:

```text
.env
 ↓
Settings
 ↓
Alembic
 ↓
PostgreSQL
```

This avoids duplicating credentials/configuration.

---

## 8. Autogenerate

Command:

```bash
alembic revision --autogenerate \
    -m "create conversations table"
```

Alembic compares:

```text
SQLAlchemy metadata
        ↕
Current database schema
```

and generates a migration.

Important:

> Autogenerate is an assistant, not an oracle.

Generated migrations should always be reviewed.

---

## 9. Migration structure

Our first migration contained:

```python
def upgrade():
    op.create_table(...)
```

and:

```python
def downgrade():
    op.drop_table(...)
```

Meaning:

```text
upgrade()
    ↓
Move database schema forward

downgrade()
    ↓
Move database schema backward
```

---

## 10. Migration revision

Our first migration had:

```python
revision = "071baddba380"
down_revision = None
```

Because it is the first migration, there is no previous revision.

Later:

```text
071baddba380
      ↓
next_revision
      ↓
next_revision
```

Alembic maintains this migration chain.

---

## 11. `alembic upgrade head`

Command:

```bash
alembic upgrade head
```

Moves the database to the latest migration.

For a new database:

```text
Empty PostgreSQL database
        ↓
alembic upgrade head
        ↓
conversations table
        ↓
alembic_version table
```

---

## 12. `alembic downgrade -1`

Moves the database one migration backward.

Example:

```bash
alembic downgrade -1
```

Then:

```bash
alembic upgrade head
```

restores the latest schema.

---

## 13. `alembic current`

Shows the migration currently applied to the database.

```bash
alembic current
```

---

## 14. `alembic history`

Shows migration history.

```bash
alembic history
```

---

## 15. `alembic_version`

Alembic maintains a table called:

```text
alembic_version
```

This records the migration revision currently applied to the database.

---

# Current Architecture After Day 9

```text
                    Client
                       │
                       ▼
                  FastAPI
                       │
                 ChatRequest
                       │
                       ▼
                 LLMService
                       │
                       ▼
                    Gemini
                       │
                       ▼
                 ChatResponse
```

Database infrastructure:

```text
                 Application
                      │
                      ▼
                  SQLAlchemy
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
         Engine              Session
            │
            ▼
          psycopg
            │
            ▼
       PostgreSQL
```

Schema management:

```text
SQLAlchemy Models
       ↓
Base.metadata
       ↓
Alembic
       ↓
Migration files
       ↓
PostgreSQL schema
```

---

# Current Project Structure

```text
ai-backend-lab/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── alembic.ini
│
├── alembic/
│   ├── versions/
│   │   └── 071baddba380_*.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   └── conversation.py
│   │
│   ├── repositories/
│   │
│   ├── schemas/
│   │   └── chat.py
│   │
│   ├── services/
│   │   └── llm_service.py
│   │
│   └── main.py
│
├── tests/
│
└── notes/
```

---

# Important Architecture Principles Learned

## 1. Separation of concerns

Different layers have different responsibilities:

```text
API Layer
    ↓
Schemas
    ↓
Services
    ↓
Repositories
    ↓
Database
```

Don't put everything in `main.py`.

---

## 2. Dependency Inversion through DI

Instead of routes creating dependencies themselves:

```text
Route
  ↓
Create dependency
```

FastAPI provides them:

```text
FastAPI
  ↓
Dependency
  ↓
Route
```

This improves testability.

---

## 3. Framework boundaries

Lower-level services should not depend unnecessarily on higher-level frameworks.

Good:

```text
LLMService
    ↓
LLMServiceError
    ↓
FastAPI converts to HTTPException
```

Bad:

```text
LLMService
    ↓
HTTPException
```

---

## 4. External services should be isolated

Gemini interaction belongs in:

```text
services/llm_service.py
```

not directly inside the route.

This makes the application easier to:

* Test
* Change
* Extend
* Maintain

---

## 5. Configuration should be centralized

Instead of:

```text
os.getenv()
os.getenv()
os.getenv()
```

throughout the application:

```text
.env
 ↓
Settings
 ↓
Application
```

One source of configuration.

---

## 6. Database sessions need lifecycle management

Never treat a SQLAlchemy Session as a permanent global object.

Correct conceptual lifecycle:

```text
Request
   ↓
Create Session
   ↓
Use Session
   ↓
Commit/Rollback
   ↓
Close Session
```

---

## 7. Migrations are version control for database schema

Code changes:

```text
Git
```

Database schema changes:

```text
Alembic
```

Both provide reproducible history.

---

# Useful Commands

## Python environment

```bash
python3 --version

python3 -m venv .venv

source .venv/bin/activate

deactivate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

---

## Run tests

```bash
python -m pytest -v
```

---

## Git

```bash
git status

git add .

git diff --staged

git commit -m "message"

git push
```

---

## PostgreSQL

```bash
psql postgres
```

```bash
psql ai_backend_lab
```

Inside PostgreSQL:

```sql
\l
```

List databases.

```sql
\dt
```

List tables.

```sql
\d conversations
```

Describe a table.

```sql
SELECT * FROM conversations;
```

Exit:

```sql
\q
```

---

## Alembic

```bash
alembic current
```

```bash
alembic history
```

```bash
alembic revision --autogenerate -m "message"
```

```bash
alembic upgrade head
```

```bash
alembic downgrade -1
```

---

# Key Interview Questions

## FastAPI

### Why FastAPI?

Because it provides:

* Type-hint-based validation
* Automatic OpenAPI documentation
* Dependency Injection
* High performance
* Async support

### What is `response_model`?

Defines and validates the response schema and controls the API response contract.

### Why use Pydantic?

For validation, serialization, and structured data contracts.

---

## Architecture

### Why separate service and API layers?

To separate HTTP concerns from application/external-service logic.

### Why shouldn't a service raise HTTPException?

Because HTTP is an API-layer concern. The service may be reused outside HTTP.

### What is dependency injection?

Providing an object's dependencies externally rather than having the object create them itself.

### Why is DI useful for testing?

Real dependencies can be replaced with fake implementations.

---

## SQLAlchemy

### What is SQLAlchemy?

A Python SQL toolkit and ORM.

### What is psycopg?

A PostgreSQL database driver.

### What is an Engine?

The main SQLAlchemy interface for database connectivity and connection pooling.

### What is a Session?

A unit of work used to interact with the database.

### Engine vs Session?

```text
Engine
→ Database connectivity / connection pool

Session
→ Application database unit of work
```

### Why shouldn't we use one global Session?

Sessions have state and transaction lifecycle and should not be shared indiscriminately across concurrent requests.

---

## Alembic

### Why use Alembic?

To version and safely evolve the database schema.

### What does `--autogenerate` do?

Compares SQLAlchemy metadata with the database schema and generates a candidate migration.

### Is autogenerate always correct?

No. Generated migrations must be reviewed.

### What is `target_metadata`?

The SQLAlchemy metadata Alembic uses for schema comparison/autogeneration.

### What is `alembic_version`?

The database table that tracks the currently applied migration revision.

---

# Current Learning Progress

```text
Day 1
FastAPI fundamentals
        ↓
Day 2
LLM integration
        ↓
Day 3
Pydantic + validation + errors
        ↓
Day 4
pytest + mocking
        ↓
Day 5
Configuration + project structure
        ↓
Day 6
Service boundaries + DI
        ↓
Day 7
Documentation + engineering review
        ↓
Day 8
PostgreSQL + SQLAlchemy
        ↓
Day 9
Alembic migrations
        ↓
Day 10
Repository + persistence  ← NEXT
```

---

# Day 10 Preview

The next architecture will be:

```text
Client
   │
   ▼
FastAPI
   │
   ├───────────────┐
   ▼               ▼
LLMService       get_db()
   │               │
   ▼               ▼
 Gemini          Session
                   │
                   ▼
             ConversationRepository
                   │
                   ▼
              PostgreSQL
```

The next concepts:

* `get_db()`
* `yield` dependencies
* Session lifecycle
* Repository Pattern
* `add()`
* `commit()`
* `refresh()`
* Database persistence
* Database dependency overrides in tests
* Transaction handling
* Saving conversations

The goal is to transform the application from a stateless LLM API into a stateful backend that can persist conversation data.
