from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
from ..services.admin_log_service import log_action
from ..utils.auth import AuthUtils
import json
from typing import Callable


class AdminActionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        admin_id = None
        admin_email = None

        # --- Extract admin info from JWT ---
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                payload = AuthUtils.verify_token(token)
                if payload and payload.get("type") == "access":
                    admin_id = payload.get("admin_id") or payload.get("user_id")
                    admin_email = payload.get("email")
        except Exception:
            logger.debug("Failed to decode auth token in logging middleware")

        mutating_methods = {"POST", "PUT", "PATCH", "DELETE"}
        is_mutating = (request.method or "").upper() in mutating_methods
        should_log = is_mutating and (admin_id or admin_email)

        body_data = None
        body_bytes = b""
        if should_log:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_text = body_bytes.decode("utf-8", errors="ignore")
                    try:
                        body_data = json.loads(body_text)
                    except Exception:
                        body_data = {"raw": body_text[:200]}
            except Exception:
                body_data = None

            # 🔑 Reset the body so downstream handlers can still read it
            async def receive() -> dict:
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request = Request(request.scope, receive=receive)

        try:
            response: Response = await call_next(request)

            if should_log:
                await log_action(
                    admin_id=admin_id,
                    admin_email=admin_email,
                    action=f"route:{request.method} {request.url.path}",
                    endpoint=str(request.url.path),
                    method=request.method,
                    payload=body_data,
                    status="success" if response.status_code < 400 else "failed",
                    status_code=response.status_code,
                    ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )

            return response

        except Exception as e:
            if should_log:
                await log_action(
                    admin_id=admin_id,
                    admin_email=admin_email,
                    action=f"route:{request.method} {request.url.path}",
                    endpoint=str(request.url.path),
                    method=request.method,
                    payload=body_data,
                    status="failed",
                    status_code=500,
                    message=str(e),
                    ip=request.client.host if request.client else None,
                )
            logger.exception("Unhandled exception in AdminActionLoggingMiddleware")
            raise
