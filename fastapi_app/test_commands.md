# Testing Your New API Routes

## 1. Test Attendance Update Route
**Endpoint:** `PATCH /api/users/{email}/attendance`

### PowerShell/cURL Commands:

```powershell
# Update user attendance to present
Invoke-RestMethod -Uri "http://localhost:8000/api/users/test@example.com/attendance" `
  -Method PATCH `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"isPresent": true}'

# Update user attendance to absent
Invoke-RestMethod -Uri "http://localhost:8000/api/users/test@example.com/attendance" `
  -Method PATCH `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"isPresent": false}'
```

```bash
# Using cURL (if you have it installed)
curl -X PATCH "http://localhost:8000/api/users/test@example.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"isPresent": true}'
```

## 2. Test Bulk Slot Assignment Route
**Endpoint:** `POST /api/users/bulk-assign-slots`

### PowerShell Commands:

```powershell
# Assign slots to multiple users
Invoke-RestMethod -Uri "http://localhost:8000/api/users/bulk-assign-slots" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"emails": ["user1@example.com", "user2@example.com"], "assignedSlot": "Slot A"}'
```

```bash
# Using cURL
curl -X POST "http://localhost:8000/api/users/bulk-assign-slots" \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user1@example.com", "user2@example.com"], "assignedSlot": "Slot A"}'
```

## 3. Test Getting Users (to verify changes)
**Endpoint:** `GET /api/users`

```powershell
# Get all users to see the new fields
Invoke-RestMethod -Uri "http://localhost:8000/api/users" -Method GET
```

## 4. Authentication Required
**Note:** Most endpoints require authentication. You'll need to:

1. First login to get a token:
```powershell
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"email": "admin@example.com", "password": "your_password"}'

$token = $loginResponse.access_token
```

2. Use the token in subsequent requests:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/users/test@example.com/attendance" `
  -Method PATCH `
  -Headers @{
    "Content-Type"="application/json"
    "Authorization"="Bearer $token"
  } `
  -Body '{"isPresent": true}'
```