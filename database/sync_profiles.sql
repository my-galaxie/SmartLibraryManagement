-- SYNC PROFILES SCRIPT
-- This script backfills missing user_profiles for users that exist in auth.users
-- This fixes the issue where users appear in the Auth dashboard but not in the API list.

INSERT INTO public.user_profiles (id, email, name, role)
SELECT 
    id, 
    email, 
    -- Use metadata name if available, otherwise use email prefix
    COALESCE(raw_user_meta_data->>'full_name', split_part(email, '@', 1)) as name,
    -- Default to 'student' if no role is defined
    COALESCE(raw_user_meta_data->>'role', 'student') as role
FROM auth.users
WHERE NOT EXISTS (
    SELECT 1 FROM public.user_profiles WHERE user_profiles.id = auth.users.id
);

-- Output result
SELECT count(*) as new_profiles_created FROM public.user_profiles 
WHERE created_at > (NOW() - INTERVAL '1 minute');
