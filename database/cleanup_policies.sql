-- NUCLEAR OPTION: RLS CLEANUP
-- This script aggressively finds and drops EVERY policy on the problematic tables
-- Run this in Supabase SQL Editor

-- 1. Redefine is_admin safely (Just in case)
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN COALESCE(
    (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin',
    FALSE
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Drop policies using standard names (History of what we might have created)
DROP POLICY IF EXISTS "Anyone can view books" ON public.books;
DROP POLICY IF EXISTS "Public view books" ON public.books;
DROP POLICY IF EXISTS "Enable read access for all users" ON public.books;
DROP POLICY IF EXISTS "Admins can manage books" ON public.books;
DROP POLICY IF EXISTS "Admins manage books" ON public.books;
DROP POLICY IF EXISTS "Admins insert books" ON public.books;
DROP POLICY IF EXISTS "Admins update books" ON public.books;
DROP POLICY IF EXISTS "Admins delete books" ON public.books;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON public.books;

DROP POLICY IF EXISTS "Users can view their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Enable read access for users based on email" ON public.user_profiles;

-- 3. Re-Apply SAFE Policies

-- BOOKS: Simples possible policy. NO conditions.
CREATE POLICY "Public view books" ON public.books FOR SELECT USING (true);

-- ADMINS: Only check is_admin (which checks JWT, not DB)
CREATE POLICY "Admins insert books" ON public.books FOR INSERT WITH CHECK (is_admin());
CREATE POLICY "Admins update books" ON public.books FOR UPDATE USING (is_admin());
CREATE POLICY "Admins delete books" ON public.books FOR DELETE USING (is_admin());

-- PROFILES
CREATE POLICY "Users can view their own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Admins can view all profiles" ON public.user_profiles
    FOR SELECT USING (is_admin());

-- 4. Verify RLS is ON
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
