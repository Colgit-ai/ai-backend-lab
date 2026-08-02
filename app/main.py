from fastapi import FastAPI
#FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
from pydantic import BaseModel
#Pydantic is the most widely used data, schema validation library for Python.
from app.services.llm_service import generate_response


app = FastAPI(
    title="AI Backend Lab",
    version="0.1.0",
)

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message:
        return {"error": "Message cannot be empty"}
    response = generate_response(request.message)
    print(f"Received message: {request.message}")
    return {
        "message": request.message,
        "response": response
    }

