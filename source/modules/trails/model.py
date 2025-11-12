from __future__ import annotations
import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from source.database.models import BaseDbModel, TimeStampMixin

class Trial(BaseDbModel, TimeStampMixin):
    __tablename__ = "trials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nct_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=True)

    # New fields for geolocation
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    def __repr__(self):
        return f"<Trial nct_id={self.nct_id} title='{self.title}'>"
