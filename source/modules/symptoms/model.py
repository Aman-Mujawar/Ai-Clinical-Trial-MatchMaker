from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.database.models import BaseDbModel, TimeStampMixin

if TYPE_CHECKING:
    from source.modules.user.models import Users  # ensure singular filename if it's `model.py`

class SymptomEntry(BaseDbModel, TimeStampMixin):
    __tablename__ = "symptom_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    symptom_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    onset_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationship to user
    user: Mapped["Users"] = relationship("Users", back_populates="symptom_entries")

    def __repr__(self) -> str:
        return f"<SymptomEntry user_id={self.user_id} symptoms={self.parsed_symptoms}>"
