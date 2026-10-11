from sqlalchemy.orm import Session
from app.models.conversation import Conversation

class ConversationRepository:
    def __init__(self, db):
        self.db = db

    def save_conversation(self, user_message: str, assistant_response: str) -> Conversation:
        conversation = Conversation(
            user_message=user_message,
            assistant_response=assistant_response
        )
        try:
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation
        except Exception as e:
            self.db.rollback()
            raise e

    def get_conversation(self, limit: int = 20, offset: int = 0)->list[Conversation]:
        return (
            self.db.query(Conversation)
            .order_by(Conversation.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )