from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.llm_service import get_llm_service, LLMService
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse
from app.core.exceptions import LLMServiceError
from app.core.database import get_db
from app.repositories.conversation_repository import ConversationRepository

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Backend Lab",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    db: Session = Depends(get_db)
) -> ChatResponse:

    logger.info("Received chat request")

    try:
        response = llm_service.generate_response(
            request.message
        )

        repository = ConversationRepository(db)

        repository.save_conversation(
            user_message=request.message,
            assistant_response=response
        )

    except LLMServiceError:
        logger.error("LLMServiceError")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the response"
        )

    except Exception:
        logger.exception("Failed to persist conversation")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while saving the conversation"
        )

    logger.info("Generated response successfully")

    return ChatResponse(
        message=request.message,
        response=response
    )

@app.get("/conversations", response_model=list[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db)
) -> list[ConversationResponse]:
    repository = ConversationRepository(db)
    return repository.get_conversation()
    