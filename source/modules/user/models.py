from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
import enum

from sqlalchemy import String, Boolean, Text, Sequence, text, TIMESTAMP, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.database.models import BaseDbModel, TimeStampMixin, CreatorModifierMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from source.modules.PatientProfile.model import PatientProfile
    from source.modules.symptoms.model import SymptomEntry
    from source.modules.matching.model import TrialMatch
    from source.modules.chatbot.models import ChatbotMessage, AIChatSession

# --- Enums ---
class UserRole(enum.Enum):
    PATIENT = "PATIENT"
    CAREGIVER = "CAREGIVER"
    PROVIDER = "PROVIDER"
    ADMIN = "ADMIN"

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

# --- Users model ---
class Users(BaseDbModel, TimeStampMixin, CreatorModifierMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence_number: Mapped[int | None] = mapped_column(
        Sequence("users_seq", start=1, increment=1),
        nullable=True,
        unique=True,
        server_default=text("nextval('users_seq')")
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_email_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole | None] = mapped_column(SAEnum(UserRole, name="userrole"), nullable=True)
    status: Mapped[UserStatus | None] = mapped_column(SAEnum(UserStatus, name="userstatus"), nullable=True)

    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    terms_accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_onboarded: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    modified_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    modified_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile", back_populates="user", uselist=False
    )

    symptom_entries: Mapped[List["SymptomEntry"]] = relationship(
        "SymptomEntry", back_populates="user", cascade="all, delete-orphan"
    )
    
    trial_matches: Mapped[List["TrialMatch"]] = relationship(
        "TrialMatch", back_populates="user", cascade="all, delete-orphan"
    )

    # ✅ Chatbot relationships
    chatbot_messages: Mapped[List["ChatbotMessage"]] = relationship(
        "ChatbotMessage", back_populates="user", cascade="all, delete-orphan"
    )

    chatbot_sessions: Mapped[List["AIChatSession"]] = relationship(
        "AIChatSession", back_populates="user", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
