
import logging
from uuid import uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import HTTPException
from app.core.database import get_db
from app.core.exceptions import LLMServiceError
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMService, get_llm_service
from app.api.auth import router as auth_router
from app.api.dependencies import get_current_user
from app.models.user import User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Backend Lab", version="0.1.0")
app.include_router(auth_router)

def error_response(
    code: str,
    message: str,
    status_code: int,
    details: list[dict] | None = None,
) -> JSONResponse:
    error = {
        "code": code,
        "message": message,
    }

    if details is not None:
        error["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={"error": error},
    )


@app.exception_handler(LLMServiceError)
async def llm_error_handler(
    request: Request,
    exc: LLMServiceError,
) -> JSONResponse:
    logger.error("LLM provider failure: %s", type(exc).__name__)

    return error_response(
        code="LLM_SERVICE_ERROR",
        message="An error occurred while generating the response",
        status_code=500,
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception("Database operation failed")

    return error_response(
        code="DATABASE_ERROR",
        message="An error occurred while accessing stored data.",
        status_code=500,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    safe_errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]

    return error_response(
        code="VALIDATION_ERROR",
        message="The request contains invalid data.",
        status_code=422,
        details=safe_errors,
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if exc.status_code == 404:
        code = "NOT_FOUND"
        message = "The requested resource was not found."
    elif exc.status_code == 401:
        code = "UNAUTHORIZED"
        message = "Authentication is required."
    elif exc.status_code == 403:
        code = "FORBIDDEN"
        message = "You do not have permission to access this resource."
    else:
        code = "HTTP_ERROR"
        message = "The request could not be completed."

    return error_response(
        code=code,
        message=message,
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unexpected application error")

    return error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred.",
        status_code=500,
    )


@app.get("/health")
def health():
    return {"status": "healthy"}



@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    logger.info("Received chat request for authenticated user")

    repository = ConversationRepository(db)
    conversation_id = request.conversation_id or str(uuid4())

    # If the client supplies an ID, it must belong to this user.
    if request.conversation_id:
        history = repository.get_conversation_history(
            conversation_id=conversation_id,
            user_id=current_user.id,
            limit=10,
        )
        if not history:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )
    else:
        history = []

    formatted_history = [
        {
            "user_message": turn.user_message,
            "assistant_response": turn.assistant_response,
        }
        for turn in history
    ]

    response = llm_service.generate_response(
        message=request.message,
        history=formatted_history,
    )

    conversation_service = ConversationService(db)
    conversation_service.save_conversation(
        user_message=request.message,
        assistant_response=response,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return ChatResponse(
        message=request.message,
        response=response,
        conversation_id=conversation_id,
    )


@app.get("/conversations")
def list_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = ConversationRepository(db)
    return repository.get_conversation(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = ConversationRepository(db)
    conversation = repository.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@app.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)
    deleted_count = conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id,
        "deleted_turns": deleted_count,
    }
