# services/settings_service.py

from typing import Optional
from app.models.settings import Settings, SettingsCreate, SettingsUpdate
from app.core.init_db import database
from odmantic import ObjectId

class SettingsService:
    """Service class for settings operations"""
    
    @staticmethod
    async def get_settings() -> Optional[Settings]:
        """Get the current settings (there should only be one document)"""
        try:
            settings = await database.engine.find_one(Settings)
            if not settings:
                # If no settings exist, create default settings
                default_settings = Settings(isResultOut=False)
                settings = await database.engine.save(default_settings)
            return settings
        except Exception as e:
            print(f"Error getting settings: {e}")
            return None
    
    @staticmethod
    async def update_settings(settings_update: SettingsUpdate) -> Optional[Settings]:
        """Update settings"""
        try:
            # Get existing settings or create default
            current_settings = await SettingsService.get_settings()
            
            if not current_settings:
                # Create new settings if none exist
                settings_data = settings_update.dict(exclude_unset=True)
                new_settings = Settings(**settings_data)
                return await database.engine.save(new_settings)
            
            # Update existing settings
            update_data = settings_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(current_settings, field, value)
            
            return await database.engine.save(current_settings)
            
        except Exception as e:
            print(f"Error updating settings: {e}")
            return None
    
    @staticmethod
    async def toggle_result_status() -> Optional[Settings]:
        """Toggle the isResultOut status"""
        try:
            current_settings = await SettingsService.get_settings()
            
            if not current_settings:
                # Create new settings with isResultOut=True if none exist
                new_settings = Settings(isResultOut=True)
                return await database.engine.save(new_settings)
            
            # Toggle the current status
            current_settings.isResultOut = not current_settings.isResultOut
            return await database.engine.save(current_settings)
            
        except Exception as e:
            print(f"Error toggling result status: {e}")
            return None
