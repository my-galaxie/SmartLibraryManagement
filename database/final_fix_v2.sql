-- RECURSION KILLER FIX V2
-- This approach uses JWT metadata effectively removing the DB query loop entirely

-- 1. Redefine is_admin to read from JWT (Memory) instead of Table (Disk/Recursion)
-- This is much faster and safer as it doesn't trigger RLS policies on tables
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN COALESCE(
    (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin',
    FALSE
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Drop potential recursive policies
DROP POLICY IF EXISTS "Admins manage books" ON public.books;
DROP POLICY IF EXISTS "Admins can view all profiles" ON public.user_profiles;

-- 3. Re-apply Admin Policies (Selectively) for Books

-- Ensure Public View exists
DROP POLICY IF EXISTS "Public view books" ON public.books;
CREATE POLICY "Public view books" ON public.books FOR SELECT USING (true);

-- Admins can do everything else (Insert, Update, Delete)
-- We split these to ensure SELECT never touches is_admin() if possible (though optimization usually handles it)
DROP POLICY IF EXISTS "Admins insert books" ON public.books;
CREATE POLICY "Admins insert books" ON public.books FOR INSERT WITH CHECK (is_admin());

DROP POLICY IF EXISTS "Admins update books" ON public.books;
CREATE POLICY "Admins update books" ON public.books FOR UPDATE USING (is_admin());

DROP POLICY IF EXISTS "Admins delete books" ON public.books;
CREATE POLICY "Admins delete books" ON public.books FOR DELETE USING (is_admin());

-- 4. Re-apply Admin Policies for User Profiles
CREATE POLICY "Admins can view all profiles" ON public.user_profiles
    FOR SELECT USING (is_admin());

-- 5. Helper verification (Optional: Run this to check if function works)
-- SELECT is_admin();
