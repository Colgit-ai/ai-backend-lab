from unittest.mock import MagicMock, patch

import pytest

from app.models.conversation import Conversation
from app.services.conversation_service import ConversationService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    with patch(
        "app.services.conversation_service.ConversationRepository"
    ) as mock_repository_class:
        mock_repository = mock_repository_class.return_value
        instance = ConversationService(mock_db)
        yield instance, mock_repository


def test_save_conversation_commits_on_success(mock_db, service):
    instance, mock_repository = service

    expected = Conversation(
        user_message="What is Redis?",
        assistant_response="Redis is an in-memory data store.",
    )
    mock_repository.save_conversation.return_value = expected

    result = instance.save_conversation(
        user_message="What is Redis?",
        assistant_response="Redis is an in-memory data store.",
    )

    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()
    assert result is expected


def test_save_conversation_rolls_back_on_failure(mock_db, service):
    instance, mock_repository = service

    mock_repository.save_conversation.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        instance.save_conversation(
            user_message="Hello",
            assistant_response="Hi there!",
        )

    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()


def test_commit_failure_triggers_rollback(mock_db, service):
    instance, mock_repository = service

    mock_repository.save_conversation.return_value = Conversation(
        user_message="Hello",
        assistant_response="Hi there!",
    )
    mock_db.commit.side_effect = RuntimeError("Commit failed")

    with pytest.raises(RuntimeError, match="Commit failed"):
        instance.save_conversation(
            user_message="Hello",
            assistant_response="Hi there!",
        )

    mock_db.rollback.assert_called_once()