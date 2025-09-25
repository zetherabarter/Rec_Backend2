from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EmailSendRequest(BaseModel):
    """Schema for sending email request"""
    subject: str = Field(..., description="Email subject")
    emails: List[EmailStr] = Field(..., description="List of recipient email addresses")
    body: str = Field(..., description="HTML body content with inline CSS")
    bcc: Optional[List[EmailStr]] = Field(default=None, description="List of BCC email addresses")
    custom: Optional[Dict[str, List[str]]] = Field(default=None, description="Map of placeholder arrays for templating")
    attachments: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of attachments: { filename, content_base64, mime_type }"
    )

class EmailSendResponse(BaseModel):
    """Schema for email send response"""
    success: bool = Field(..., description="Whether the email sending was successful")
    sent_count: int = Field(..., description="Number of emails successfully sent")
    failed_count: int = Field(..., description="Number of emails that failed to send")
    total_recipients: int = Field(..., description="Total number of recipients")
    errors: Optional[List[str]] = Field(default=None, description="List of error messages if any")
    message: str = Field(..., description="Response message")

    class Config:
        from_attributes = True

class EmailSummaryResponse(BaseModel):
    """Schema for email summary response"""
    id: str = Field(..., description="Email summary ID")
    subject: str = Field(..., description="Email subject")
    recipients: List[str] = Field(..., description="List of recipient email addresses (unique)")
    bcc_recipients: Optional[List[str]] = Field(default=None, description="List of BCC recipient email addresses (unique)")
    body_preview: str = Field(..., description="Preview of email body")
    sent_at: datetime = Field(..., description="When the email was sent")
    success: bool = Field(..., description="Whether the email was sent successfully")
    sent_count: int = Field(..., description="Number of successfully sent emails")
    failed_count: int = Field(..., description="Number of failed emails")
    errors: Optional[List[str]] = Field(default=None, description="Any errors that occurred")

    class Config:
        from_attributes = True

class EmailStatsResponse(BaseModel):
    """Schema for email statistics response"""
    total_emails: int = Field(..., description="Total number of emails sent")
    successful_emails: int = Field(..., description="Number of successful emails")
    failed_emails: int = Field(..., description="Number of failed emails")
    recent_emails_24h: int = Field(..., description="Number of emails sent in last 24 hours")
    success_rate: float = Field(..., description="Success rate percentage")

    class Config:
        from_attributes = True


class EmailTemplateCreate(BaseModel):
    """Schema for creating/saving an email template"""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="HTML body content with inline CSS")
    custom: Optional[List[str]] = Field(default=None, description="Custom attribute names used in the template")


class EmailTemplateResponse(BaseModel):
    """Schema returned after saving an email template"""
    id: str = Field(..., description="Template identifier")
    subject: str
    body: str
    custom: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        