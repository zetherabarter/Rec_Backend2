from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from odmantic import Model, Field as OdmanticField
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

# ----------------- Schemas -----------------

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
    gender: Optional[GenderEnum] = None  # Optional for backward compatibility
    course: Optional[CourseEnum] = None  # Optional for backward compatibility
    why_ecell: str
    what_motivates_you: Optional[str] = None  # Optional for backward compatibility
    linkedIn: Optional[str] = None
    domains: List[str] = Field(default_factory=list)
    groupNumber: Optional[int] = None
    isPresent: bool = Field(default=False)
    isHosteller: bool = Field(default=False)
    pastAchievement: Optional[str] = None
    assignedSlot: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    domain_pref_one: DomainPreferenceSchema
    domain_pref_two: DomainPreferenceSchema

class ScreeningUpdate(BaseModel):
    """Schema for updating screening status"""
    status: str
    datetime: datetime
    remarks: str

class GDUpdate(BaseModel):
    """Schema for updating GD status"""
    status: str
    datetime: datetime
    remarks: str

class PIUpdate(BaseModel):
    """Schema for updating PI status"""
    status: str
    datetime: datetime
    remarks: str

class TaskUpdate(BaseModel):
    """Schema for updating task status"""
    status: str
    tasks: List[Dict[str, Any]] = Field(default_factory=list)

class AttendanceUpdate(BaseModel):
    """Schema for updating attendance status"""
    isPresent: bool

class BulkSlotAssignment(BaseModel):
    """Schema for bulk slot assignment"""
    emails: List[EmailStr]
    assignedSlot: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    domain_pref_one: Optional[Dict[str, Any]] = None
    domain_pref_two: Optional[Dict[str, Any]] = None
    screening: Dict[str, Any] = Field(default_factory=dict)
    gd: Dict[str, Any] = Field(default_factory=dict)
    pi: Dict[str, Any] = Field(default_factory=dict)
    task: Dict[str, Any] = Field(default_factory=dict)
    shortlisted: bool = Field(default=False)

    class Config:
        from_attributes = True

# ----------------- Odmantic Model -----------------

class User(Model):
    """Odmantic model for MongoDB"""
    name: str
    email: str = OdmanticField(unique=True)
    personal_email: Optional[str] = OdmanticField(default=None)
    phone: int
    year: int
    lib_id: str
    branch: str
    gender: Optional[str] = OdmanticField(default=None)  # Optional for backward compatibility
    course: Optional[str] = OdmanticField(default=None)  # Optional for backward compatibility
    why_ecell: str
    what_motivates_you: Optional[str] = OdmanticField(default=None)  # Optional for backward compatibility
    linkedIn: Optional[str] = OdmanticField(default="")
    domains: List[str] = OdmanticField(default_factory=list)
    domain_pref_one: Optional[Dict[str, Any]] = OdmanticField(default_factory=dict)
    domain_pref_two: Optional[Dict[str, Any]] = OdmanticField(default_factory=dict)
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
