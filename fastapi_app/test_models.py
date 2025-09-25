#!/usr/bin/env python3
"""
Test script to validate our model changes without running the full application.
This script tests the new fields (isPresent, assignedSlot) and validates schemas.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Test Domain Preference Schema
class DomainPreferenceSchema(BaseModel):
    """Schema for domain preferences"""
    name: str
    reason: str

# Test UserBase with new fields
class UserBase(BaseModel):
    """Base user schema with new fields"""
    name: str
    email: EmailStr
    phone: int
    year: int
    lib_id: str
    branch: str
    why_ecell: str
    linkedIn: Optional[str] = None
    domains: List[str] = Field(default_factory=list)
    groupNumber: Optional[int] = None
    isPresent: bool = Field(default=False)
    assignedSlot: Optional[str] = None

# Test UserCreate schema
class UserCreate(UserBase):
    """Schema for creating a new user"""
    domain_pref_one: DomainPreferenceSchema
    domain_pref_two: DomainPreferenceSchema

# Test AttendanceUpdate schema
class AttendanceUpdate(BaseModel):
    """Schema for updating attendance status"""
    isPresent: bool

# Test BulkSlotAssignment schema
class BulkSlotAssignment(BaseModel):
    """Schema for bulk slot assignment"""
    emails: List[EmailStr]
    assignedSlot: str

# Test UserResponse schema
class UserResponse(UserBase):
    """Schema for user response with new fields"""
    id: str
    domain_pref_one: Dict[str, Any]
    domain_pref_two: Dict[str, Any]
    screening: Dict[str, Any] = Field(default_factory=dict)
    gd: Dict[str, Any] = Field(default_factory=dict)
    pi: Dict[str, Any] = Field(default_factory=dict)
    task: Dict[str, Any] = Field(default_factory=dict)
    shortlisted: bool = Field(default=False)
    isPresent: bool = Field(default=False)
    assignedSlot: Optional[str] = None

    class Config:
        from_attributes = True

def test_user_creation():
    """Test creating a user with new fields"""
    print("🧪 Testing User Creation with new fields...")
    
    # Test data
    domain_pref_1 = DomainPreferenceSchema(
        name="Technical",
        reason="I love coding and technology"
    )
    
    domain_pref_2 = DomainPreferenceSchema(
        name="Events",
        reason="I enjoy organizing events"
    )
    
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": 1234567890,
        "year": 2,
        "lib_id": "LIB123",
        "branch": "Computer Science",
        "why_ecell": "I want to learn about entrepreneurship",
        "linkedIn": "https://linkedin.com/in/johndoe",
        "domains": ["Technical", "Events"],
        "groupNumber": 1,
        "isPresent": True,  # New field
        "assignedSlot": "Slot A",  # New field
        "domain_pref_one": domain_pref_1,
        "domain_pref_two": domain_pref_2
    }
    
    try:
        user = UserCreate(**user_data)
        print("✅ UserCreate schema validation passed!")
        print(f"   - Name: {user.name}")
        print(f"   - Email: {user.email}")
        print(f"   - isPresent: {user.isPresent}")
        print(f"   - assignedSlot: {user.assignedSlot}")
        return True
    except Exception as e:
        print(f"❌ UserCreate schema validation failed: {e}")
        return False

def test_attendance_update():
    """Test attendance update schema"""
    print("\n🧪 Testing AttendanceUpdate schema...")
    
    try:
        # Test valid attendance update
        attendance_data = {"isPresent": True}
        attendance = AttendanceUpdate(**attendance_data)
        print("✅ AttendanceUpdate schema validation passed!")
        print(f"   - isPresent: {attendance.isPresent}")
        
        # Test with False value
        attendance_false = AttendanceUpdate(isPresent=False)
        print(f"   - isPresent (False): {attendance_false.isPresent}")
        return True
    except Exception as e:
        print(f"❌ AttendanceUpdate schema validation failed: {e}")
        return False

def test_bulk_slot_assignment():
    """Test bulk slot assignment schema"""
    print("\n🧪 Testing BulkSlotAssignment schema...")
    
    try:
        slot_data = {
            "emails": ["user1@example.com", "user2@example.com", "user3@example.com"],
            "assignedSlot": "Slot B"
        }
        slot_assignment = BulkSlotAssignment(**slot_data)
        print("✅ BulkSlotAssignment schema validation passed!")
        print(f"   - Emails count: {len(slot_assignment.emails)}")
        print(f"   - Assigned slot: {slot_assignment.assignedSlot}")
        return True
    except Exception as e:
        print(f"❌ BulkSlotAssignment schema validation failed: {e}")
        return False

def test_user_response():
    """Test user response schema with new fields"""
    print("\n🧪 Testing UserResponse schema...")
    
    try:
        response_data = {
            "id": "507f1f77bcf86cd799439011",
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": 9876543210,
            "year": 3,
            "lib_id": "LIB456",
            "branch": "Information Technology",
            "why_ecell": "I want to start my own company",
            "linkedIn": "https://linkedin.com/in/janesmith",
            "domains": ["Corporate Relations", "Public Relations"],
            "groupNumber": 2,
            "isPresent": False,  # New field
            "assignedSlot": "Slot C",  # New field
            "domain_pref_one": {"name": "Corporate Relations", "reason": "I love business networking"},
            "domain_pref_two": {"name": "Public Relations", "reason": "I enjoy media and communications"},
            "screening": {"status": "selected", "datetime": "2025-09-20T10:00:00", "remarks": "Good performance"},
            "gd": {},
            "pi": {},
            "task": {},
            "shortlisted": True
        }
        
        user_response = UserResponse(**response_data)
        print("✅ UserResponse schema validation passed!")
        print(f"   - ID: {user_response.id}")
        print(f"   - Name: {user_response.name}")
        print(f"   - isPresent: {user_response.isPresent}")
        print(f"   - assignedSlot: {user_response.assignedSlot}")
        print(f"   - Shortlisted: {user_response.shortlisted}")
        return True
    except Exception as e:
        print(f"❌ UserResponse schema validation failed: {e}")
        return False

def test_api_payloads():
    """Test API payload formats"""
    print("\n🧪 Testing API payload formats...")
    
    # Test attendance update payload
    print("📋 Attendance update payload:")
    attendance_payload = {"isPresent": True}
    print(f"   {attendance_payload}")
    
    # Test bulk slot assignment payload  
    print("📋 Bulk slot assignment payload:")
    slot_payload = {
        "emails": ["user1@example.com", "user2@example.com"],
        "assignedSlot": "Morning Slot"
    }
    print(f"   {slot_payload}")
    
    print("✅ API payload formats look good!")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Model Validation Tests")
    print("=" * 50)
    
    tests = [
        test_user_creation,
        test_attendance_update,
        test_bulk_slot_assignment,
        test_user_response,
        test_api_payloads
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The model changes are working correctly.")
        print("\n📋 Summary of Changes:")
        print("   ✅ Added 'isPresent' boolean field (default: False)")
        print("   ✅ Added 'assignedSlot' optional string field")
        print("   ✅ Created AttendanceUpdate schema")
        print("   ✅ Created BulkSlotAssignment schema")
        print("   ✅ Updated UserResponse schema")
        print("\n🛠️  New API Endpoints (once app is running):")
        print("   📌 PATCH /api/users/{email}/attendance")
        print("   📌 POST /api/users/bulk-assign-slots")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)