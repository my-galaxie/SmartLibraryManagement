-- GENERATE STUDENT IDs SCRIPT
-- This script populates NULL student_id fields with a generated format (e.g., STU2024001)

WITH numbered_students AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as r_num
  FROM public.user_profiles
  WHERE role = 'student' AND student_id IS NULL
)
UPDATE public.user_profiles
SET student_id = 'STU' || to_char(NOW(), 'YYYY') || lpad(ns.r_num::text, 3, '0')
FROM numbered_students ns
WHERE public.user_profiles.id = ns.id;

-- Verify the changes
SELECT name, student_id FROM public.user_profiles WHERE role = 'student';
