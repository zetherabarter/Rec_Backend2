from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from ..schemas.email_schema import EmailSendRequest, EmailSendResponse, EmailTemplateCreate, EmailTemplateResponse
from ..utils.resend_service import email_service
from ..models.email_summary import EmailSummary
from ..models.email_template import EmailTemplate
from ..core.init_db import get_database

router = APIRouter(prefix="/emails", tags=["emails"])

@router.post("/send", response_model=EmailSendResponse)
async def send_email(email_request: EmailSendRequest):
    """
    Send email to multiple recipients with HTML content
    
    - **subject**: Email subject line
    - **emails**: List of recipient email addresses
    - **body**: HTML body content with inline CSS (will be rendered in email clients)
    - **bcc**: Optional list of BCC email addresses
    """
    try:
        # Validate that we have at least one recipient
        if not email_request.emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="At least one email recipient is required"
            )

        # Send email using the email service (per-recipient templating happens in the service)
        result = await email_service.send_email(
            subject=email_request.subject,
            emails=email_request.emails,
            body=email_request.body,
            bcc=email_request.bcc,
            custom=email_request.custom or {},
            attachments=email_request.attachments or []
        )

        # Prepare response based on result
        if result["success"]:
            message = f"Email sent successfully to {result['sent_count']} out of {result.get('total_recipients', len(email_request.emails))} recipients"
            if result.get("failed_count", 0) > 0:
                message += f". {result['failed_count']} emails failed to send."
        else:
            message = f"Failed to send emails. Error: {result.get('error', 'Unknown error')}"

        return EmailSendResponse(
            success=result["success"],
            sent_count=result.get("sent_count", 0),
            failed_count=result.get("failed_count", 0),
            total_recipients=result.get("total_recipients", len(email_request.emails)),
            errors=result.get("errors"),
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def save_email_template(template: EmailTemplateCreate):
    """
    Save an email template in the "email-template" collection.
    Stores: subject, body, and optional custom attributes. No sending involved.
    """
    try:
        engine = get_database()

        # Create ODMantic document
        template_doc = EmailTemplate(
            subject=template.subject,
            body=template.body,
            custom=template.custom
        )

        saved = await engine.save(template_doc)

        return EmailTemplateResponse(
            id=str(saved.id),
            subject=saved.subject,
            body=saved.body,
            custom=saved.custom,
            created_at=saved.created_at,
            updated_at=saved.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save email template: {str(e)}"
        )

@router.get("/templates", response_model=List[EmailTemplateResponse])
async def get_email_templates():
    """
    Get all saved email templates from the "email-template" collection.
    """
    try:
        engine = get_database()
        templates = await engine.find(EmailTemplate)

        return [
            EmailTemplateResponse(
                id=str(t.id),
                subject=t.subject,
                body=t.body,
                custom=t.custom,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in templates
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email templates: {str(e)}",
        )

@router.get("/summaries", response_model=List[EmailSummary])
async def get_email_summaries(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of summaries to return"),
    skip: int = Query(default=0, ge=0, description="Number of summaries to skip (for pagination)")
):
    """
    Get email summaries with pagination
    
    - **limit**: Maximum number of summaries to return (1-100, default 50)
    - **skip**: Number of summaries to skip for pagination (default 0)
    
    Returns list of email summaries ordered by sent date (newest first).
    Each summary contains unique recipients (no duplicates if email was sent to multiple people).
    """
    try:
        summaries = await email_service.get_email_summaries(limit=limit, skip=skip)
        return summaries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email summaries: {str(e)}"
        )

@router.get("/summaries/stats")
async def get_email_summary_stats():
    """
    Get email summary statistics
    
    Returns statistics about sent emails including:
    - Total emails sent
    - Successful vs failed emails  
    - Recent activity (last 24 hours)
    - Success rate percentage
    """
    try:
        stats = await email_service.get_email_summary_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email statistics: {str(e)}"
        )
