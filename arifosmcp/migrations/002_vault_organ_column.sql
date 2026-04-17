-- Step 3 — Add organ column to vault table
-- Run this on Supabase

ALTER TABLE arifosmcp_vault_seals 
ADD COLUMN IF NOT EXISTS organ VARCHAR 
CHECK (organ IN ('arifos', 'wealth', 'well', 'geox'));

-- Add index for efficient filtering by organ
CREATE INDEX IF NOT EXISTS idx_vault_organ 
ON arifosmcp_vault_seals (organ, timestamp DESC);
