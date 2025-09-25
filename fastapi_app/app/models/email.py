from typing import List, Optional
from odmantic import Model, Field
from datetime import datetime
from ..utils.enums import EmailStatus

class Email(Model):
    """Email model for tracking communication"""
    recipients: List[str]  # List of recipient email addresses
    status: EmailStatus
    message: str
    subject: str
    date_time: datetime
    
    class Config:
        collection = "emails"

class EmailSummary(Model):
    """Email summary model for tracking sent emails"""
    subject: str
    recipients: List[str]  # Unique list of recipients (no duplicates)
    bcc: Optional[List[str]] = Field(default=None)
    body_preview: str  # First 200 characters of body
    sent_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    total_recipients: int = Field(default=0)
    status: str = Field(default="sent")  # sent, failed, partial
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    errors: Optional[List[str]] = Field(default=None)
    
    class Config:
        collection = "email_summaries"
