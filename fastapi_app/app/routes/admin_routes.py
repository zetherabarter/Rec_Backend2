from fastapi import APIRouter, HTTPException, status, Depends
from ..models.admin import AdminCreate, AdminLogin, AdminResponse
from ..models.auth import TokenResponse, RefreshTokenRequest
from ..services.admin_service import AdminService
from ..utils.auth import AuthUtils
from ..utils.auth_middleware import get_current_admin, require_roles
from ..utils.enums import UserRole
from datetime import timedelta
import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/admin", tags=["admin"])

# @router.get("/admin/get", response_model=List[UserResponse])
# async def get_admin_users(current_admin = Depends(require_roles([UserRole.SCREENING, UserRole.SUPERADMIN, UserRole.GDPROCTOR, UserRole.INTERVIEWER]))):
#     """Get all users by admin login (accessible to all authenticated admins)"""
#     try:
#         user_dicts = await UserService.get_users_for_admin()
#         response_users = []
#         for user_dict in user_dicts:
#             response_users.append(UserResponse(**user_dict))
#         return response_users
#     except Exception as e:
#         logging.error(f"Exception in /admin/users: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to get users: {str(e)}"
#         )


@router.post("/create", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: AdminCreate,
    current_admin = Depends(require_roles([UserRole.SUPERADMIN]))
):
    """
    Create a new admin user (SuperAdmin only)
    """
    logger.info(f"🔥 CREATE ADMIN REQUEST - SuperAdmin: {current_admin.email} ({current_admin.id})")
    logger.info(f"🔥 REQUEST DATA: name={admin_data.name}, email={admin_data.email}, role={admin_data.role}")
    
    try:
        logger.info(f"🔥 Calling AdminService.create_admin...")
        created_admin = await AdminService.create_admin(admin_data)
        logger.info(f"🔥 ADMIN CREATED SUCCESSFULLY: {created_admin}")
        
        admin_dict = created_admin.dict()
        admin_dict['id'] = str(created_admin.id)
        logger.info(f"🔥 ADMIN DICT: {admin_dict}")
        
        response = AdminResponse(**admin_dict)
        logger.info(f"🔥 RESPONSE OBJECT: {response}")
        
        return response
    except ValueError as e:
        logger.error(f"🔥 VALUE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🔥 UNEXPECTED ERROR: {str(e)}")
        logger.error(f"🔥 ERROR TYPE: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def admin_login(login_data: AdminLogin):
    """
    Admin login endpoint
    """
    logger.info(f"🔥 ADMIN LOGIN REQUEST - Email: {login_data.email}")
    
    success, admin, message = await AdminService.authenticate_admin(login_data)
    logger.info(f"🔥 AUTHENTICATION RESULT - Success: {success}, Message: {message}")
    
    if not success:
        logger.warning(f"🔥 LOGIN FAILED - Email: {login_data.email}, Reason: {message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    logger.info(f"🔥 LOGIN SUCCESSFUL - Admin: {admin.email} ({admin.id}), Role: {admin.role}")
    
    # Create tokens
    access_token_data = {
        "admin_id": str(admin.id),
        "email": admin.email,
        "role": admin.role.value
    }
    logger.info(f"🔥 TOKEN DATA: {access_token_data}")
    
    access_token = AuthUtils.create_access_token(access_token_data)
    refresh_token = AuthUtils.create_refresh_token(access_token_data)
    logger.info(f"🔥 TOKENS CREATED - Access token length: {len(access_token)}, Refresh token length: {len(refresh_token)}")
    
    response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
    logger.info(f"🔥 LOGIN RESPONSE READY")
    
    return response

@router.post("/refresh", response_model=dict, status_code=status.HTTP_200_OK)
async def refresh_admin_token(refresh_request: RefreshTokenRequest):
    """
    Refresh admin access token using refresh token
    """
    logger.info(f"🔥 ADMIN REFRESH TOKEN REQUEST")
    
    success, new_access_token, message = await AdminService.refresh_access_token(refresh_request.refresh_token)
    
    if not success:
        logger.warning(f"🔥 REFRESH FAILED - Reason: {message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    logger.info(f"🔥 REFRESH SUCCESSFUL")
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "message": message
    }

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin = Depends(get_current_admin)):
    """
    Get current admin information
    """
    logger.info(f"🔥 GET CURRENT ADMIN INFO - Admin: {current_admin.email} ({current_admin.id})")
    
    admin_dict = current_admin.dict()
    admin_dict['id'] = str(current_admin.id)
    logger.info(f"🔥 ADMIN INFO DICT: {admin_dict}")
    
    response = AdminResponse(**admin_dict)
    logger.info(f"🔥 ADMIN INFO RESPONSE READY")
    
    return response
