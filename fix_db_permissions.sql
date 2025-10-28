-- Run these commands in your PostgreSQL database to fix permissions
-- Connect to your database first, then run these commands

-- Grant privileges to your database user (replace 'your_db_user' with actual username)
GRANT ALL PRIVILEGES ON SCHEMA public TO your_db_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_db_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_db_user;

-- If you're the owner or using the postgres user, you can also run:
ALTER SCHEMA public OWNER TO your_db_user;

-- For RDS specifically, you might need to grant from rds_superuser:
-- GRANT your_db_user TO rds_superuser;
