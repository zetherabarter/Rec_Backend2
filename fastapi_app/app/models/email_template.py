from typing import List, Optional
from odmantic import Model, Field
from datetime import datetime


class EmailTemplate(Model):
    """Model for storing reusable email templates"""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="HTML body content with inline CSS")
    custom: Optional[List[str]] = Field(default=None, description="Custom attribute names used in the template")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the template was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the template was last updated")

    class Config:
        collection = "email-template"


