"""
Script to delete all users from the database
WARNING: This will delete all user data!
"""
from src.main import app
from src.services.database_service import db
from src.models.user import User

def delete_all_users():
    with app.app_context():
        try:
            # Delete all users
            num_deleted = User.query.delete()
            db.session.commit()
            print(f"✅ Successfully deleted {num_deleted} users")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting users: {e}")

if __name__ == '__main__':
    confirm = input("⚠️  Are you sure you want to delete ALL users? (yes/no): ")
    if confirm.lower() == 'yes':
        delete_all_users()
    else:
        print("Operation cancelled")
