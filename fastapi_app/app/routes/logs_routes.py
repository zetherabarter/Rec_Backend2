from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from ..utils.auth_middleware import require_roles
from ..utils.enums import UserRole
from ..core.init_db import get_database
from ..models.admin_action_log import AdminActionLog
from ..services.admin_log_service import redact_payload
from odmantic import query

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", response_model=List[dict])
async def get_logs(
    limit: int = 50,
    skip: int = 0,
    admin_email: Optional[str] = None,
    status: Optional[str] = None,
    current_admin = Depends(require_roles([UserRole.SUPERADMIN])),
):
    """Get admin action logs (SuperAdmin only)"""
    try:
        engine = get_database()  # returns AIOEngine

        # Build filters
        filters = []
        if admin_email:
            filters.append(AdminActionLog.admin_email == admin_email)
        if status:
            filters.append(AdminActionLog.status == status)

        # Fetch logs
        if filters:
            logs = await engine.find(
                AdminActionLog,
                query.and_(*filters),
                skip=skip,
                limit=limit,
                sort=AdminActionLog.created_at.desc()
            )
        else:
            logs = await engine.find(
                AdminActionLog,
                skip=skip,
                limit=limit,
                sort=AdminActionLog.created_at.desc()
            )

        results = []
        for log in logs:
            doc = log.dict()
            # Redact payload
            if "payload" in doc and isinstance(doc["payload"], dict):
                doc["payload"] = redact_payload(doc["payload"])
            doc["id"] = str(doc.pop("id", None))  # convert Odmantic id to string
            results.append(doc)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
