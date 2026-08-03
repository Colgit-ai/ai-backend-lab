from fastapi import FastAPI
from app.services.llm_service import generate_response
import logging 
from app.schemas.chat import ChatRequest, ChatResponse

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
def chat(request: ChatRequest)-> ChatResponse: 
    logger.info("Received chat request")

    response = generate_response(request.message)

    logger.info("Generated response Successfully")
    return ChatResponse(
        message=request.message, 
        response=response
    )

