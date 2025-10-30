from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Computed,
    Integer,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.models import (
    BaseDbModel,
    CreatorModifierMixin,
    SoftDeleteMixin,
    TimeStampMixin,
)


class User(BaseDbModel, TimeStampMixin, CreatorModifierMixin, SoftDeleteMixin):
    """Represents application users"""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    seq_id: Mapped[int] = mapped_column(Integer)

    internal_id: Mapped[str] = mapped_column(Text, unique=True, nullable=True)

    name: Mapped[str] = mapped_column(Text)

    email: Mapped[str] = mapped_column(Text)
    normalized_email: Mapped[str] = mapped_column(Text, unique=True)

    address: Mapped[str | None] = mapped_column(Text)
    sub_district: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    province: Mapped[str | None] = mapped_column(Text)
    postal_code: Mapped[str | None] = mapped_column(Text)

    phone_cc: Mapped[str] = mapped_column(Text)
    phone_number: Mapped[str] = mapped_column(Text)
    phone_full: Mapped[str] = mapped_column(
        Text, Computed("phone_cc || phone_number", persisted=True)
    )

    password: Mapped[str] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("phone_cc", "phone_number"),)