-- ULTIMATE RLS FIX
-- This script uses Dynamic SQL to find and DROP ALL policies on the target tables
-- regardless of what they are named. This ensures we start with a clean slate.

-- 1. Safe is_admin (JWT based)
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN COALESCE(
    (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin',
    FALSE
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Dynamic Policy Removal (The Nuke)
DO $$ 
DECLARE 
    r RECORD; 
BEGIN 
    -- Drop all policies on 'books'
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'books' AND schemaname = 'public') 
    LOOP 
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.books'; 
    END LOOP;

    -- Drop all policies on 'user_profiles'
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'user_profiles' AND schemaname = 'public') 
    LOOP 
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON public.user_profiles'; 
    END LOOP;
END $$;

-- 3. Apply Simple, Safe Policies

-- BOOKS
CREATE POLICY "Public view books" ON public.books FOR SELECT USING (true);
CREATE POLICY "Admins manage books" ON public.books FOR ALL USING (is_admin());

-- PROFILES
CREATE POLICY "Users view own profile" ON public.user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users update own profile" ON public.user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users insert own profile" ON public.user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Admins view all profiles" ON public.user_profiles FOR SELECT USING (is_admin());

-- 4. Enable RLS
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
