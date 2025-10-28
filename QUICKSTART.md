# Quick Start Guide - Authentication Testing

## Step 1: Setup Backend

### Activate Virtual Environment
```powershell
cd savetogether-backend
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies
```powershell
pip install Flask Flask-SQLAlchemy Flask-CORS Flask-JWT-Extended python-dotenv Werkzeug requests
```

### Initialize Database
```powershell
python init_db.py
```

### Run Backend Server
```powershell
python src/main.py
```

Server should start on: `http://localhost:5000`

## Step 2: Test Backend (Optional)

### Open a new terminal and activate venv:
```powershell
cd savetogether-backend
.\.venv\Scripts\Activate.ps1
python test_auth.py
```

This will test:
- User registration
- User login
- Get profile

## Step 3: Setup Flutter

### Install Dependencies
```powershell
cd stockvel
flutter pub get
```

### Run Flutter App
```powershell
flutter run
```

## Step 4: Test in Flutter App

1. The app should open to the login screen
2. Try registering a new user:
   - Email: `test@example.com`
   - Password: `password123`
3. Or login with existing credentials

## Troubleshooting

### Backend Error: "SQLAlchemy instance not registered"
**Fixed!** Make sure you're running the latest code where `main.py` imports `db` from `database_service.py`

### Backend Error: "Import could not be resolved"
**Solution:** Install packages:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Flutter Error: "Target of URI doesn't exist: 'package:shared_preferences'"
**Solution:** Run:
```powershell
flutter pub get
```

### Connection Error from Flutter
**Solution:** 
1. Make sure backend is running on port 5000
2. If testing on physical device, update API URL in `lib/services/api_service.dart`:
   ```dart
   static const String baseUrl = 'http://YOUR_COMPUTER_IP:5000/api';
   ```
3. If testing on Android Emulator, use:
   ```dart
   static const String baseUrl = 'http://10.0.2.2:5000/api';
   ```

### CORS Error
Make sure `CORS_ORIGINS` in your `.env` file includes your Flutter app URL

## Quick Commands Reference

### Backend
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run server
python src/main.py

# Test endpoints
python test_auth.py

# Initialize database
python init_db.py
```

### Flutter
```powershell
# Get dependencies
flutter pub get

# Run app
flutter run

# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

## API Endpoints

All requests use `Content-Type: application/json`

### Register
```http
POST http://localhost:5000/api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "display_name": "User Name" (optional)
}
```

### Login
```http
POST http://localhost:5000/api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Get Profile (requires token)
```http
GET http://localhost:5000/api/auth/profile
Authorization: Bearer {your_token_here}
```

## Success Indicators

✅ Backend: Console shows "Running on http://127.0.0.1:5000"
✅ Database: `init_db.py` prints "Database tables created successfully!"
✅ Test: `test_auth.py` shows 200/201 status codes
✅ Flutter: Login screen loads without Firebase errors
✅ Flutter: Can register and login successfully
