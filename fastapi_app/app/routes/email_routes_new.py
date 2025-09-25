from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel, EmailStr
from app.services.recruitment_email_service import recruitment_email_service
from app.utils.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/emails", tags=["emails"])

# Request models
class BulkEmailRequest(BaseModel):
    recipients: List[Dict[str, str]]  # [{"email": "user@example.com", "name": "User Name"}]
    notification_type: str
    message: str
    action_required: bool = False
    action_link: str = ""

class InterviewReminderRequest(BaseModel):
    email: EmailStr
    name: str
    interview_type: str
    date: str
    time: str
    location: str = "Online"
    meeting_link: str = ""

class StatusUpdateRequest(BaseModel):
    email: EmailStr
    name: str
    job_title: str
    status: str  # "screening", "selected", "rejected"
    stage: str  # "application", "interview", "final"
    next_round: str = ""
    package: str = ""
    joining_date: str = ""
    feedback: str = ""

class DocumentRequestEmail(BaseModel):
    email: EmailStr
    name: str
    documents: List[str]
    deadline: str

class OfferLetterEmail(BaseModel):
    email: EmailStr
    name: str
    job_title: str
    package: str
    joining_date: str
    offer_valid_till: str

class GroupDiscussionReminderRequest(BaseModel):
    email: EmailStr
    name: str
    date: str
    time: str
    location: str
    topic: str = ""

class CustomEmailRequest(BaseModel):
    email: EmailStr
    name: str
    template_type: str
    custom_params: Dict[str, Any]

@router.post("/send-welcome")
async def send_welcome_email(
    email: EmailStr,
    name: str,
    current_user: User = Depends(get_current_user)
):
    """Send welcome email to new user"""
    try:
        success = await recruitment_email_service.send_welcome_email(email, name)
        if success:
            return {"message": "Welcome email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send welcome email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending welcome email: {str(e)}"
        )

@router.post("/send-interview-reminder")
async def send_interview_reminder(
    request: InterviewReminderRequest,
    current_user: User = Depends(get_current_user)
):
    """Send interview reminder email"""
    try:
        success = await recruitment_email_service.send_interview_reminder(
            email=request.email,
            name=request.name,
            interview_type=request.interview_type,
            date=request.date,
            time=request.time,
            location=request.location,
            meeting_link=request.meeting_link
        )
        
        if success:
            return {"message": "Interview reminder sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send interview reminder"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending interview reminder: {str(e)}"
        )

@router.post("/send-group-discussion-reminder")
async def send_group_discussion_reminder(
    request: GroupDiscussionReminderRequest,
    current_user: User = Depends(get_current_user)
):
    """Send group discussion reminder email"""
    try:
        success = await recruitment_email_service.send_group_discussion_reminder(
            email=request.email,
            name=request.name,
            date=request.date,
            time=request.time,
            location=request.location,
            topic=request.topic
        )
        
        if success:
            return {"message": "Group discussion reminder sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send group discussion reminder"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending group discussion reminder: {str(e)}"
        )

@router.post("/send-status-update")
async def send_status_update(
    request: StatusUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Send status update email (screening, selection, rejection)"""
    try:
        if request.status.lower() == "screening":
            success = await recruitment_email_service.send_screening_notification(
                email=request.email,
                name=request.name,
                job_title=request.job_title,
                next_round=request.next_round
            )
        elif request.status.lower() == "selected":
            success = await recruitment_email_service.send_selection_notification(
                email=request.email,
                name=request.name,
                job_title=request.job_title,
                package=request.package,
                joining_date=request.joining_date
            )
        elif request.status.lower() == "rejected":
            success = await recruitment_email_service.send_rejection_notification(
                email=request.email,
                name=request.name,
                stage=request.stage,
                feedback=request.feedback
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Use 'screening', 'selected', or 'rejected'"
            )
        
        if success:
            return {"message": f"Status update email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send status update email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending status update: {str(e)}"
        )

@router.post("/send-document-request")
async def send_document_request(
    request: DocumentRequestEmail,
    current_user: User = Depends(get_current_user)
):
    """Send document submission request email"""
    try:
        success = await recruitment_email_service.send_document_request(
            email=request.email,
            name=request.name,
            documents=request.documents,
            deadline=request.deadline
        )
        
        if success:
            return {"message": "Document request email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send document request email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending document request: {str(e)}"
        )

@router.post("/send-offer-letter")
async def send_offer_letter_notification(
    request: OfferLetterEmail,
    current_user: User = Depends(get_current_user)
):
    """Send offer letter notification email"""
    try:
        success = await recruitment_email_service.send_offer_letter(
            email=request.email,
            name=request.name,
            job_title=request.job_title,
            package=request.package,
            joining_date=request.joining_date,
            offer_valid_till=request.offer_valid_till
        )
        
        if success:
            return {"message": "Offer letter notification sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send offer letter notification"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending offer letter notification: {str(e)}"
        )

@router.post("/send-bulk-notification")
async def send_bulk_notification(
    request: BulkEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """Send bulk notification emails"""
    try:
        results = await recruitment_email_service.send_bulk_notification(
            recipients=request.recipients,
            notification_type=request.notification_type,
            message=request.message,
            action_required=request.action_required,
            action_link=request.action_link
        )
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        return {
            "message": f"Bulk notification completed",
            "successful": successful,
            "total": total,
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending bulk notification: {str(e)}"
        )

@router.post("/send-custom-email")
async def send_custom_email(
    request: CustomEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """Send custom email with specific template"""
    try:
        success = await recruitment_email_service.send_custom_recruitment_email(
            email=request.email,
            name=request.name,
            template_type=request.template_type,
            custom_params=request.custom_params
        )
        
        if success:
            return {"message": "Custom email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send custom email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending custom email: {str(e)}"
        )
