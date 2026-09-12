from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Optional

from sqlalchemy import select

from app.database.database import SessionLocal
from app.database.schema import Conversation, ConversationMessage, User


class HistoryService:
    def _message_to_dict(self, message: ConversationMessage) -> Dict[str, Any]:
        sources = []
        metadata = {}

        if message.sources:
            try:
                sources = json.loads(message.sources)
            except json.JSONDecodeError:
                sources = []

        if message.metadata_json:
            try:
                metadata = json.loads(message.metadata_json)
            except json.JSONDecodeError:
                metadata = {}

        return {
            "role": message.role,
            "content": message.content,
            "language": message.language,
            "sources": sources,
            "metadata": metadata,
        }

    def _conversation_to_dict(self, conversation: Conversation) -> Dict[str, Any]:
        return {
            "conversation_id": conversation.conversation_id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "language": conversation.language,
            "messages": [
                self._message_to_dict(message)
                for message in conversation.messages
            ],
            "metadata": {},
        }

    async def get_history(
        self,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        with SessionLocal() as db:
            statement = select(Conversation).order_by(
                Conversation.updated_at.desc()
            )

            if user_id:
                statement = statement.where(
                    Conversation.user_id == user_id
                )

            if conversation_id:
                statement = statement.where(
                    Conversation.conversation_id == conversation_id
                )

            conversations = db.scalars(statement).unique().all()

            return {
                "conversations": [
                    self._conversation_to_dict(conversation)
                    for conversation in conversations
                ]
            }

    async def create_conversation(
        self,
        user_id: Optional[str] = None,
        language: str = "en",
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        conversation_id = str(uuid.uuid4())

        with SessionLocal() as db:
            if user_id and db.scalar(
                select(User).where(User.user_id == user_id)
            ) is None:
                db.add(User(user_id=user_id, language=language))
                db.flush()

            conversation = Conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                title=title,
                language=language,
            )
            db.add(conversation)
            db.commit()

            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "language": language,
                "title": title,
                "status": "created",
            }
