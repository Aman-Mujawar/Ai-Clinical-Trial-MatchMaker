from __future__ import annotations
import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, JSON, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from source.database.models import BaseDbModel, TimeStampMixin, CreatorModifierMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from source.modules.user.models import Users  # type hint only


# --- PatientProfile Model ---
class PatientProfile(BaseDbModel, TimeStampMixin, CreatorModifierMixin, SoftDeleteMixin):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Demographics (free text now)
    date_of_birth: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Measurements
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Medical / clinical data
    diagnoses: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")
    allergies: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")
    medications: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")
    vaccinations: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")
    family_history: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")

    # Lifestyle (free text)
    smoking_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    alcohol_use: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Insurance & contact
    insurance: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")
    emergency_contact: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default="{}")

    # Provider linking
    primary_provider_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    prescreening: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Preferences
    consent_to_share: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    contact_preference: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Relationship to Users
    user: Mapped["Users"] = relationship("Users", back_populates="patient_profile", uselist=False)

    # --- Computed properties ---
    @property
    def age(self) -> int | None:
        """Return the patient's age in years based on date_of_birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def conditions(self) -> list:
        """Return a list of condition names from diagnoses JSON."""
        if self.diagnoses:
            return list(self.diagnoses.keys())  # or list(self.diagnoses.values()) if needed
        return []

    def __repr__(self):
        return f"<PatientProfile user_id={self.user_id}>"

    # --- Add this inside PatientProfile class ---
    @property
    def location(self) -> str | None:
        """Return a string representing the patient's location, default None if not set."""
        # Example: extract from emergency_contact or other data
        if self.emergency_contact and "address" in self.emergency_contact:
            return self.emergency_contact["address"]
        return None
