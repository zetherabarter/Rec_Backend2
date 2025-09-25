# routes/settings_routes.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.models.settings import Settings, SettingsUpdate, SettingsResponse
from app.services.settings_service import SettingsService
from app.utils.auth_middleware import get_current_admin

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)

@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """
    Get current settings
    
    Returns:
        SettingsResponse: Current settings with isResultOut status
    """
    try:
        settings = await SettingsService.get_settings()
        
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        return SettingsResponse(
            id=str(settings.id),
            isResultOut=settings.isResultOut
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/toggle-result", response_model=SettingsResponse)
async def toggle_result_status(admin_data=Depends(get_current_admin)):
    """
    Toggle the isResultOut status
    
    Requires admin authentication
    
    Returns:
        SettingsResponse: Updated settings with toggled isResultOut status
    """
    try:
        settings = await SettingsService.toggle_result_status()
        
        if not settings:
            raise HTTPException(status_code=500, detail="Failed to toggle result status")
        
        return SettingsResponse(
            id=str(settings.id),
            isResultOut=settings.isResultOut
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/", response_model=SettingsResponse)
async def update_settings(
    settings_update: SettingsUpdate,
    admin_data=Depends(get_current_admin)
):
    """
    Update settings
    
    Requires admin authentication
    
    Args:
        settings_update: Settings data to update
        
    Returns:
        SettingsResponse: Updated settings
    """
    try:
        settings = await SettingsService.update_settings(settings_update)
        
        if not settings:
            raise HTTPException(status_code=500, detail="Failed to update settings")
        
        return SettingsResponse(
            id=str(settings.id),
            isResultOut=settings.isResultOut
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/result-status", response_model=Dict[str, bool])
async def get_result_status():
    """
    Get only the result status (public endpoint)
    
    Returns:
        Dict with isResultOut boolean value
    """
    try:
        settings = await SettingsService.get_settings()
        
        if not settings:
            return {"isResultOut": False}  # Default to False if no settings exist
        
        return {"isResultOut": settings.isResultOut}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
