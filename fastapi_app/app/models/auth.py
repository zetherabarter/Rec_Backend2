# ----------------- Imports -----------------
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from odmantic import Model, Field as OdmanticField

# ----------------- Pydantic Schemas -----------------

class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    """Schema for OTP verification"""
    email: EmailStr
    otp: str

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str

# ----------------- Odmantic Models -----------------

class OTP(Model):
    """ODMantic model for OTP storage"""
    email: str
    otp: str
    created_at: datetime = OdmanticField(default_factory=datetime.utcnow)
    expires_at: datetime
    is_used: bool = OdmanticField(default=False)
    attempts: int = OdmanticField(default=0)
    
    class Config:
        collection = "otps"

class RefreshToken(Model):
    """ODMantic model for refresh tokens"""
    user_id: str
    token: str
    created_at: datetime = OdmanticField(default_factory=datetime.utcnow)
    expires_at: datetime
    is_revoked: bool = OdmanticField(default=False)
    
    class Config:
        collection = "refresh_tokens"
