# Authentication Setup Guide

## Overview
The backend now handles user authentication with email and password, replacing Firebase Auth.

## Backend Changes

### 1. Authentication Endpoints

#### Register User
- **Endpoint**: `POST /api/auth/register`
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "display_name": "User Name" (optional),
  "phone": "+1234567890" (optional)
}
```
- **Response** (201):
```json
{
  "message": "User registered successfully",
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "User Name",
    "phone": "+1234567890",
    "created_at": "2025-10-28T12:00:00",
    "is_active": true,
    "joined_group_ids": []
  }
}
```

#### Login User
- **Endpoint**: `POST /api/auth/login`
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **Response** (200):
```json
{
  "message": "Login successful",
  "access_token": "jwt_token_here",
  "user": { /* same as register */ }
}
```

#### Get Profile
- **Endpoint**: `GET /api/auth/profile`
- **Headers**: `Authorization: Bearer {token}`
- **Response** (200):
```json
{
  "user": { /* user object */ }
}
```

#### Update Profile
- **Endpoint**: `PUT /api/auth/profile`
- **Headers**: `Authorization: Bearer {token}`
- **Body**:
```json
{
  "display_name": "New Name",
  "phone": "+1234567890",
  "profile_image": "url_to_image"
}
```

#### Change Password
- **Endpoint**: `POST /api/auth/change-password`
- **Headers**: `Authorization: Bearer {token}`
- **Body**:
```json
{
  "old_password": "current_password",
  "new_password": "new_password"
}
```

### 2. User Model Updates
- Added `display_name` field
- Added `password_hash` field
- Added `is_active` field
- Added `last_login` field
- Added methods: `set_password()`, `check_password()`

### 3. Security
- Passwords are hashed using Werkzeug's `generate_password_hash`
- JWT tokens are generated using Flask-JWT-Extended
- Token expiration can be configured in `config.py`

## Flutter Changes

### 1. Updated Login Screen
- Replaced Firebase Auth with HTTP requests to backend
- Uses `http` package for API calls
- Uses `shared_preferences` to store JWT token

### 2. New API Service
- Created `lib/services/api_service.dart`
- Handles all authentication API calls
- Manages JWT token storage and retrieval
- Provides helper methods for authenticated requests

### 3. Required Packages
Add to `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.2
```

## Setup Instructions

### Backend

1. **Activate Virtual Environment**:
```bash
cd savetogether-backend
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize Database**:
```bash
python init_db.py
```

4. **Run the Server**:
```bash
python src/main.py
```

### Flutter

1. **Install Packages**:
```bash
cd stockvel
flutter pub get
```

2. **Update API URL** (if needed):
Edit `lib/services/api_service.dart` and update the `baseUrl`:
```dart
static const String baseUrl = 'http://your-backend-url:5000/api';
```

3. **Run the App**:
```bash
flutter run
```

## Testing

### Using curl

**Register**:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Login**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Get Profile**:
```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Migration Notes

### Removed Firebase Dependencies (in auth flow):
- `firebase_auth` - replaced with HTTP API calls
- `cloud_firestore` - replaced with backend database

### What Still Uses Firebase:
- Firebase Storage (for images)
- Can be migrated later if needed

## Environment Variables

Make sure these are set in your `.env` file:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///savetogether.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Deployment

### EC2 Deployment

1. **SSH into EC2**:
```bash
ssh -i your-key.pem ubuntu@ec2-18-227-114-213.us-east-2.compute.amazonaws.com
```

2. **Pull Latest Changes**:
```bash
cd ~/savetogether-backend
git pull origin main
```

3. **Install Dependencies**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. **Restart Service**:
```bash
sudo systemctl restart savetogether
```

## Troubleshooting

### Common Issues

1. **Import Errors in Backend**:
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **CORS Errors in Flutter**:
   - Check `CORS_ORIGINS` in backend config
   - Make sure backend is running and accessible

3. **Token Expired**:
   - JWT tokens expire after 24 hours by default
   - User needs to login again
   - Can extend expiration in config

4. **Connection Refused**:
   - Make sure backend is running
   - Check firewall settings on EC2
   - Verify security group allows port 5000

## Next Steps

- [ ] Add password reset functionality
- [ ] Add email verification
- [ ] Add refresh token mechanism
- [ ] Add rate limiting for auth endpoints
- [ ] Add account lockout after failed attempts
- [ ] Migrate remaining Firebase services
