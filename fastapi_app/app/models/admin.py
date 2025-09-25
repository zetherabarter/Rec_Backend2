# ----------------- Imports -----------------
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from odmantic import Model, Field as OdmanticField
from ..utils.enums import UserRole

# ----------------- Pydantic Schemas -----------------

class AdminCreate(BaseModel):
    """Schema for creating a new admin user"""
    name: str
    email: EmailStr
    password: str
    role: UserRole

class AdminLogin(BaseModel):
    """Schema for admin login"""
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    """Schema for admin response"""
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Odmantic Model -----------------

class Admin(Model):
    """Odmantic model for admin users in MongoDB"""
    name: str
    email: str
    password_hash: str  # Store hashed password
    role: UserRole
    is_active: bool = OdmanticField(default=True)
    created_at: datetime = OdmanticField(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = OdmanticField(default=None)

    class Config:
        collection = "admins"
