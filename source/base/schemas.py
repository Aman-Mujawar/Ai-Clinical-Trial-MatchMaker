"""
Base Schemas
"""

from datetime import datetime
from typing import Annotated, Generic, List, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field
from pydantic.alias_generators import to_camel

DataT = TypeVar("DataT")
"""Generic type for the 'data' attribute of the base API response model"""

ListItemsT = TypeVar("ListDataT")
"""Generic type for the 'data' attribute of the paginated list model"""


class AppBaseModel(BaseModel):
    """
    Base model to use for all app schemas
    """

    class Config:
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        str_strip_whitespace = True
        populate_by_name = True
        alias_generator = to_camel

        json_encoders = {
            # custom output conversion for datetime
            datetime: lambda v: v.isoformat(timespec="seconds") if v else None,
        }


class BaseApiResponse(AppBaseModel, Generic[DataT]):
    """
    Base API Response model
    """

    status: bool = Field(
        description="General status of the response - True: success, False: failure",
        default=True,
    )
    """General status of the response - True: success, False: failure"""
    code: str | None = Field(description="Response Code", default=None)
    """Response Code"""
    message: str | None = Field(
        description="Optional message / comment / hint / error", default=None
    )
    """Optional message / comment / hint / error"""
    data: DataT | None = Field(description="The 'data' or payload", default=None)
    """The 'data' or payload"""
    errors: List[str] | None = Field(description="Error(s), if any", default=None)
    """Error(s), if any"""

    @classmethod
    def success_instance(
        cls,
        code: str = "OK",
        message: Union[str, None] = None,
        data: Union[DataT, None] = None,
    ):
        """
        Create a success instance

        Parameters:
            code (str): Response code
            message (str): Optional message
            data (DataT): Data / payload

        Returns:
            BaseApiResponse: Success instance
        """

        return cls(status=True, code=code, message=message, data=data)


class BooleanApiResponse(BaseApiResponse[bool]):
    """
    Boolean API Response model
    """

    pass


class IdApiResponse(BaseApiResponse[UUID]):
    """
    ID (UUID) API Response model
    """

    pass


class PaginatedListData(AppBaseModel, Generic[ListItemsT]):
    """
    Paginated List Data model
    """

    list_items: List[ListItemsT] = Field(..., description="List items")
    total_records: int = Field(..., description="Total records")
    page_number: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")


class IdResponseData(AppBaseModel):
    """
    ID Response Data model
    """

    id: UUID = Field(..., description="ID")


class IdResponse(BaseApiResponse[IdResponseData]):
    """
    ID Response model
    """

    pass


def empty_string_to_none(v):
    """
    Convert empty string to None
    """
    if v == "":
        return None
    return v

UUIDEmptyStrToNone = Annotated[UUID | None, BeforeValidator(empty_string_to_none)]
"""UUID or None with empty string converted to None"""

StrEmptyStrToNone = Annotated[str | None, BeforeValidator(empty_string_to_none)]
"""String or None with empty string converted to None"""

IntEmptyStrToNone = Annotated[int | None, BeforeValidator(empty_string_to_none)]
"""Int or None with empty string converted to None"""

FloatEmptyStrToNone = Annotated[float | None, BeforeValidator(empty_string_to_none)]
"""Float or None with empty string converted to None"""
