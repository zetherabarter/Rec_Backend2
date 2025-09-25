from fastapi import APIRouter, HTTPException, status, Depends
from ..models.auth import LoginRequest, OTPVerifyRequest, TokenResponse, RefreshTokenRequest
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest):
    """
    Login endpoint - sends OTP to user's email if user exists
    """
    success, message = await AuthService.login(login_request)
    
    if not success:
        if "not found" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    
    return {"message": message}

@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_otp(verify_request: OTPVerifyRequest):
    """
    Verify OTP and return access and refresh tokens
    """
    success, token_response, message = await AuthService.verify_otp(verify_request)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return token_response

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    success, new_access_token, message = await AuthService.refresh_access_token(
        refresh_request.refresh_token
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "message": message
    }

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(refresh_request: RefreshTokenRequest):
    """
    Logout user by revoking refresh token
    """
    success = await AuthService.revoke_refresh_token(refresh_request.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout"
        )
    
    return {"message": "Logged out successfully"}
