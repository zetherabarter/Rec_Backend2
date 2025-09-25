from typing import Optional, Tuple
from datetime import datetime
from ..models.admin import Admin, AdminCreate, AdminLogin
from ..utils.auth import AuthUtils
from ..core.init_db import get_database

class AdminService:
    """Service class for admin operations"""
    
    @staticmethod
    async def create_admin(admin_data: AdminCreate) -> Admin:
        """Create a new admin user"""
        engine = get_database()
        
        # Check if admin with email already exists
        existing_admin = await engine.find_one(Admin, Admin.email == admin_data.email)
        if existing_admin:
            raise ValueError("Admin with this email already exists")
        
        # Hash the password
        password_hash = AuthUtils.hash_password(admin_data.password)
        
        # Create admin
        admin = Admin(
            name=admin_data.name,
            email=admin_data.email,
            password_hash=password_hash,
            role=admin_data.role
        )
        
        return await engine.save(admin)
    
    @staticmethod
    async def authenticate_admin(login_data: AdminLogin) -> Tuple[bool, Optional[Admin], str]:
        """Authenticate admin user"""
        try:
            engine = get_database()
            
            # Find admin by email
            admin = await engine.find_one(Admin, Admin.email == login_data.email)
            if not admin:
                return False, None, "Invalid email or password"
            
            # Check if admin is active
            if not admin.is_active:
                return False, None, "Account is deactivated"
            
            # Verify password
            if not AuthUtils.verify_password(login_data.password, admin.password_hash):
                return False, None, "Invalid email or password"
            
            # Update last login
            admin.last_login = datetime.utcnow()
            await engine.save(admin)
            
            return True, admin, "Login successful"
            
        except Exception as e:
            return False, None, f"Authentication failed: {str(e)}"
    
    @staticmethod
    async def get_admin(admin_id: str) -> Optional[Admin]:
        """Get admin by ID"""
        try:
            engine = get_database()
            return await engine.find_one(Admin, Admin.id == admin_id)
        except Exception:
            return None
    
    @staticmethod
    async def get_admin_by_email(email: str) -> Optional[Admin]:
        """Get admin by email"""
        try:
            engine = get_database()
            return await engine.find_one(Admin, Admin.email == email)
        except Exception:
            return None
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Tuple[bool, Optional[str], str]:
        """
        Refresh access token for admin using refresh token
        Returns: (success, new_access_token, message)
        """
        try:
            # Verify refresh token
            payload = AuthUtils.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return False, None, "Invalid refresh token"
            
            # Check if the token contains admin_id (admin token) vs user_id (user token)
            admin_id = payload.get("admin_id")
            if not admin_id:
                return False, None, "Invalid admin refresh token"
            
            # Get admin to verify they still exist and are active
            admin = await AdminService.get_admin(admin_id)
            if not admin:
                return False, None, "Admin not found"
            
            if not admin.is_active:
                return False, None, "Admin account is deactivated"
            
            # Generate new access token
            admin_data = {
                "admin_id": str(admin.id),
                "email": admin.email,
                "role": admin.role.value
            }
            
            new_access_token = AuthUtils.create_access_token(admin_data)
            
            return True, new_access_token, "Admin token refreshed successfully"
            
        except Exception as e:
            print(f"Error in admin refresh_access_token: {e}")
            return False, None, "Token refresh failed"
