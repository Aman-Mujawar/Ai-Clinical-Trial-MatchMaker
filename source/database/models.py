"""
Base Database Models
"""

from datetime import datetime
from uuid import UUID
from sqlalchemy import TIMESTAMP, Boolean, Uuid, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )


class CreatorModifierMixin(object):
    """Creator and modifier mixin"""

    created_by: Mapped[UUID] = mapped_column(Uuid)
    modified_by: Mapped[UUID] = mapped_column(Uuid)


class SoftDeleteMixin(object):
    """Soft delete flag mixin"""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class BaseDbModel(DeclarativeBase):
    """
    Base class for all database models.
    """
