from typing import Any, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def error_body(code: str, message: str, request_id: str, details: Optional[dict] = None) -> dict:
    return {
        "success": False,
        "error": {"code": code, "message": message, "details": details or {}},
        "request_id": request_id,
    }


def success_body(data: Any, request_id: str) -> dict:
    return {"success": True, "data": data, "request_id": request_id}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, request_id, exc.details),
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        code = detail.get("code", "HTTP_ERROR")
        message = detail.get("message", str(detail))
        details = detail.get("details", {})
    else:
        code = "HTTP_ERROR"
        message = str(detail)
        details = {}
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, message, request_id, details),
    )
