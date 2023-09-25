from typing import Any, Dict
from fastapi.security import SecurityScopes
from pydantic import BaseModel
from fastapi import HTTPException, status


class HttpExceptionModel(BaseModel):
    """
    这个类用在 `responses` 参数中提供响应码`model`用的。

    用法：
    ```python

    @api.get(
        "/test",
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR:{"model":HttpExceptionModel}
        }
    )
    async def test():
        rase HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="hello")

    ```

    Args:
        BaseModel (_type_): _description_
    """

    detail: str


class ExistedError(HTTPException):
    def __init__(
        self,
        detail: Any = None,
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, headers)


class NotFoundError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class JWTUnauthorizedError(HTTPException):
    """
    JWT授权异常
    """

    def __init__(
        self, detail: Any = None, scopes: SecurityScopes | None = None
    ) -> None:
        headers = {}
        headers["WWW-Authenticate"] = (
            "Bearer" if not scopes else f"Bearer scopes={scopes.scope_str}"
        )
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)
