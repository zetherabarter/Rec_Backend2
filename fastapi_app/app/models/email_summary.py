from typing import List, Optional
from datetime import datetime
from odmantic import Model, Field

class EmailSummary(Model):
    """Model for storing email summaries"""
    subject: str = Field(..., description="Email subject")
    recipients: List[str] = Field(..., description="List of recipient email addresses") 
    bcc_recipients: Optional[List[str]] = Field(default=None, description="List of BCC recipient email addresses")
    body_preview: str = Field(..., description="Preview of email body (first 200 characters)")
    sent_at: datetime = Field(default_factory=datetime.utcnow, description="When the email was sent")
    success: bool = Field(..., description="Whether the email was sent successfully")
    sent_count: int = Field(default=0, description="Number of successfully sent emails")
    failed_count: int = Field(default=0, description="Number of failed emails")
    errors: Optional[List[str]] = Field(default=None, description="Any errors that occurred")
    
    class Config:
        collection = "email_summaries"
