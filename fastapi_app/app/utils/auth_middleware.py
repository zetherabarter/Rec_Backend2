from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List

from ..utils.auth import AuthUtils
from ..services.user_service import UserService
from ..services.admin_service import AdminService
from ..utils.enums import UserRole

# Create security scheme
security = HTTPBearer()

import logging

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logging.info(f"[AUTH] Raw token: {credentials.credentials}")
        payload = AuthUtils.verify_token(credentials.credentials)
        logging.info(f"[AUTH] Decoded payload: {payload}")
        if payload is None or payload.get("type") != "access":
            logging.warning("[AUTH] Invalid or missing payload/type in token.")
            raise credentials_exception

        # Prefer user_id for normal user tokens
        user_id: str = payload.get("user_id")
        if user_id:
            logging.info(f"[AUTH] Extracted user_id: {user_id}")
            user = await UserService.get_user(user_id)
            logging.info(f"[AUTH] User found: {user}")
            if user is None:
                logging.warning("[AUTH] No user found for user_id from token.")
                raise credentials_exception
            return user

        # If there's no user_id, accept admin tokens by falling back to admin_id/email
        admin_id: str = payload.get("admin_id")
        admin_email: str = payload.get("email")
        logging.info(f"[AUTH] Extracted admin_id: {admin_id}, admin_email: {admin_email}")
        if admin_id or admin_email:
            # Verify admin exists
            admin = None
            if admin_email:
                admin = await AdminService.get_admin_by_email(admin_email)
            elif admin_id:
                admin = await AdminService.get_admin(admin_id)

            if admin is None:
                logging.warning("[AUTH] No admin found for admin credentials in token.")
                raise credentials_exception

            # Return a simple proxy object that has at least 'email' and 'role' attributes so
            # routes depending on a User can still access minimal identity info. Routes that
            # expect full User-specific fields should still fail intentionally.
            class _AdminProxy:
                def __init__(self, admin):
                    self.email = admin.email
                    # give a role-like attribute to let role checks operate if needed
                    self.role = admin.role

                def dict(self):
                    return {"email": self.email, "role": self.role}

            return _AdminProxy(admin)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[AUTH] Exception in get_current_user: {e}")
        raise credentials_exception

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated admin from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = AuthUtils.verify_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            raise credentials_exception
        
        admin_id: str = payload.get("admin_id")
        admin_email: str = payload.get("email")
        if admin_id is None:
            raise credentials_exception
        
        if admin_email is None:
            raise credentials_exception
            
        # Get admin from database
        admin = await AdminService.get_admin_by_email(admin_email)
        
        if admin is None:
            raise credentials_exception
            
        return admin
        
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency factory to create role-based authorization
    """
    async def role_checker(current_admin = Depends(get_current_admin)):
        if current_admin.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_admin
    return role_checker

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    """
    Optional dependency to get current user (for endpoints that work with or without auth)
    """
    if credentials is None:
        return None
    
    try:
        payload = AuthUtils.verify_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            return None

        # Try user token first
        user_id: str = payload.get("user_id")
        if user_id:
            try:
                user = await UserService.get_user(user_id)
                return user
            except Exception:
                return None

        # Fallback to admin token — return proxy admin as optional current user
        admin_id: str = payload.get("admin_id")
        admin_email: str = payload.get("email")
        if admin_id or admin_email:
            admin = None
            try:
                if admin_email:
                    admin = await AdminService.get_admin_by_email(admin_email)
                elif admin_id:
                    admin = await AdminService.get_admin(admin_id)
            except Exception:
                admin = None

            if admin:
                class _AdminProxy:
                    def __init__(self, admin):
                        self.email = admin.email
                        self.role = admin.role

                    def dict(self):
                        return {"email": self.email, "role": self.role}

                return _AdminProxy(admin)

        return None
        
    except Exception:
        return None
