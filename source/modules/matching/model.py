from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.database.models import BaseDbModel, TimeStampMixin
if TYPE_CHECKING:
    from source.modules.user.models import Users


class TrialMatch(BaseDbModel, TimeStampMixin):
    __tablename__ = "trial_matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    matched_trials: Mapped[Any] = mapped_column(JSONB, nullable=True)  # Store trial results as JSON

    # Relationship
    user: Mapped["Users"] = relationship("Users", back_populates="trial_matches")

    def __repr__(self):
        return f"<TrialMatch user_id={self.user_id} query='{self.query_text}'>"
