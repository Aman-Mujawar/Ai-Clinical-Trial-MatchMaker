# models.py - Simplified version
from datetime import datetime
from uuid import UUID
from sqlalchemy import Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from database.models import BaseDbModel

class User(BaseDbModel):
    """Represents application users"""
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password: Mapped[str | None] = mapped_column(Text, nullable=True)
