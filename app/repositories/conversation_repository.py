
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_conversation(
        self,
        user_message: str,
        assistant_response: str,
        conversation_id: str,
        user_id: int,
    ) -> Conversation:
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            user_message=user_message,
            assistant_response=assistant_response,
        )
        self.db.add(conversation)
        self.db.flush()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(desc(Conversation.id))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_conversation_history(
        self,
        conversation_id: str,
        user_id: int,
        limit: int = 10,
    ) -> list[Conversation]:
        recent_turns = (
            self.db.query(Conversation)
            .filter(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
            .order_by(Conversation.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(recent_turns))

    def get_conversation_by_id(
        self, conversation_id: str, user_id: int
    ) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
            .order_by(Conversation.id.asc())
            .all()
        )

    def delete_conversation(self, conversation_id: str, user_id: int) -> int:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
            .delete(synchronize_session=False)
        )
