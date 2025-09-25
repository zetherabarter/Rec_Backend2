from odmantic import Model, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AdminActionLog(Model):
    admin_id: Optional[str] = Field(default=None)
    admin_email: Optional[str] = Field(default=None)
    action: str
    resource_type: Optional[str] = Field(default=None)
    resource_id: Optional[str] = Field(default=None)
    endpoint: Optional[str] = Field(default=None)
    method: Optional[str] = Field(default=None)
    payload: Optional[Dict[str, Any]] = Field(default=None)
    changes: Optional[Dict[str, Any]] = Field(default=None)
    status: str = Field(default="success")
    status_code: Optional[int] = Field(default=None)
    message: Optional[str] = Field(default=None)
    ip: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        collection = "admin_action_logs"
