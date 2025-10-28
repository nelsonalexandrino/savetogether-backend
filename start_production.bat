@echo off
REM Windows batch script to start backend with production environment

set FLASK_ENV=production
set DEBUG=False
set SECRET_KEY=dev-secret-key-123
set JWT_SECRET_KEY=dev-jwt-secret-key-456
set DATABASE_URL=postgresql://savetogether_user:savetogetherwithabsa@localhost:5432/savetogether
set CORS_ORIGINS=*
set PORT=5000
set HOST=0.0.0.0

echo Starting SaveTogether Backend in PRODUCTION mode...
echo JWT_SECRET_KEY: %JWT_SECRET_KEY:~0,10%...
echo DATABASE: %DATABASE_URL%

python src/main.py
