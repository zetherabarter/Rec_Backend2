"""
Script to create the initial SuperAdmin user
Run this once to set up the first admin user
"""
import asyncio
from app.models.admin import AdminCreate
from app.services.admin_service import AdminService
from app.utils.enums import UserRole
from app.core.init_db import connect_to_mongo, close_mongo_connection

async def create_super_admin():
    """Create the initial SuperAdmin user"""
    await connect_to_mongo()
    
    # SuperAdmin details
    super_admin_data = AdminCreate(
        name="Super Admin",
        email="parle@gmail.com",  # Updated email
        password="12345678",        # Updated password
        role=UserRole.SUPERADMIN
    )
    
    try:
        admin = await AdminService.create_admin(super_admin_data)
        print(f"✅ SuperAdmin created successfully!")
        print(f"Email: {admin.email}")
        print(f"Name: {admin.name}")
        print(f"Role: {admin.role}")
        print(f"ID: {admin.id}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    print("🚀 Creating SuperAdmin user...")
    asyncio.run(create_super_admin())
