"""
Migration script to add position column to stockvel_members table
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_position_column():
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'stockvel_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='stockvel_members' AND column_name='position';
        """)
        
        if cursor.fetchone():
            print("Column 'position' already exists in stockvel_members table")
        else:
            # Add position column
            cursor.execute("""
                ALTER TABLE stockvel_members 
                ADD COLUMN position INTEGER;
            """)
            print("Added 'position' column to stockvel_members table")
            
            # Initialize positions based on joined_at (existing members)
            cursor.execute("""
                WITH ranked_members AS (
                    SELECT id, 
                           ROW_NUMBER() OVER (PARTITION BY stockvel_id ORDER BY joined_at ASC) - 1 as pos
                    FROM stockvel_members
                )
                UPDATE stockvel_members sm
                SET position = rm.pos
                FROM ranked_members rm
                WHERE sm.id = rm.id;
            """)
            print("Initialized position values for existing members based on join date")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    add_position_column()
