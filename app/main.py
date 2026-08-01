from fastapi import FastAPI
#FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
from pydantic import BaseModel
#Pydantic is the most widely used data, schema validation library for Python.

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
    return {
        "message": request.message,
        "response": f"You said: {request.message}"
    }

