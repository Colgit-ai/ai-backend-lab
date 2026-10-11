from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions import LLMServiceError
from app.services.llm_service import LLMService, get_llm_service

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_empty_message():
    response = client.post(
        "/chat",
        json={"message": ""}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Message cannot be empty or whitespace"

def test_whitespace_message():
    response = client.post(
        "/chat",
        json={"message":"       "}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Message cannot be empty or whitespace"

def test_missing_message():
    response = client.post(
        "/chat",
        json={}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"

def test_wrong_datatype():
    response = client.post(
        "/chat",
        json={"message": 123211}
    )   
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Message must be a string"

def test_message_too_long():
    response = client.post(
        "/chat",
        json={"message": "a" * 1001}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at most 1000 characters"

class FakeLLMService:
    def generate_response(self, message: str) -> str:
        return "This is a mocked response"

def get_fake_llm_service() -> FakeLLMService:
    return FakeLLMService()

def test_valid_chat():
    #mock the generate_response function to return a specific response. This allows you to test the /chat endpoint without actually calling the LLM service.
    
    app.dependency_overrides[get_llm_service] = get_fake_llm_service

    response = client.post(
        "/chat",
        json={"message": "What is Redis?"}
    )

    app.dependency_overrides = {}  # Reset dependency overrides after the test
    assert response.status_code == 200
    assert response.json() == {
        "message": "What is Redis?",
        "response": "This is a mocked response"
    }

class FailingLLMService:
    def generate_response(self, message: str) -> str:
        raise LLMServiceError("Unable to generate response")

def get_failing_llm_service() -> FailingLLMService:
    return FailingLLMService()

def test_llm_failure():
    #mock the generate_response function to raise an LLMServiceError with a 500 status code and a specific detail message. This simulates a failure in the LLM service.
    
    app.dependency_overrides[get_llm_service] = get_failing_llm_service
    response = client.post(
        "/chat",
        json={"message": "What is Redis?"}
    )   
    app.dependency_overrides = {}  # Reset dependency overrides after the test
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred while generating the response"