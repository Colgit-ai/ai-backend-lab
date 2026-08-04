from fastapi import FastAPI, Depends, HTTPException
from app.services.llm_service import get_llm_service, LLMService
import logging 
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.exceptions import LLMServiceError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Backend Lab",
    version="0.1.0",
)

# 4xx → Client caused the problem
# 5xx → Server caused the problem

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
): 
    logger.info("Received chat request")

    try:
        response = llm_service.generate_response(request.message)
    
    except LLMServiceError:
        logger.exception("Failed to generate response from LLM service")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate response"
        )

    logger.info("Generated response Successfully")
    return ChatResponse(
        message=request.message, 
        response=response
    )

