# ----------------- Imports -----------------
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from odmantic import Model, Field as OdmanticField
from ..utils.enums import status, TaskStatus, DomainEnum
from enum import Enum

# ----------------- Enums -----------------

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"

class CourseEnum(str, Enum):
    btech = "B-Tech"
    bpharma = "B-Pharma"
    mba = "MBA"
    mca = "MCA"

# ----------------- Pydantic Schemas -----------------

class DomainPreferenceSchema(BaseModel):
    """Schema for domain preferences"""
    name: str
    reason: str

class UserBase(BaseModel):
    """Base user schema"""
    name: str
    email: EmailStr
    personal_email: Optional[EmailStr] = None
    phone: int
    year: int
    lib_id: str
    branch: str
    gender: Optional[GenderEnum] = None
    course: Optional[CourseEnum] = None
    why_ecell: str
    what_motivates_you: Optional[str] = None
    linkedIn: Optional[str] = None
    domains: List[str] = Field(default_factory=list)
    isHosteller: bool = Field(default=True)
    pastAchievement: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    domain_pref_one: DomainPreferenceSchema
    domain_pref_two: DomainPreferenceSchema

class screeningUpdate(BaseModel):
    """Schema for updating screening status"""
    status: str
    datetime: datetime
    remarks: str
    domains: Optional[List[str]] = Field(default=None, description="List of domains to add to user")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [s.value for s in status]:
            raise ValueError(f'Status must be one of: {[s.value for s in status]}')
        return v
    
    @validator('domains')
    def validate_domains(cls, v):
        if v is not None:
            if len(v) != len(set(v)):
                raise ValueError('Duplicate domains are not allowed in the request')
            if any(not domain.strip() for domain in v):
                raise ValueError('Domain names cannot be empty')
        return v

class GDUpdate(BaseModel):
    status: str
    datetime: datetime
    remarks: str
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [s.value for s in status]:
            raise ValueError(f'Status must be one of: {[s.value for s in status]}')
        return v

class PIUpdate(BaseModel):
    status: str
    datetime: datetime
    remarks: str
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [s.value for s in status]:
            raise ValueError(f'Status must be one of: {[s.value for s in status]}')
        return v

class TaskItem(BaseModel):
    domain: str = Field(..., description="Domain for the task")
    url: HttpUrl = Field(..., description="URL for the task submission")
    
    @validator('domain')
    def validate_domain(cls, v):
        if v not in [d.value for d in DomainEnum]:
            raise ValueError(f'Domain must be one of: {[d.value for d in DomainEnum]}')
        return v

class TaskUpdate(BaseModel):
    status: str
    tasks: List[TaskItem] = Field(default_factory=list)
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [ts.value for ts in TaskStatus]:
            raise ValueError(f'Status must be one of: {[ts.value for ts in TaskStatus]}')
        return v

class ShortlistRequest(BaseModel):
    emails: List[EmailStr] = Field(..., description="List of user emails to shortlist/unshortlist")

    class Config:
        schema_extra = {
            "example": {
                "emails": ["user1@example.com", "user2@example.com"]
            }
        }

class TaskStatusUpdate(BaseModel):
    domain: str
    url: HttpUrl
    
    @validator('domain')
    def validate_domain(cls, v):
        if v not in [d.value for d in DomainEnum]:
            raise ValueError(f'Domain must be one of: {[d.value for d in DomainEnum]}')
        return v

class UserResponse(BaseModel):
    """Response schema for user data with more flexible field types"""
    id: str
    name: str
    email: EmailStr
    personal_email: Optional[EmailStr] = None
    phone: int
    year: int
    lib_id: str
    branch: str
    gender: Optional[str] = None  # Use string instead of enum for flexibility
    course: Optional[str] = None  # Use string instead of enum for flexibility
    why_ecell: str
    what_motivates_you: Optional[str] = None
    linkedIn: Optional[str] = None
    domains: List[str] = Field(default_factory=list)
    isHosteller: bool = Field(default=True)
    pastAchievement: Optional[str] = None
    domain_pref_one: Dict[str, Any]
    domain_pref_two: Dict[str, Any]
    screening: Dict[str, Any] = Field(default_factory=dict)
    gd: Dict[str, Any] = Field(default_factory=dict)
    pi: Dict[str, Any] = Field(default_factory=dict)
    task: Dict[str, Any] = Field(default_factory=dict)
    shortlisted: bool = Field(default=False)
    isPresent: bool = Field(default=False)
    assignedSlot: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- Odmantic Model -----------------

class User(Model):
    name: str
    email: str
    personal_email: Optional[str] = OdmanticField(default=None)
    phone: int
    year: int
    lib_id: str
    branch: str
    gender: str  # Male/Female
    course: str  # B-Tech, B-Pharma, MBA, MCA
    why_ecell: str
    what_motivates_you: str
    linkedIn: Optional[str] = OdmanticField(default="")
    domains: List[str] = OdmanticField(default_factory=list)
    domain_pref_one: Dict[str, Any]
    domain_pref_two: Dict[str, Any]
    groupNumber: Optional[int] = OdmanticField(default=None)
    isPresent: bool = OdmanticField(default=False)
    isHosteller: bool = OdmanticField(default=True)
    pastAchievement: Optional[str] = OdmanticField(default=None)
    assignedSlot: Optional[str] = OdmanticField(default=None)
    screening: Dict[str, Any] = OdmanticField(default_factory=dict)
    gd: Dict[str, Any] = OdmanticField(default_factory=dict)
    pi: Dict[str, Any] = OdmanticField(default_factory=dict)
    task: Dict[str, Any] = OdmanticField(default_factory=dict)
    shortlisted: bool = OdmanticField(default=False)

    class Config:
        collection = "users"
