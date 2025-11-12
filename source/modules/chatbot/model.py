from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.database.models import BaseDbModel, TimeStampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.modules.user.models import Users


class ChatbotMessage(BaseDbModel, TimeStampMixin):
    __tablename__ = "chatbot_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationship with user
    user: Mapped["Users"] = relationship("Users", back_populates="chatbot_messages")


class AIChatSession(BaseDbModel, TimeStampMixin):
    """
    Stores conversation state per user for the chatbot.
    """
    __tablename__ = "chatbot_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_data: Mapped[dict] = mapped_column(JSONB, nullable=True)  # store conversation state
    messages: Mapped[list] = mapped_column(JSONB, nullable=True)      # user/assistant messages
    last_interaction: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationship with user
    user: Mapped["Users"] = relationship("Users", back_populates="chatbot_sessions")
