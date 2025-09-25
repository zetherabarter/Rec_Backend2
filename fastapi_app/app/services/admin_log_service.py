from typing import Optional, Dict, Any
from ..core.init_db import get_database
from loguru import logger
from datetime import datetime
from ..models.admin_action_log import AdminActionLog  

SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "otp"}


def redact_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    out = {}
    for k, v in payload.items():
        if k.lower() in SENSITIVE_KEYS:
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out


async def log_action(
    admin_id: Optional[str],
    admin_email: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    changes: Optional[Dict[str, Any]] = None,
    status: str = "success",
    status_code: Optional[int] = None,
    message: Optional[str] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    try:
        engine = get_database()  # this is an AIOEngine, not a raw DB
        log_entry = AdminActionLog(
            admin_id=str(admin_id) if admin_id else None,
            admin_email=admin_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            endpoint=endpoint,
            method=method,
            payload=redact_payload(payload) if payload else None,
            changes=changes,
            status=status,
            status_code=status_code,
            message=message,
            ip=ip,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
        )
        await engine.save(log_entry)
    except Exception:
        logger.exception("Failed to write admin action log")
