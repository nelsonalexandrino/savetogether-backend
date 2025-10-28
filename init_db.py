#!/usr/bin/env python3
"""
Initialize the database with all tables
Run this after starting the database for the first time
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment variables if not already set
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://savetogether_user:savetogetherwithabsa@db:5432/savetogether'

print("=" * 60)
print("🗄️  Initializing SaveTogether Database")
print("=" * 60)

from main import app
from services.database_service import db

# Import all models to ensure they're registered
from models.user import User
from models.stockvel import Stockvel, StockvelMember, Contribution

if __name__ == '__main__':
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        print("✅ All tables created successfully!")
        
        # List all tables
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Created tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
        except Exception as e:
            print(f"Could not list tables: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)
