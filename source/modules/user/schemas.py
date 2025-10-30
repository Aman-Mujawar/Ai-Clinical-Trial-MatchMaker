
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi.responses import StreamingResponse
from pydantic import EmailStr, Field

from base.schemas import (
    AppBaseModel,
    BaseApiResponse,
    BooleanApiResponse,
    PaginatedListData,
)

class AddUserRequest(AppBaseModel):
    name: str = Field(..., description="User name")
    email: EmailStr = Field(..., description="User email")
    phone_cc: str = Field(..., description="User phone country code")
    phone_number: str = Field(..., description="User phone number")
    address: str = Field(..., description="User's address")
    managers: List[str] = Field(..., description="Managers of the user")
