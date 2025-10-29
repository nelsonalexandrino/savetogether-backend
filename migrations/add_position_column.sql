-- Add position column to stockvel_members table for member ordering
-- This allows admins to set and persist the payout rotation order

-- Add position column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stockvel_members' AND column_name='position'
    ) THEN
        ALTER TABLE stockvel_members ADD COLUMN position INTEGER;
        RAISE NOTICE 'Added position column to stockvel_members table';
    ELSE
        RAISE NOTICE 'Position column already exists';
    END IF;
END $$;

-- Initialize positions based on joined_at for existing members
-- This ensures existing stockvels have a default order
WITH ranked_members AS (
    SELECT id, 
           ROW_NUMBER() OVER (PARTITION BY stockvel_id ORDER BY joined_at ASC) - 1 as pos
    FROM stockvel_members
    WHERE position IS NULL
)
UPDATE stockvel_members sm
SET position = rm.pos
FROM ranked_members rm
WHERE sm.id = rm.id;

-- Verify the migration
SELECT 'Migration completed. Updated ' || COUNT(*) || ' members with positions' 
FROM stockvel_members 
WHERE position IS NOT NULL;
