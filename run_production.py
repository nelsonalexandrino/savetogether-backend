#!/usr/bin/env python3
"""
Production startup script for SaveTogether Backend
This ensures environment variables are set correctly before starting the app
"""
import os
import sys

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'dev-secret-key-123'
os.environ['JWT_SECRET_KEY'] = 'dev-jwt-secret-key-456'
os.environ['DATABASE_URL'] = 'postgresql://savetogether_user:savetogetherwithabsa@localhost:5432/savetogether'
os.environ['CORS_ORIGINS'] = '*'
os.environ['PORT'] = '5000'
os.environ['HOST'] = '0.0.0.0'

print("=" * 60)
print("🚀 Starting SaveTogether Backend - PRODUCTION MODE")
print("=" * 60)
print(f"Flask Environment: {os.environ['FLASK_ENV']}")
print(f"Debug Mode: {os.environ['DEBUG']}")
print(f"JWT Secret Key: {os.environ['JWT_SECRET_KEY'][:15]}...")
print(f"Database: {os.environ['DATABASE_URL'].split('@')[1] if '@' in os.environ['DATABASE_URL'] else 'configured'}")
print(f"CORS Origins: {os.environ['CORS_ORIGINS']}")
print(f"Host: {os.environ['HOST']}:{os.environ['PORT']}")
print("=" * 60)
print()

# Add the src directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the app
if __name__ == '__main__':
    from main import app
    
    # Run the Flask app
    app.run(
        host=os.environ['HOST'],
        port=int(os.environ['PORT']),
        debug=os.environ['DEBUG'].lower() == 'true'
    )
