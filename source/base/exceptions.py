"""
Base Exceptions
"""

from fastapi import HTTPException, status


class AgriAppError(HTTPException):
    """
    Base error (exception) class for the application

    Attributes:
    - code: str: Error code, in the format E_XXX_XXX
    - reason: str: Error reason
    """

    code: str
    """Error code, in the format E_XXX_XXX"""
    reason: str
    """Error reason"""

    def __init__(self, code: str, reason: str):
        self.code = code
        self.reason = reason
        super().__init__(status.HTTP_200_OK, [self.code, self.reason])

    def __str__(self):
        return f"{self.code}: {self.reason}"