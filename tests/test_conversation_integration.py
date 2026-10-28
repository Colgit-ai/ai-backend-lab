from app.core.config import settings

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.conversation import Conversation
from app.repositories.conversation_repository import (
    ConversationRepository,
)

TEST_DATABASE_URL = settings.test_database_url

if not TEST_DATABASE_URL:
    pytest.skip(
        "TEST_DATABASE_URL is not configured",
        allow_module_level=True,
    )

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_save_and_retrieve_conversation(db_session):
    repository = ConversationRepository(db_session)

    repository.save_conversation(
        user_message="What is Redis?",
        assistant_response="Redis is an in-memory data store.",
    )

    conversations = repository.get_conversation(
        limit=10,
        offset=0,
    )

    assert len(conversations) == 1
    assert conversations[0].user_message == "What is Redis?"
    assert (
        conversations[0].assistant_response
        == "Redis is an in-memory data store."
    )

def test_rollback_discards_uncommitted_conversation(db_session):
    conversation = Conversation(
        user_message="Test rollback",
        assistant_response="This should not be saved.",
    )

    db_session.add(conversation)

    # Send the INSERT to PostgreSQL without committing.
    db_session.flush()

    # Undo the uncommitted transaction.
    db_session.rollback()

    # Verify the conversation was not persisted.
    conversations = db_session.query(Conversation).all()

    assert conversations == []