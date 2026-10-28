
from fastapi.testclient import TestClient

from app.core.exceptions import LLMServiceError
from app.main import app
from app.services.llm_service import get_llm_service

client = TestClient(app, raise_server_exceptions=False)


class FailingLLMService:
    def generate_response(self, message: str):
        raise LLMServiceError(
            "Internal provider details must not leak"
        )


def test_llm_failure_returns_safe_error():
    app.dependency_overrides[get_llm_service] = (
        lambda: FailingLLMService()
    )

    try:
        response = client.post(
            "/chat",
            json={"message": "Hello"},
        )

        assert response.status_code == 500
        assert response.json() == {
            "error": {
                "code": "LLM_SERVICE_ERROR",
                "message": (
                    "An error occurred while generating the response"
                ),
            }
        }
        assert "Internal provider details" not in response.text
    finally:
        app.dependency_overrides.clear()


def test_invalid_request_uses_standard_error_format():
    response = client.post("/chat", json={})

    assert response.status_code == 422

    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == (
        "The request contains invalid data."
    )
    assert "details" in body["error"]
    assert isinstance(body["error"]["details"], list)


def test_missing_route_uses_standard_error_format():
    response = client.get("/route-that-does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "The requested resource was not found.",
        }
    }
