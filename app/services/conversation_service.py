
from sqlalchemy.orm import Session

from app.repositories.conversation_repository import ConversationRepository


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ConversationRepository(db)

    def save_conversation(
        self,
        user_message: str,
        assistant_response: str,
        conversation_id: str,
        user_id: int,
    ):
        try:
            conversation = self.repository.save_conversation(
                user_message=user_message,
                assistant_response=assistant_response,
                conversation_id=conversation_id,
                user_id=user_id,
            )
            self.db.commit()
            return conversation
        except Exception:
            self.db.rollback()
            raise

    def delete_conversation(self, conversation_id: str, user_id: int) -> int:
        try:
            deleted_count = self.repository.delete_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
            )
            if deleted_count == 0:
                return 0

            self.db.commit()
            return deleted_count
        except Exception:
            self.db.rollback()
            raise
