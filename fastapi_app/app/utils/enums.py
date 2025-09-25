from enum import Enum

class EmailStatus(str,Enum):
    """Email status enumeration"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"


class status(Enum):
    SELECTED = "selected"
    REJECTED = "rejected"
    UNSURE = "unsure"
    SCHEDULED = "scheduled"
    PENDING = "pending"
    ABSENT = "absent"

class screeningStatus(Enum):
    """screening status enumeration"""
    SELECTED = "selected"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    PENDING = "pending"

class TaskStatus(Enum):
    """Task status enumeration for user tasks"""
    PENDING = "pending"  # Default status
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class UserRole(str, Enum):
    """User role enumeration for authentication and authorization"""
    GDPROCTOR = "GDProctor"
    INTERVIEWER = "Interviewer" 
    SCREENING = "Screening"
    SUPERADMIN = "SuperAdmin"


# Domain enum for user domains
class DomainEnum(str, Enum):
    TECHNICAL = "Technical"
    EVENTS = "Events"
    CORPORATE_RELATIONS = "Corporate Relations"
    PUBLIC_RELATIONS = "Public Relations"
    GRAPHICS = "Graphics"
