from fastapi import FastAPI, HTTPException
#FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
from pydantic import BaseModel, Field, ConfigDict, field_validator
#Pydantic is the most widely used data, schema validation library for Python.
from app.services.llm_service import generate_response
import logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Backend Lab",
    version="0.1.0",
)

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1, 
        max_length=1000, 
        description="The message to send to the LLM service"
    )

    @field_validator("message", mode="before")
    @classmethod
    def validate_message(cls, value: str):

        if not isinstance(value, str):
            logger.warning("Message must be a string")
            #Don't raise HTTPException inside Pydantic validators
            raise ValueError("Message must be a string") 

        if not value.strip():
            logger.error("Message cannot be empty or whitespace")
            raise ValueError("Message cannot be empty or whitespace")
        return value.strip()


# 4xx → Client caused the problem
# 5xx → Server caused the problem

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
def chat(request: ChatRequest):
    logger.info("Received chat request")
    response = generate_response(request.message)
    logger.info(f"Generated response: {response}")
    return {
        "message": request.message,
        "response": response
    }

