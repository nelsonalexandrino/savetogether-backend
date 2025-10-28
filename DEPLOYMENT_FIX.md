# PostgreSQL Permission Fix for EC2/RDS

## Problem
Getting error: `permission denied for schema public` when trying to create tables.

## Solution Options

### Option 1: Fix Permissions (Recommended)

SSH into your EC2 instance and connect to PostgreSQL:

```bash
# Connect to PostgreSQL as the main user
sudo -u postgres psql

# Or if using RDS, connect with your master user
psql -h your-rds-endpoint.rds.amazonaws.com -U your_master_user -d your_database_name
```

Then run these SQL commands (replace `your_db_user` with your actual database username):

```sql
-- Grant all privileges on the public schema
GRANT ALL PRIVILEGES ON SCHEMA public TO your_db_user;

-- Grant privileges on all existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_db_user;

-- Grant privileges on all sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_db_user;

-- Make the user the owner of the public schema
ALTER SCHEMA public OWNER TO your_db_user;

-- Exit
\q
```

### Option 2: Use SQLite for Development (Quick Fix)

If you just want to test quickly, you can temporarily use SQLite instead of PostgreSQL.

1. **Update your `.env` file on EC2**:

```bash
nano ~/.env
```

Change the DATABASE_URL to:
```env
DATABASE_URL=sqlite:///savetogether.db
```

2. **Run init_db.py again**:
```bash
cd ~/savetogether-backend
source venv/bin/activate
python3 init_db.py
```

### Option 3: Create a New PostgreSQL User with Proper Permissions

If you need to create a new user from scratch:

```bash
# Connect as postgres user
sudo -u postgres psql
```

```sql
-- Create new user
CREATE USER savetogether_user WITH PASSWORD 'your_secure_password';

-- Create database
CREATE DATABASE savetogether_db OWNER savetogether_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE savetogether_db TO savetogether_user;

-- Connect to the new database
\c savetogether_db

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO savetogether_user;
ALTER SCHEMA public OWNER TO savetogether_user;

-- Exit
\q
```

Then update your `.env` file:
```env
DATABASE_URL=postgresql://savetogether_user:your_secure_password@localhost/savetogether_db
```

### Option 4: Using RDS (AWS)

If you're using AWS RDS:

1. **Connect with your master user**:
```bash
psql -h your-rds-endpoint.rds.amazonaws.com -U your_master_user -d postgres
```

2. **Create database and user**:
```sql
CREATE DATABASE savetogether_db;
CREATE USER savetogether_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE savetogether_db TO savetogether_user;
\c savetogether_db
GRANT ALL PRIVILEGES ON SCHEMA public TO savetogether_user;
ALTER SCHEMA public OWNER TO savetogether_user;
\q
```

3. **Update your `.env` file**:
```env
DATABASE_URL=postgresql://savetogether_user:your_secure_password@your-rds-endpoint.rds.amazonaws.com:5432/savetogether_db
```

## Verify the Fix

After applying one of the solutions above, test it:

```bash
cd ~/savetogether-backend
source venv/bin/activate
python3 init_db.py
```

You should see:
```
Database initialized successfully!
Created tables for: users, stockvels, stockvel_members, contributions
```

## Common Issues

### Issue 1: Can't connect to PostgreSQL
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if needed
sudo systemctl start postgresql
```

### Issue 2: Don't know the database username
```bash
# Check your .env file
cat .env | grep DATABASE_URL

# Or check your connection string in utils/config.py
```

### Issue 3: RDS Security Group
Make sure your EC2 instance's security group has access to your RDS instance:
- RDS Security Group should allow inbound connections on port 5432 from EC2's security group

## Quick Commands Reference

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@ec2-18-227-114-213.us-east-2.compute.amazonaws.com

# Activate virtual environment
cd ~/savetogether-backend
source venv/bin/activate

# Check environment variables
cat .env

# Initialize database
python3 init_db.py

# Run the application
python3 src/main.py

# Check logs
tail -f logs/app.log  # if you have logging set up
```

## Need More Help?

Check your current database configuration:
```bash
# In your EC2 instance
cd ~/savetogether-backend
source venv/bin/activate
python3 -c "from utils.config import config_by_name; import os; print(config_by_name[os.getenv('FLASK_ENV', 'development')].SQLALCHEMY_DATABASE_URI)"
```

This will show you what database URL is being used.
