-- Add CASCADE DELETE to foreign key constraints
-- This ensures that when a user is deleted, their memberships and contributions are also deleted

-- Drop existing foreign key constraints
ALTER TABLE stockvel_members DROP CONSTRAINT IF EXISTS stockvel_members_user_id_fkey;
ALTER TABLE contributions DROP CONSTRAINT IF EXISTS contributions_user_id_fkey;

-- Recreate with CASCADE DELETE
ALTER TABLE stockvel_members 
ADD CONSTRAINT stockvel_members_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE contributions 
ADD CONSTRAINT contributions_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Verify constraints
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confdeltype AS delete_action
FROM pg_constraint
WHERE conname IN ('stockvel_members_user_id_fkey', 'contributions_user_id_fkey');
