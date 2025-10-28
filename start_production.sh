#!/bin/bash

# Load production environment variables
export FLASK_ENV=production
export DEBUG=False
export SECRET_KEY=dev-secret-key-123
export JWT_SECRET_KEY=dev-jwt-secret-key-456
export DATABASE_URL=postgresql://savetogether_user:savetogetherwithabsa@localhost:5432/savetogether
export CORS_ORIGINS=*
export PORT=5000
export HOST=0.0.0.0

echo "Starting SaveTogether Backend in PRODUCTION mode..."
echo "JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:10}..."
echo "DATABASE: $DATABASE_URL"

# Start the application
python3 src/main.py
