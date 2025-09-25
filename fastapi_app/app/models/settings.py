# models/settings.py

from pydantic import BaseModel
from odmantic import Model, Field as OdmanticField
from typing import Optional

# ----------------- Pydantic Schemas -----------------

class SettingsBase(BaseModel):
    """Base settings schema"""
    isResultOut: bool = False

class SettingsCreate(SettingsBase):
    """Schema for creating settings"""
    pass

class SettingsUpdate(BaseModel):
    """Schema for updating settings"""
    isResultOut: Optional[bool] = None

class SettingsResponse(SettingsBase):
    """Schema for settings response"""
    id: Optional[str] = None

# ----------------- ODMantic Models -----------------

class Settings(Model):
    """Settings model for MongoDB collection"""
    isResultOut: bool = OdmanticField(default=False)
    
    class Config:
        collection = "settings"
