-- Smart Library Management System - Database Reset Script
-- Run this FIRST before running schema.sql

-- ================================================
-- DROP ALL POLICIES (to avoid "already exists" errors)
-- ================================================

-- Drop RLS policies for user_profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON public.user_profiles;

-- Drop RLS policies for books
DROP POLICY IF EXISTS "Anyone can view books" ON public.books;
DROP POLICY IF EXISTS "Only admins can insert books" ON public.books;
DROP POLICY IF EXISTS "Only admins can update books" ON public.books;
DROP POLICY IF EXISTS "Only admins can delete books" ON public.books;

-- Drop RLS policies for book_copies
DROP POLICY IF EXISTS "Anyone can view book copies" ON public.book_copies;
DROP POLICY IF EXISTS "Only admins can manage copies" ON public.book_copies;

-- Drop RLS policies for borrows
DROP POLICY IF EXISTS "Students can view own borrows" ON public.borrows;
DROP POLICY IF EXISTS "Admins can view all borrows" ON public.borrows;
DROP POLICY IF EXISTS "Only admins can insert borrows" ON public.borrows;
DROP POLICY IF EXISTS "Only admins can update borrows" ON public.borrows;

-- Drop RLS policies for notifications
DROP POLICY IF EXISTS "Users can view own notifications" ON public.notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON public.notifications;
DROP POLICY IF EXISTS "Admins can manage all notifications" ON public.notifications;

-- Drop RLS policies for fines
DROP POLICY IF EXISTS "Students can view own fines" ON public.fines;
DROP POLICY IF EXISTS "Admins can view all fines" ON public.fines;
DROP POLICY IF EXISTS "Only admins can manage fines" ON public.fines;

-- Drop RLS policies for resources
DROP POLICY IF EXISTS "Anyone can view resources" ON public.resources;
DROP POLICY IF EXISTS "Only admins can manage resources" ON public.resources;

-- Drop RLS policies for availability_subscriptions
DROP POLICY IF EXISTS "Users can view own subscriptions" ON public.availability_subscriptions;
DROP POLICY IF EXISTS "Users can manage own subscriptions" ON public.availability_subscriptions;

-- Drop RLS policies for system_config
DROP POLICY IF EXISTS "Anyone can view config" ON public.system_config;
DROP POLICY IF EXISTS "Only admins can update config" ON public.system_config;

-- ================================================
-- DROP ALL TRIGGERS
-- ================================================

DROP TRIGGER IF EXISTS update_book_available_copies_on_copy_change ON public.book_copies;
DROP TRIGGER IF EXISTS update_book_available_copies_on_borrow ON public.borrows;

-- ================================================
-- DROP ALL FUNCTIONS
-- ================================================

DROP FUNCTION IF EXISTS public.update_book_available_copies();
DROP FUNCTION IF EXISTS public.update_available_copies_on_borrow();

-- ================================================
-- DROP ALL TABLES (in correct order due to foreign keys)
-- ================================================

DROP TABLE IF EXISTS public.availability_subscriptions CASCADE;
DROP TABLE IF EXISTS public.fines CASCADE;
DROP TABLE IF EXISTS public.notifications CASCADE;
DROP TABLE IF EXISTS public.borrows CASCADE;
DROP TABLE IF EXISTS public.book_copies CASCADE;
DROP TABLE IF EXISTS public.books CASCADE;
DROP TABLE IF EXISTS public.resources CASCADE;
DROP TABLE IF EXISTS public.system_config CASCADE;
DROP TABLE IF EXISTS public.user_profiles CASCADE;

-- ================================================
-- DROP EXTENSIONS
-- ================================================

-- Don't drop uuid-ossp as it might be used by other projects
-- DROP EXTENSION IF EXISTS "uuid-ossp";

-- ================================================
-- DONE - Now you can run schema.sql
-- ================================================

SELECT 'Database reset complete. You can now run schema.sql' as message;
