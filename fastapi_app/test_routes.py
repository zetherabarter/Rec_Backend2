#!/usr/bin/env python3
"""
Test script for new API routes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_attendance_update():
    """Test the attendance update endpoint"""
    print("🧪 Testing Attendance Update Route...")
    
    # Test data
    email = "test@example.com"
    url = f"{BASE_URL}/api/users/{email}/attendance"
    
    # Test updating to present
    payload = {"isPresent": True}
    
    try:
        response = requests.patch(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Attendance update successful!")
        else:
            print("❌ Attendance update failed")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_bulk_slot_assignment():
    """Test the bulk slot assignment endpoint"""
    print("\n🧪 Testing Bulk Slot Assignment Route...")
    
    url = f"{BASE_URL}/api/users/bulk-assign-slots"
    
    # Test data
    payload = {
        "emails": ["user1@example.com", "user2@example.com"],
        "assignedSlot": "Slot A"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Bulk slot assignment successful!")
        else:
            print("❌ Bulk slot assignment failed")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_server_health():
    """Test if server is responding"""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print("❌ Server responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        return False

def main():
    print("🚀 Starting API Route Tests...")
    print("=" * 50)
    
    # Check if server is running
    if not test_server_health():
        print("\n💡 Make sure to start the server with:")
        print("uvicorn app.main:app --reload --port 8000")
        return
    
    # Run tests
    test_attendance_update()
    test_bulk_slot_assignment()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Check the status codes and responses above")
    print("- 401 = Unauthorized (need authentication)")
    print("- 404 = User not found")
    print("- 200 = Success")

if __name__ == "__main__":
    main()