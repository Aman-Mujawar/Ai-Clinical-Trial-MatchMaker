import uuid
from datetime import datetime
from io import BytesIO
from typing import List
from uuid import UUID, uuid4

import pandas as pd
from fastapi.responses import StreamingResponse
from sqlalchemy import String, cast
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.sql import func, or_, select

from base.exceptions import AgriAppError
from logger import service as log_service
from modules.authentication import service as auth_service
from modules.client import service as client_service
from modules.email import service as email_service
from modules.farmer import service as farmer_service
from modules.role_permission import service as role_permission_service
from modules.role_permission.enums import RoleCodesE
from modules.role_permission.models import Role
from modules.role_permission.schemas import RoleVmList
from modules.session.schema import ApiSessionData
from modules.user import service as user_service
from modules.user.enums import UserPreferenceCodesE
from modules.user.errors import ErrorCode
from modules.user.models import User, UserManager, UserRole
from modules.user.schemas import (
    AddUserRequest,
    ChangePasswordRequest,
    CurrentUserVm,
    ImportUserResponseData,
    PaginatedUserListData,
    RoleCountVm,
    UpdateUserRequest,
    UpdateUserResponseData,
    UserApplicationPreferencesData,
    UserListItemVm,
    UserMinVm,
    UserPersonalDetailsResponseData,
)


def add_user(
    db: DbSession, session_data: ApiSessionData, request: AddUserRequest
) -> bool:
    client_id = session_data.client_id

    if user_service.check_user_exists_with_email(db, request.email):
        raise AgriAppError(
            ErrorCode.E_DUPLICATE_USER_EMAIL["code"],
            ErrorCode.E_DUPLICATE_USER_EMAIL["message"],
        )
    if user_service.check_user_exists_with_phone_number(
        db, request.phone_cc, request.phone_number
    ):
        raise AgriAppError(
            ErrorCode.E_DUPLICATE_USER_PHONENUMBER["code"],
            ErrorCode.E_DUPLICATE_USER_PHONENUMBER["message"],
        )

    # double check if the role is allowed for the client
    if not client_service.check_role_allowed_for_client(
        db, client_id, role_code=request.role
    ):
        raise AgriAppError(
            ErrorCode.E_INVALID_ROLE_FOR_CLIENT["code"],
            ErrorCode.E_INVALID_ROLE_FOR_CLIENT["message"],
        )

    user_uuid = uuid.uuid4()
    created_by_uuid = session_data.user_id
    modified_by_uuid = session_data.user_id
    hardcoded_password = "defaultpassword123"
    lockout_end = datetime.min

    new_user = User(
        id=user_uuid,
        name=request.name,
        email=request.email,
        normalized_email=user_service.make_normalized_email(request.email),
        phone_cc=request.phone_cc,
        phone_number=request.phone_number,
        address=request.address,
        password=hardcoded_password,
        is_setup_complete=False,
        is_active=True,
        is_lockedout=False,
        is_test_user=False,
        sub_district=None,
        district=None,
        province=None,
        postal_code=None,
        client_id=client_id,
        created_by=created_by_uuid,
        modified_by=modified_by_uuid,
        lockout_end=lockout_end,
    )

    db.add(new_user)

    # Single role
    role_to_assign = role_permission_service.get_role_by_code(db, request.role)
    user_role = UserRole(
        id=uuid.uuid4(),
        user_id=new_user.id,
        role_id=role_to_assign.id,
        created_by=created_by_uuid,
        modified_by=modified_by_uuid,
    )
    db.add(user_role)

    if isinstance(request.managers, list):
        for manager_id in request.managers:
            user_manager = UserManager(
                id=uuid.uuid4(),
                user_id=new_user.id,
                manager_id=manager_id,
                created_by=created_by_uuid,
                modified_by=modified_by_uuid,
            )
            db.add(user_manager)

    db.commit()
 

