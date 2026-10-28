
from unittest.mock import MagicMock

import pytest

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repository(mock_db):
    return ConversationRepository(mock_db)


def test_get_conversations_applies_pagination(
    mock_db, repository
):
    expected = [
        Conversation(
            user_message="Hello",
            assistant_response="Hi there!"
        )
    ]

    query = mock_db.query.return_value
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.all.return_value = expected

    result = repository.get_conversation(
        limit=5,
        offset=10
    )

    assert result == expected
    query.offset.assert_called_once_with(10)
    query.limit.assert_called_once_with(5)
    query.all.assert_called_once()


def test_save_conversation_adds_and_flushes(
    mock_db,
    repository,
):
    result = repository.save_conversation(
        user_message="What is Redis?",
        assistant_response="Redis is an in-memory data store.",
    )

    mock_db.add.assert_called_once_with(result)
    mock_db.flush.assert_called_once()
    mock_db.refresh.assert_called_once_with(result)

    # Transaction management belongs to the service layer.
    mock_db.commit.assert_not_called()
    mock_db.rollback.assert_not_called()

    assert result.user_message == "What is Redis?"
    assert result.assistant_response == "Redis is an in-memory data store."


def test_save_conversation_propagates_flush_failure(
    mock_db,
    repository,
):
    mock_db.flush.side_effect = RuntimeError("Database error")

    with pytest.raises(RuntimeError, match="Database error"):
        repository.save_conversation(
            user_message="Hello",
            assistant_response="Hi there!",
        )

    # The repository propagates the failure.
    # The service layer will handle rollback.
    mock_db.rollback.assert_not_called()

