import smtplib
import asyncio
import socket
import errno
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from ..core.config import settings
from ..core.init_db import get_database
from ..models.email_summary import EmailSummary

class EmailService:
    """
    Email service for sending emails via Gmail SMTP with enhanced blocking detection
    """

    def __init__(self):
        # Gmail SMTP configuration from settings
        self.smtp_host = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.smtp_secure = settings.EMAIL_SECURE
        self.email_user = settings.EMAIL_USER
        # Gmail App Passwords are shown with spaces for readability; remove them if present
        self.email_pass = settings.EMAIL_PASS.replace(" ", "") if settings.EMAIL_PASS else settings.EMAIL_PASS
        self.email_from = settings.EMAIL_FROM
        
        # Test mode - only enable if explicitly set to True
        self.test_mode = settings.EMAIL_TEST_MODE
        
        # SMTP blocking detection cache
        self._smtp_blocked_cache = None
        self._smtp_test_performed = False
        
        logger.info(f"Email Service initialized:")
        logger.info(f"  - Test Mode: {self.test_mode}")
        logger.info(f"  - SMTP Host: '{self.smtp_host}'")
        logger.info(f"  - SMTP Port: {self.smtp_port}")
        logger.info(f"  - Email User: '{self.email_user}'")
        logger.info(f"  - Email From: '{self.email_from}'")
        logger.info(f"  - Environment: '{settings.ENVIRONMENT}'")

    async def test_smtp_connectivity(self) -> Dict[str, Any]:
        """
        Test SMTP connectivity without sending emails
        Returns detailed connectivity information
        """
        if self._smtp_test_performed and self._smtp_blocked_cache is not None:
            return self._smtp_blocked_cache
            
        logger.info("Testing SMTP connectivity...")
        
        try:
            timeout = getattr(settings, "EMAIL_SMTP_TIMEOUT", 10)
            
            # Test basic socket connection first
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            try:
                result = sock.connect_ex((self.smtp_host, self.smtp_port))
                sock.close()
                
                if result != 0:
                    # Connection failed at socket level
                    error_msg = f"Socket connection failed to {self.smtp_host}:{self.smtp_port} (errno: {result})"
                    
                    # Check for common blocking scenarios
                    if result == errno.ENETUNREACH:
                        error_msg += " - Network unreachable (likely blocked by host/firewall)"
                    elif result == errno.EHOSTUNREACH:
                        error_msg += " - Host unreachable (DNS or routing issue)"
                    elif result == errno.ECONNREFUSED:
                        error_msg += " - Connection refused (port blocked or service down)"
                    elif result == errno.ETIMEDOUT:
                        error_msg += " - Connection timed out (firewall or network issue)"
                    
                    self._smtp_blocked_cache = {
                        "success": False,
                        "blocked": True,
                        "error": error_msg,
                        "error_code": result,
                        "test_type": "socket",
                        "recommendations": self._get_blocking_recommendations()
                    }
                    self._smtp_test_performed = True
                    return self._smtp_blocked_cache
                    
            except socket.timeout:
                self._smtp_blocked_cache = {
                    "success": False,
                    "blocked": True,
                    "error": f"Socket timeout after {timeout}s - likely blocked by firewall",
                    "error_code": "TIMEOUT",
                    "test_type": "socket",
                    "recommendations": self._get_blocking_recommendations()
                }
                self._smtp_test_performed = True
                return self._smtp_blocked_cache
                
            except Exception as e:
                self._smtp_blocked_cache = {
                    "success": False,
                    "blocked": True,
                    "error": f"Socket error: {str(e)}",
                    "error_code": getattr(e, 'errno', 'UNKNOWN'),
                    "test_type": "socket",
                    "recommendations": self._get_blocking_recommendations()
                }
                self._smtp_test_performed = True
                return self._smtp_blocked_cache
            
            # Socket connection successful, test SMTP protocol
            try:
                loop = asyncio.get_event_loop()
                smtp_result = await loop.run_in_executor(None, self._test_smtp_protocol)
                self._smtp_blocked_cache = smtp_result
                self._smtp_test_performed = True
                return smtp_result
                
            except Exception as e:
                self._smtp_blocked_cache = {
                    "success": False,
                    "blocked": self._is_blocking_error(e),
                    "error": f"SMTP protocol test failed: {str(e)}",
                    "error_code": getattr(e, 'errno', 'UNKNOWN'),
                    "test_type": "smtp",
                    "recommendations": self._get_blocking_recommendations() if self._is_blocking_error(e) else []
                }
                self._smtp_test_performed = True
                return self._smtp_blocked_cache
                
        except Exception as e:
            logger.error(f"SMTP connectivity test failed: {str(e)}")
            self._smtp_blocked_cache = {
                "success": False,
                "blocked": self._is_blocking_error(e),
                "error": str(e),
                "error_code": getattr(e, 'errno', 'UNKNOWN'),
                "test_type": "general",
                "recommendations": self._get_blocking_recommendations() if self._is_blocking_error(e) else []
            }
            self._smtp_test_performed = True
            return self._smtp_blocked_cache

    def _test_smtp_protocol(self) -> Dict[str, Any]:
        """
        Test SMTP protocol connectivity (runs in thread pool)
        """
        try:
            timeout = getattr(settings, "EMAIL_SMTP_TIMEOUT", 10)
            
            # Create SMTP connection
            smtp = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=timeout)
            smtp.set_debuglevel(0)
            
            # Test STARTTLS
            smtp.starttls()
            
            # Test authentication (this is where many issues occur)
            smtp.login(self.email_user, self.email_pass)
            
            # Clean disconnect
            smtp.quit()
            
            return {
                "success": True,
                "blocked": False,
                "message": "SMTP connection and authentication successful",
                "test_type": "smtp",
                "host": self.smtp_host,
                "port": self.smtp_port
            }
            
        except smtplib.SMTPAuthenticationError as e:
            return {
                "success": False,
                "blocked": False,  # Auth error, not blocking
                "error": f"SMTP Authentication failed: {str(e)}",
                "error_code": "AUTH_FAILED",
                "test_type": "smtp",
                "recommendations": [
                    "Check if you're using an App Password for Gmail (not your regular password)",
                    "Verify 2FA is enabled on your Gmail account",
                    "Ensure EMAIL_USER and EMAIL_PASS settings are correct",
                    "Check if 'Less secure app access' needs to be enabled (not recommended)"
                ]
            }
            
        except smtplib.SMTPConnectError as e:
            return {
                "success": False,
                "blocked": True,
                "error": f"SMTP Connection failed: {str(e)}",
                "error_code": "CONNECT_FAILED",
                "test_type": "smtp",
                "recommendations": self._get_blocking_recommendations()
            }
            
        except Exception as e:
            return {
                "success": False,
                "blocked": self._is_blocking_error(e),
                "error": f"SMTP test failed: {str(e)}",
                "error_code": getattr(e, 'errno', 'UNKNOWN'),
                "test_type": "smtp",
                "recommendations": self._get_blocking_recommendations() if self._is_blocking_error(e) else []
            }

    def _is_blocking_error(self, error: Exception) -> bool:
        """
        Determine if an error indicates SMTP blocking
        """
        error_no = getattr(error, 'errno', None)
        
        # Common network blocking error codes
        blocking_errors = {
            errno.ENETUNREACH,    # Network unreachable
            errno.EHOSTUNREACH,   # Host unreachable  
            errno.ECONNREFUSED,   # Connection refused
            errno.ETIMEDOUT,      # Connection timed out
            errno.ENETDOWN,       # Network is down
            errno.EHOSTDOWN       # Host is down
        }
        
        if error_no in blocking_errors:
            return True
            
        # Check error message for blocking indicators
        error_str = str(error).lower()
        blocking_keywords = [
            'network is unreachable',
            'connection refused',
            'connection timed out',
            'no route to host',
            'host unreachable',
            'network unreachable'
        ]
        
        return any(keyword in error_str for keyword in blocking_keywords)

    def _get_blocking_recommendations(self) -> List[str]:
        """
        Get recommendations for resolving SMTP blocking
        """
        return [
            "🔥 SMTP appears to be blocked by your hosting provider/network",
            "🌐 Common with cloud providers (AWS, Google Cloud, Azure, DigitalOcean, etc.)",
            "📧 Use a transactional email service instead:",
            "   • SendGrid (recommended for high volume)",
            "   • Mailgun (developer-friendly)",
            "   • Amazon SES (AWS integrated)",
            "   • Postmark (simple, reliable)",
            "   • Resend (modern, developer-focused)",
            "⚙️  Alternative solutions:",
            "   • Use a dedicated SMTP relay service",
            "   • Switch to a VPS/dedicated server with SMTP access",
            "   • Configure your hosting firewall to allow SMTP ports (587, 465, 25)",
            "   • Contact your hosting provider about SMTP restrictions",
            "🔧 For development: Enable EMAIL_TEST_MODE=true to simulate emails"
        ]

    async def send_email(self, 
                        subject: str, 
                        emails: List[str], 
                        body: str, 
                        bcc: List[str] = None,
                        custom: Dict[str, List[str]] = None,
                        attachments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send email to multiple recipients with enhanced blocking detection
        """
        try:
            # Remove duplicates while preserving order
            unique_emails = list(dict.fromkeys(emails))
            unique_bcc = list(dict.fromkeys(bcc)) if bcc else None
            
            # Test mode for development
            if self.test_mode:
                logger.info(f"TEST MODE: Would send email to {unique_emails} with subject '{subject}'")
                result = {
                    "success": True,
                    "sent_count": len(unique_emails),
                    "failed_count": 0,
                    "total_recipients": len(unique_emails),
                    "test_mode": True,
                    "message": "Email simulated successfully (test mode)",
                    "smtp_blocked": False
                }
            else:
                # Check SMTP connectivity first
                connectivity = await self.test_smtp_connectivity()
                
                if connectivity.get("blocked", False):
                    logger.error("SMTP is blocked - cannot send emails")
                    result = {
                        "success": False,
                        "sent_count": 0,
                        "failed_count": len(unique_emails) + (len(unique_bcc) if unique_bcc else 0),
                        "total_recipients": len(unique_emails),
                        "smtp_blocked": True,
                        "connectivity_test": connectivity,
                        "error": "SMTP blocked by hosting provider/network",
                        "recommendations": connectivity.get("recommendations", [])
                    }
                else:
                    # SMTP appears to be available, attempt to send
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, 
                        self._send_smtp_email, 
                        subject, unique_emails, body, unique_bcc, custom, attachments
                    )
            
            # Save email summary to database
            await self._save_email_summary(subject, unique_emails, body, unique_bcc, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Email Service: Error sending email: {str(e)}")
            result = {
                "success": False,
                "error": str(e),
                "sent_count": 0,
                "failed_count": len(emails) + (len(bcc) if bcc else 0),
                "smtp_blocked": self._is_blocking_error(e)
            }
            
            # Save failed email summary
            await self._save_email_summary(subject, emails, body, bcc, result)
            return result

    def _send_smtp_email(self, subject: str, emails: List[str], body: str, bcc: List[str] = None, custom: Dict[str, List[str]] = None, attachments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal method to send email via SMTP with enhanced error handling
        """
        sent_count = 0
        failed_count = 0
        errors = []

        try:
            logger.info(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")
            timeout = getattr(settings, "EMAIL_SMTP_TIMEOUT", 10)

            # Enhanced SMTP connection with better error handling
            try:
                smtp = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=timeout)
            except OSError as e:
                # Enhanced blocking detection
                error_msg = f"SMTP connection failed: {str(e)}"
                smtp_blocked = self._is_blocking_error(e)
                
                if smtp_blocked:
                    error_msg += "\n\n🚫 OUTBOUND SMTP APPEARS TO BE BLOCKED"
                    error_msg += "\n" + "\n".join(self._get_blocking_recommendations())
                
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "sent_count": 0,
                    "failed_count": len(emails) + (len(bcc) if bcc else 0),
                    "smtp_blocked": smtp_blocked,
                    "recommendations": self._get_blocking_recommendations() if smtp_blocked else []
                }
            
            smtp.set_debuglevel(0)
            smtp.starttls()
            smtp.login(self.email_user, self.email_pass)

            # Email sending logic (unchanged from original)
            import re
            import base64
            from email.mime.base import MIMEBase
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email import encoders
            
            pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\[\s*\d+\s*\]\s*\}\}")

            for idx, recipient in enumerate(emails):
                try:
                    all_recipients = [recipient]
                    if bcc:
                        all_recipients.extend(bcc)
                    
                    # Per-recipient placeholder replacement
                    def per_recipient_replace(text: str) -> str:
                        if not text or not custom:
                            return text
                        def replacer(match: re.Match) -> str:
                            key = match.group(1)
                            values = custom.get(key)
                            if isinstance(values, list) and 0 <= idx < len(values):
                                return str(values[idx])
                            return match.group(0)
                        return pattern.sub(replacer, text)

                    rendered_subject = per_recipient_replace(subject)
                    rendered_body = per_recipient_replace(body)

                    # Build MIME message
                    msg = MIMEMultipart()
                    msg['From'] = self.email_from
                    msg['To'] = recipient
                    if bcc:
                        msg['Bcc'] = ', '.join(bcc)
                    msg['Subject'] = rendered_subject

                    msg.attach(MIMEText(rendered_body, 'html', 'utf-8'))

                    # Handle attachments
                    if attachments:
                        for att in attachments:
                            try:
                                filename = att.get('filename') or 'attachment'
                                content_b64 = att.get('content_base64')
                                mime_type = att.get('mime_type', 'application/octet-stream')
                                if not content_b64:
                                    continue
                                main_type, _, sub_type = mime_type.partition('/')
                                part = MIMEBase(main_type, sub_type or 'octet-stream')
                                part.set_payload(base64.b64decode(content_b64))
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                                msg.attach(part)
                            except Exception as att_e:
                                errors.append(f"Attachment error for {recipient}: {str(att_e)}")

                    # Send email
                    smtp.sendmail(self.email_from, all_recipients, msg.as_string())
                    sent_count += 1
                    logger.info(f"Email sent successfully to {recipient}")

                except Exception as e:
                    failed_count += 1
                    error_msg = f"Failed to send to {recipient}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            smtp.quit()

            return {
                "success": sent_count > 0,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_recipients": len(emails),
                "errors": errors,
                "smtp_blocked": False
            }

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed: {str(e)}"
            error_msg += "\n\n🔐 GMAIL AUTHENTICATION ISSUE"
            error_msg += "\n• Use an App Password, not your regular Gmail password"
            error_msg += "\n• Enable 2-Factor Authentication on your Gmail account"
            error_msg += "\n• Generate an App Password in Gmail settings"
            error_msg += "\n• See GMAIL_SETUP_GUIDE.md for detailed instructions"
            
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "sent_count": 0,
                "failed_count": len(emails) + (len(bcc) if bcc else 0),
                "smtp_blocked": False,
                "auth_error": True
            }
            
        except Exception as e:
            smtp_blocked = self._is_blocking_error(e)
            error_msg = f"SMTP error: {str(e)}"
            
            if smtp_blocked:
                error_msg += "\n\n🚫 OUTBOUND SMTP APPEARS TO BE BLOCKED"
                error_msg += "\n" + "\n".join(self._get_blocking_recommendations())
            
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "sent_count": 0,
                "failed_count": len(emails) + (len(bcc) if bcc else 0),
                "smtp_blocked": smtp_blocked,
                "recommendations": self._get_blocking_recommendations() if smtp_blocked else []
            }

    # Keep all existing methods unchanged
    async def _save_email_summary(self, subject: str, emails: List[str], body: str, bcc: List[str] = None, result: Dict[str, Any] = None):
        """Save email summary to database (unchanged)"""
        try:
            from ..models.email_summary import EmailSummary
            from ..core.init_db import get_database
            
            import re
            body_preview = re.sub(r'<[^>]+>', '', body)[:200]
            if len(body_preview) == 200:
                body_preview += "..."
            
            if result and result.get("sent_count", 0) == result.get("total_recipients", 0):
                status = "sent"
            elif result and result.get("sent_count", 0) > 0:
                status = "partial"
            else:
                status = "failed"
            
            email_summary = EmailSummary(
                subject=subject,
                recipients=emails,
                bcc_recipients=bcc,
                body_preview=body_preview,
                success=(status == "sent"),
                sent_count=result.get("sent_count", 0) if result else 0,
                failed_count=result.get("failed_count", 0) if result else 0,
                errors=result.get("errors") if result else None
            )

            engine = get_database()
            await engine.save(email_summary)
            logger.info(f"Email summary saved for subject: '{subject}' with {len(emails)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to save email summary: {str(e)}")

    async def get_email_summaries(self, limit: int = 50, skip: int = 0) -> List:
        """Get email summaries from database (unchanged)"""
        try:
            from ..core.init_db import get_database
            engine = get_database()
            docs = await engine.find(EmailSummary, sort=-(EmailSummary.sent_at))
            summaries = [doc.dict() for doc in docs[skip:skip+limit]]
            return summaries
        except Exception as e:
            logger.error(f"Failed to get email summaries: {str(e)}")
            return []

    async def get_email_summary_stats(self) -> Dict[str, Any]:
        """Get email summary statistics (unchanged)"""
        try:
            from ..core.init_db import get_database
            from datetime import timedelta
            engine = get_database()

            docs = await engine.find(EmailSummary)
            total_emails = len(docs)
            successful_emails = sum(1 for d in docs if d.success)
            failed_emails = sum(1 for d in docs if not d.success and (d.sent_count == 0))
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_emails = sum(1 for d in docs if d.sent_at >= recent_cutoff)
            
            return {
                "total_emails": total_emails,
                "successful_emails": successful_emails,
                "failed_emails": failed_emails,
                "recent_emails_24h": recent_emails,
                "success_rate": (successful_emails / total_emails * 100) if total_emails > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get email summary stats: {str(e)}")
            return {
                "total_emails": 0,
                "successful_emails": 0,
                "failed_emails": 0,
                "recent_emails_24h": 0,
                "success_rate": 0
            }

# Create instance
email_service = EmailService()
