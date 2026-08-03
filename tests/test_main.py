from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from fastapi import HTTPException

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

def test_valid_chat():
    #mock the generate_response function to return a specific response. This allows you to test the /chat endpoint without actually calling the LLM service.
    with patch(
        "app.main.generate_response",
        return_value="This is a mocked response"
    ):
        response = client.post(
            "/chat",
            json={"message": "What is Redis?"}
        )

    assert response.status_code == 200
    assert response.json() == {
        "message": "What is Redis?",
        "response": "This is a mocked response"
    }

def test_llm_failure():
    #mock the generate_response function to raise an HTTPException with a 500 status code and a specific detail message. This simulates a failure in the LLM service.
    with patch(
        "app.main.generate_response",
        side_effect=HTTPException(status_code=500, detail="Unable to generate response")
    ):
        response = client.post(
            "/chat",
            json={"message": "What is Redis?"}
        )   
    assert response.status_code == 500
    assert response.json()["detail"] == "Unable to generate response"