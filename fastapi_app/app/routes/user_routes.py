from fastapi import APIRouter, HTTPException, status, Depends, Body
from typing import List
from ..schemas.user_schema import (
    UserCreate, UserResponse, screeningUpdate,
    GDUpdate, PIUpdate, TaskUpdate, ShortlistRequest, TaskStatusUpdate
)
from ..models.user import AttendanceUpdate, BulkSlotAssignment
from ..services.user_service import UserService
from ..core.init_db import get_database

# Inline schema for bulk round update (no extra packages)
from pydantic import BaseModel, EmailStr, validator, Field
from typing import List, Optional
from datetime import datetime
from ..utils.enums import status as StatusEnum, TaskStatus, DomainEnum

class BulkRoundUpdateRequest(BaseModel):
    emails: List[EmailStr]
    screening: Optional[dict] = None  # {"status": str, "datetime": datetime}
    gd: Optional[dict] = None         # {"status": str, "datetime": datetime, "remarks": str}
    pi: Optional[dict] = None         # {"status": str, "datetime": datetime, "remarks": list}
    
    @validator('screening')
    def validate_screening_status(cls, v):
        """Validate screening status if provided"""
        if v and 'status' in v:
            status_value = v['status']
            if status_value not in [s.value for s in StatusEnum]:
                raise ValueError(f'Screening status must be one of: {[s.value for s in StatusEnum]}')
        return v
    
    @validator('gd')
    def validate_gd_status(cls, v):
        """Validate GD status if provided"""
        if v and 'status' in v:
            status_value = v['status']
            if status_value not in [s.value for s in StatusEnum]:
                raise ValueError(f'GD status must be one of: {[s.value for s in StatusEnum]}')
        return v
    
    @validator('pi')
    def validate_pi_status(cls, v):
        """Validate PI status if provided"""
        if v and 'status' in v:
            status_value = v['status']
            if status_value not in [s.value for s in StatusEnum]:
                raise ValueError(f'PI status must be one of: {[s.value for s in StatusEnum]}')
        return v



# ...existing code...

from ..utils.auth_middleware import get_current_user, get_current_user_optional, require_roles
from ..models.user import User
from ..utils.enums import UserRole
import logging

router = APIRouter(prefix="/users", tags=["users"])

# ...existing route definitions...

from fastapi.responses import JSONResponse

class BulkUpdateResponse(BaseModel):
    updated: List[EmailStr]
    failed: List[dict]

class ChangeGroupResponse(BaseModel):
    updated: List[EmailStr]
    failed: List[dict]
    targetGroupNumber: int
    schedulingTimes: dict
    
    class Config:
        schema_extra = {
            "example": {
                "updated": ["user1@example.com", "user2@example.com"],
                "failed": [],
                "targetGroupNumber": 5,
                "schedulingTimes": {
                    "gdTime": "2025-09-05T17:00:00",
                    "screeningTime": "2025-09-05T17:10:00", 
                    "piTime": "2025-09-05T17:20:00"
                }
            }
        }

class MarkAbsentRequest(BaseModel):
    emails: List[EmailStr]
    
    class Config:
        schema_extra = {
            "example": {
                "emails": ["user1@example.com", "user2@example.com", "user3@example.com"]
            }
        }

class ChangeGroupRequest(BaseModel):
    emails: List[EmailStr]
    targetGroupNumber: int
    
    class Config:
        schema_extra = {
            "example": {
                "emails": ["user1@example.com", "user2@example.com"],
                "targetGroupNumber": 5
            }
        }

class BulkCreateRoundsRequest(BaseModel):
    emails: List[EmailStr]
    batchSize: int = Field(gt=0, description="Number of users per batch")
    startDate: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$', description="Start date in YYYY-MM-DD format")
    startTime: str = Field(pattern=r'^\d{2}:\d{2}$', description="Start time in HH:MM format")
    endTime: str = Field(pattern=r'^\d{2}:\d{2}$', description="End time in HH:MM format")
    roundDuration: int = Field(gt=0, description="Duration of each round in minutes")
    
    @validator('startTime', 'endTime')
    def validate_time_format(cls, v):
        """Validate time format"""
        try:
            hours, minutes = map(int, v.split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError('Invalid time format')
            return v
        except:
            raise ValueError('Time must be in HH:MM format')
    
    @validator('endTime')
    def validate_end_after_start(cls, v, values):
        """Validate that end time is after start time"""
        if 'startTime' in values:
            start_hours, start_minutes = map(int, values['startTime'].split(':'))
            end_hours, end_minutes = map(int, v.split(':'))
            start_total = start_hours * 60 + start_minutes
            end_total = end_hours * 60 + end_minutes
            if end_total <= start_total:
                raise ValueError('End time must be after start time')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "emails": ["one@gmail.com", "two@gmail.com"],
                "batchSize": 2,
                "startDate": "2025-09-05",
                "startTime": "17:00",
                "endTime": "21:00",
                "roundDuration": 10
            }
        }

class BatchInfo(BaseModel):
    batchNumber: int
    groupNumber: int
    users: List[EmailStr]
    gdTime: str
    screeningTime: str
    interviewTime: str
    date: str

class BulkCreateRoundsResponse(BaseModel):
    totalUsersScheduled: int
    totalBatches: int
    batches: List[BatchInfo]
    failed: List[dict] = Field(default_factory=list)


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Validate domains
    allowed_domains = [d.value for d in DomainEnum]
    invalid_domains = [d for d in user.domains if d not in allowed_domains]
    if invalid_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid domains: {invalid_domains}. Allowed domains are: {allowed_domains}"
        )
    # Check for duplicate email
    existing_user = await UserService.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    try:
        created_user = await UserService.create_user(user)
        # Convert ODMantic model to dict and convert ObjectId to string
        user_dict = created_user.dict()
        user_dict['id'] = str(created_user.id)  # Convert ObjectId to string
        return UserResponse(**user_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/get", response_model=List[UserResponse])
async def get_admin_users(current_admin = Depends(require_roles([UserRole.SCREENING, UserRole.SUPERADMIN, UserRole.GDPROCTOR, UserRole.INTERVIEWER]))):
    """Get all users - admin endpoint"""
    try:
        users = await UserService.get_users_for_admin()
        # Users are already formatted as dicts with string IDs
        response_users = []
        for user_dict in users:
            response_users.append(UserResponse(**user_dict))
        return response_users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.get("/{email}", response_model=UserResponse)
async def get_user(email: str, current_user: User = Depends(get_current_user)):
    """Get user by email (requires authentication)"""
    try:
        user = await UserService.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        # Convert ODMantic model to response schema
        user_dict = user.dict()
        user_dict['id'] = str(user.id)  # Convert ObjectId to string
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user: {str(e)}"
        )


@router.get("/admin/{email}", response_model=UserResponse)
async def get_user(email: str, current_admin = Depends(require_roles([UserRole.SCREENING, UserRole.SUPERADMIN, UserRole.GDPROCTOR, UserRole.INTERVIEWER]))):
    """Get user by email (requires authentication)"""
    try:
        user = await UserService.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        # Convert ODMantic model to response schema
        user_dict = user.dict()
        user_dict['id'] = str(user.id)  # Convert ObjectId to string
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user: {str(e)}"
        )



@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user)):
    """Get all users (accessible to all authenticated users and admins)"""
    try:
        users = await UserService.get_users()
        # Convert each ODMantic model to response schema
        response_users = []
        for user in users:
            user_dict = user.dict()
            user_dict['id'] = str(user.id)  # Convert ObjectId to string
            response_users.append(UserResponse(**user_dict))
        return response_users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )



@router.get("/group/{group_number}", response_model=List[UserResponse])
async def get_users_by_group(
    group_number: int, 
    current_admin = Depends(require_roles([UserRole.SCREENING, UserRole.SUPERADMIN, UserRole.GDPROCTOR, UserRole.INTERVIEWER]))
):
    """Get all users by group number (requires authentication)"""
    try:
        users = await UserService.get_users_by_group(group_number)
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No users found in group {group_number}"
            )
        
        # Convert each ODMantic model to response schema
        response_users = []
        for user in users:
            user_dict = user.dict()
            user_dict['id'] = str(user.id)  # Convert ObjectId to string
            response_users.append(UserResponse(**user_dict))
        return response_users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users by group: {str(e)}"
        )

@router.put("/{email}/screening", response_model=UserResponse)
async def update_screening(email: str, update: screeningUpdate, current_admin = Depends(require_roles([UserRole.SCREENING, UserRole.SUPERADMIN]))):
    """Update user's screening status and optionally add domains"""
    try:
        
        if not current_admin:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unauthenticated"
            )
        
        user = await UserService.update_screening_by_email(email, update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except ValueError as e:
        # Handle domain duplicate errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update screening: {str(e)}"
        )

@router.put("/{email}/gd", response_model=UserResponse )
async def update_gd(email: str, update: GDUpdate, current_admin = Depends(require_roles([UserRole.GDPROCTOR, UserRole.SUPERADMIN]))):
    """Update user's GD status"""
    try:
        user = await UserService.update_gd_by_email(email, update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update GD status: {str(e)}"
        )

@router.put("/{email}/pi", response_model=UserResponse)
async def update_pi(email: str, update: PIUpdate, current_admin = Depends(require_roles([UserRole.INTERVIEWER, UserRole.SUPERADMIN]))):
    """Update user's PI status"""
    try:
        user = await UserService.update_pi_by_email(email, update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update PI status: {str(e)}"
        )

@router.put("/{email}/task", response_model=UserResponse)
async def update_task(email: str, update: TaskUpdate, current_user: User = Depends(get_current_user)):
    """Update user's task status and tasks. Adds new tasks or updates existing ones based on domain."""
    try:
        # Validate that all task URLs are allowed types
        allowed_domains = [
            "docs.google.com",
            "drive.google.com",
            "github.com",
            "canva.com",
            "figma.com",
            "youtube.com"
        ]
        for task in update.tasks:
            url_str = str(task.url)
            if not any(domain in url_str for domain in allowed_domains):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task submission link for domain '{task.domain}' must be a Google Docs, Google Drive, GitHub, Canva, Figma, or YouTube link."
                )
        user = await UserService.update_task_by_email(email, update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update task status: {str(e)}"
        )

@router.put(
    "/bulk/update-rounds",
    response_model=BulkUpdateResponse,
)
async def bulk_update_rounds(
    payload: BulkRoundUpdateRequest = Body(
        ...,
        example={
            "emails": ["user1@example.com", "user2@example.com"],
            "screening": {"status": "passed", "datetime": "2025-08-24T10:00:00", "remarks": "To be scheduled"},
            "gd": {"status": "pending", "datetime": "2025-08-25T14:00:00", "remarks": "To be scheduled"},
            "pi": {"status": "not started", "datetime": "2025-08-26T16:00:00", "remarks": "To be scheduled"}
        }
    ),
    current_admin = Depends(require_roles([UserRole.SUPERADMIN]))
):
    """
    Bulk update screening, gd, and pi rounds for multiple users by email.
    - **emails**: List of user emails to update
    - **screening**: Dict with status and datetime (optional)
    - **gd**: Dict with status, datetime, remarks (optional)
    - **pi**: Dict with status, datetime, remarks (optional)
    """
    updated = []
    failed = []
    for email in payload.emails:
        user = await UserService.get_user_by_email(email)
        if not user:
            failed.append({"email": email, "reason": "User not found"})
            continue
        try:
            if payload.screening:
                user.screening = payload.screening
            if payload.gd:
                user.gd = payload.gd
            if payload.pi:
                user.pi = payload.pi
            engine = UserService.get_engine()
            await engine.save(user)
            updated.append(email)
        except Exception as e:
            failed.append({"email": email, "reason": str(e)})
    return BulkUpdateResponse(updated=updated, failed=failed)

@router.put(
    "/bulk/mark-absent",
    response_model=BulkUpdateResponse,
)
async def mark_users_absent(
    payload: MarkAbsentRequest = Body(
        ...,
        example={
            "emails": ["user1@example.com", "user2@example.com"]
        }
    ),
    current_admin = Depends(require_roles([UserRole.SUPERADMIN, UserRole.GDPROCTOR]))
):
    """
    Mark multiple users as absent in all three rounds (Screening, GD, PI).
    - **emails**: List of user emails to mark as absent
    
    This will set the status to 'absent' for screening, gd, and pi rounds for all specified users.
    """
    updated = []
    failed = []
    
    for email in payload.emails:
        try:
            user = await UserService.get_user_by_email(email)
            if not user:
                failed.append({"email": email, "reason": "User not found"})
                continue
            
            # Set all three rounds to absent status
            # Keep existing datetime and remarks if they exist, or set default values
            user.screening = {
                "status": "absent",
                "datetime": user.screening.get("datetime") if user.screening else None,
                "remarks": user.screening.get("remarks") if user.screening else "Marked absent"
            }
            
            user.gd = {
                "status": "absent", 
                "datetime": user.gd.get("datetime") if user.gd else None,
                "remarks": user.gd.get("remarks") if user.gd else "Marked absent"
            }
            
            user.pi = {
                "status": "absent",
                "datetime": user.pi.get("datetime") if user.pi else None, 
                "remarks": user.pi.get("remarks") if user.pi else ["Marked absent"]
            }
            
            engine = UserService.get_engine()
            await engine.save(user)
            updated.append(email)
            
        except Exception as e:
            failed.append({"email": email, "reason": str(e)})
    
    return BulkUpdateResponse(updated=updated, failed=failed)

@router.put(
    "/bulk/change-group",
    response_model=ChangeGroupResponse,
)
async def change_users_group(
    payload: ChangeGroupRequest = Body(
        ...,
        example={
            "emails": ["user1@example.com", "user2@example.com"],
            "targetGroupNumber": 5
        }
    ),
    current_admin = Depends(require_roles([UserRole.SUPERADMIN, UserRole.SCREENING, UserRole.GDPROCTOR]))
):
    """
    Change group number for multiple users to an existing group and update their scheduling times.
    - **emails**: List of user emails to move to the target group
    - **targetGroupNumber**: The existing group number to move users to
    
    This will:
    1. Verify the target group exists
    2. Copy scheduling times from the target group
    3. Update group number and times for all specified users
    """
    try:
        result = await UserService.change_user_groups(payload.emails, payload.targetGroupNumber)
        return ChangeGroupResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change user groups: {str(e)}"
        )

@router.post(
    "/bulk/create-rounds",
    response_model=BulkCreateRoundsResponse,
)
async def bulk_create_rounds(
    payload: BulkCreateRoundsRequest = Body(
        ...,
        example={
            "emails": ["one@gmail.com", "two@gmail.com"],
            "batchSize": 2,
            "startDate": "2025-09-05",
            "startTime": "17:00",
            "endTime": "21:00",
            "roundDuration": 10
        }
    ),
    current_admin = Depends(require_roles([UserRole.SUPERADMIN, UserRole.SCREENING]))
):
    """
    Bulk create and schedule rounds for multiple users.
    
    **Logic:**
    1. Fetch users by the given emails
    2. Assign them to new groups with auto-incremented groupNumber
    3. Randomly distribute users into batches of batchSize
    4. For each batch:
       - Schedule GD at the given startTime
       - Schedule Screening exactly roundDuration minutes after GD
       - Schedule Interview exactly roundDuration minutes after Screening
    5. Keep creating batches until endTime is reached
    6. If batches spill beyond endTime, continue from next day (skipping Sundays)
    7. Update user status to "scheduled" for all rounds
    
    **Parameters:**
    - **emails**: List of user emails to schedule
    - **batchSize**: Number of users per batch
    - **startDate**: Start date in YYYY-MM-DD format
    - **startTime**: Start time in HH:MM format
    - **endTime**: End time in HH:MM format  
    - **roundDuration**: Duration of each round in minutes
    
    **Example:**
    For input with 2 users, batchSize=2, duration=10min:
    - Batch 1: GD→17:00, Screening→17:10, Interview→17:20
    - Users get groupNumber and status="scheduled"
    """
    try:
        result = await UserService.bulk_create_rounds(
            emails=payload.emails,
            batch_size=payload.batchSize,
            start_date=payload.startDate,
            start_time=payload.startTime,
            end_time=payload.endTime,
            round_duration=payload.roundDuration
        )
        
        return BulkCreateRoundsResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bulk rounds: {str(e)}"
        )



# ================== ROLE-BASED ENDPOINTS ==================

@router.put("/{email}/screening", response_model=UserResponse)
async def update_user_screening_by_role(
    email: str, 
    update: screeningUpdate,
    current_admin = Depends(require_roles([UserRole.SCREENING, UserRole.SUPERADMIN]))
):
    """
    Update user's screening status and optionally add domains (Screening role and SuperAdmin only)
    """
    try:
        user = await UserService.update_screening_by_email(email, update)

        logging.info(f"update_user_screening_by_role called by admin: {getattr(current_admin, 'email', str(current_admin))}")
        
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except ValueError as e:
        # Handle domain duplicate errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update screening status: {str(e)}"
        )

@router.put("/{email}/gd", response_model=UserResponse)
async def update_user_gd_by_role(
    email: str, 
    update: GDUpdate,
    current_admin = Depends(require_roles([UserRole.GDPROCTOR, UserRole.SUPERADMIN]))
):
    """
    Update user's GD status (GDProctor and SuperAdmin only)
    """
    try:
        user = await UserService.update_gd_by_email(email, update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update GD status: {str(e)}"
        )

@router.put("/{email}/pi", response_model=UserResponse)
async def update_user_pi_by_role(
    email: str, 
    update: PIUpdate,
    current_admin = Depends(require_roles([UserRole.INTERVIEWER, UserRole.SUPERADMIN]))
):
    """
    Update user's PI status (Interviewer and SuperAdmin only)
    """
    try:
        user = await UserService.update_pi_by_email(email, update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update PI status: {str(e)}"
        )

# Shortlist functionality routes
@router.post("/shortlist", response_model=dict)
async def toggle_shortlist_users(
    request: ShortlistRequest,
    current_admin = Depends(require_roles([UserRole.SUPERADMIN]))
):
    """Toggle shortlist status for multiple users. Creates tasks for shortlisted users, removes for un-shortlisted."""
    try:
        result = await UserService.toggle_shortlist_users(request.emails)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to toggle shortlist status: {str(e)}"
        )

@router.put("/{email}/task-status", response_model=UserResponse)
async def update_task_status(
    email: str, 
    task_update: TaskStatusUpdate, 
    current_user: User = Depends(get_current_user)
):
    """Update specific task status to completed and add URL for shortlisted users."""
    try:
        # Check if the logged-in user can only update their own tasks
        if current_user.email != email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own tasks"
            )
        
        user = await UserService.update_task_status_by_email(email, task_update)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = user.dict()
        user_dict['id'] = str(user.id)
        return UserResponse(**user_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update task status: {str(e)}"
        )

@router.post("/migrate/add-shortlisted", response_model=dict)
async def migrate_add_shortlisted_field(
    current_admin = Depends(require_roles([UserRole.SUPERADMIN]))
):
    """Migration endpoint to add shortlisted field to all existing users (SuperAdmin only)"""
    try:
        result = await UserService.migrate_add_shortlisted_field()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )

@router.patch("/{email}/attendance", response_model=UserResponse)
async def update_user_attendance(
    email: str,
    attendance_update: dict = Body(..., example={"isPresent": True}),
    current_admin = Depends(require_roles([UserRole.SUPERADMIN, UserRole.SCREENING, UserRole.GDPROCTOR, UserRole.INTERVIEWER]))
):
    """Update user's attendance status by email"""
    try:
        is_present = attendance_update.get("isPresent")
        if is_present is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="isPresent field is required"
            )
        
        updated_user = await UserService.update_attendance_by_email(email, is_present)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Convert ObjectId to string for response
        user_dict = updated_user.dict()
        user_dict["id"] = str(updated_user.id)
        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update attendance: {str(e)}"
        )

@router.post("/bulk-assign-slots", response_model=dict)
async def bulk_assign_slots(
    assignment_request: dict = Body(..., example={"emails": ["user1@example.com", "user2@example.com"], "assignedSlot": "Slot A"}),
    current_admin = Depends(require_roles([UserRole.SUPERADMIN]))
):
    """Assign slots to multiple users in bulk (SuperAdmin only)"""
    try:
        emails = assignment_request.get("emails", [])
        assigned_slot = assignment_request.get("assignedSlot")
        
        if not emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="emails field is required and must not be empty"
            )
        
        if not assigned_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="assignedSlot field is required"
            )
        
        result = await UserService.bulk_assign_slots(emails, assigned_slot)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to assign slots: {str(e)}"
        )