from typing import Dict, Any, Optional, List
from ..utils.resend_service import email_service
from loguru import logger

# Fix: Define resend_service as email_service
resend_service = email_service

class RecruitmentEmailService:
    """
    High-level email service for recruitment portal
    Uses EmailJS for all email communications
    """
    
    @staticmethod
    async def send_login_otp(email: str, name: str, otp: str) -> bool:
        """Send OTP for user login"""
        return await resend_service.send_otp_email(email, name, otp)
    
    @staticmethod
    async def send_welcome_email(email: str, name: str) -> bool:
        """Send welcome email to new users"""
        return await resend_service.send_welcome_email(email, name)
    
    @staticmethod
    async def send_application_confirmation(
        email: str, 
        name: str, 
        job_title: str, 
        application_id: str
    ) -> bool:
        """Send application confirmation email"""
        return await resend_service.send_notification_email(
            email, name,
            "Application Received",
            f"Your application for {job_title} has been successfully submitted. "
            f"Your application ID is: {application_id}. "
            f"We will review your application and get back to you soon.",
            False
        )
    
    @staticmethod
    async def send_screening_notification(
        email: str, 
        name: str, 
        job_title: str, 
        next_round: str
    ) -> bool:
        """Send screening notification"""
        return await resend_service.send_status_update_email(
            email, name,
            "Application Review",
            "screening",
            f"You have been selected for {next_round}. Details will be shared shortly."
        )
    
    @staticmethod
    async def send_interview_reminder(
        email: str, 
        name: str, 
        interview_type: str,
        date: str, 
        time: str, 
        location: str = "Online",
        meeting_link: str = ""
    ) -> bool:
        """Send interview reminder"""
        location_text = location if location != "Online" else f"Online - {meeting_link}"
        
        return await resend_service.send_reminder_email(
            email, name,
            f"{interview_type} Interview",
            date, time, location_text
        )
    
    @staticmethod
    async def send_group_discussion_reminder(
        email: str, 
        name: str, 
        date: str, 
        time: str, 
        location: str,
        topic: str = ""
    ) -> bool:
        """Send group discussion reminder"""
        topic_text = f"Topic: {topic}" if topic else "Topic will be provided on the day"
        
        return await resend_service.send_reminder_email(
            email, name,
            "Group Discussion",
            date, time, f"{location}. {topic_text}"
        )
    
    @staticmethod
    async def send_selection_notification(
        email: str, 
        name: str, 
        job_title: str,
        package: str = "",
        joining_date: str = ""
    ) -> bool:
        """Send final selection notification"""
        message = f"Congratulations! You have been selected for the position of {job_title}."
        if package:
            message += f" Package: {package}."
        if joining_date:
            message += f" Expected joining date: {joining_date}."
        message += " HR will contact you with further details."
        
        return await resend_service.send_status_update_email(
            email, name, "Final Selection", "Selected", message
        )
    
    @staticmethod
    async def send_rejection_notification(
        email: str, 
        name: str, 
        stage: str,
        feedback: str = ""
    ) -> bool:
        """Send rejection notification"""
        message = f"Thank you for your interest in our company. "
        message += f"Unfortunately, we will not be moving forward with your application at the {stage} stage."
        if feedback:
            message += f" Feedback: {feedback}"
        message += " We encourage you to apply for future opportunities."
        
        return await resend_service.send_status_update_email(
            email, name, stage, "Not Selected", message
        )
    
    @staticmethod
    async def send_document_request(
        email: str, 
        name: str, 
        documents: List[str],
        deadline: str
    ) -> bool:
        """Send document submission request"""
        doc_list = ", ".join(documents)
        message = f"Please submit the following documents: {doc_list}. "
        message += f"Deadline: {deadline}. Upload documents through your candidate portal."
        
        return await resend_service.send_notification_email(
            email, name,
            "Document Submission Required",
            message, True,
            "https://your-portal.com/upload-documents"
        )
    
    @staticmethod
    async def send_offer_letter(
        email: str, 
        name: str, 
        job_title: str,
        package: str,
        joining_date: str,
        offer_valid_till: str
    ) -> bool:
        """Send offer letter notification"""
        message = f"Congratulations! We are pleased to offer you the position of {job_title}. "
        message += f"Package: {package}. Joining Date: {joining_date}. "
        message += f"This offer is valid till {offer_valid_till}. "
        message += "Please check your email for the detailed offer letter."
        
        return await resend_service.send_notification_email(
            email, name, "Job Offer", message, True,
            "https://your-portal.com/offer-letter"
        )
    
    @staticmethod
    async def send_bulk_notification(
        recipients: List[Dict[str, str]], 
        notification_type: str, 
        message: str,
        action_required: bool = False,
        action_link: str = ""
    ) -> Dict[str, bool]:
        """
        Send bulk notifications to multiple recipients
        Recipients format: [{"email": "user@example.com", "name": "User Name"}, ...]
        Returns: {"email": success_status, ...}
        """
        results = {}
        
        for recipient in recipients:
            try:
                success = await resend_service.send_notification_email(
                    recipient["email"], recipient["name"],
                    notification_type, message, action_required, action_link
                )
                results[recipient["email"]] = success
                
            except Exception as e:
                logger.error(f"Failed to send email to {recipient['email']}: {str(e)}")
                results[recipient["email"]] = False
        
        return results
    
    @staticmethod
    async def send_custom_recruitment_email(
        email: str,
        name: str,
        template_type: str,
        custom_params: Dict[str, Any]
    ) -> bool:
        """Send custom recruitment email"""
        try:
            return await resend_service.send_custom_email(template_type, {
                "to_email": email,
                "to_name": name,
                "from_name": "Recruitment Portal Team",
                "company_name": "Recruitment Portal",
                "reply_to": "hr@recruitmentportal.com",
                **custom_params
            })
        except Exception as e:
            logger.error(f"Error sending custom email: {str(e)}")
            return False

# Create singleton instance
recruitment_email_service = RecruitmentEmailService()
