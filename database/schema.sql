-- Smart Library Management System - Database Schema
-- Execute this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USER PROFILES TABLE
-- ============================================
-- Extends Supabase auth.users with additional profile information
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'admin')),
    student_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- BOOKS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.books (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT,
    subject TEXT,
    category TEXT,
    department TEXT,
    semester INTEGER,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    description TEXT,
    cover_image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- BOOK COPIES TABLE
-- ============================================
-- Individual RFID-tagged copies of books
CREATE TABLE IF NOT EXISTS public.book_copies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
    rfid_uid TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'borrowed', 'maintenance', 'lost')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- BORROW TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.borrows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
    book_copy_id UUID REFERENCES public.book_copies(id) ON DELETE SET NULL,
    borrow_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    return_date TIMESTAMP WITH TIME ZONE,
    status TEXT NOT NULL DEFAULT 'borrowed' CHECK (status IN ('borrowed', 'returned', 'overdue')),
    fine_amount DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('due_soon', 'overdue', 'availability', 'announcement', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_borrow_id UUID REFERENCES public.borrows(id) ON DELETE SET NULL,
    related_book_id UUID REFERENCES public.books(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- FINES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.fines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrow_id UUID NOT NULL REFERENCES public.borrows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    days_overdue INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'waived')),
    paid_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- ACADEMIC RESOURCES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('cie_paper', 'syllabus', 'notes', 'other')),
    subject TEXT NOT NULL,
    semester INTEGER,
    year INTEGER,
    file_url TEXT NOT NULL,
    file_size BIGINT,
    uploaded_by UUID REFERENCES public.user_profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- AVAILABILITY SUBSCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.availability_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES public.books(id) ON DELETE CASCADE,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, book_id)
);

-- ============================================
-- SYSTEM CONFIGURATION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key TEXT NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- User profiles indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON public.user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_student_id ON public.user_profiles(student_id);

-- Books indexes
CREATE INDEX IF NOT EXISTS idx_books_title ON public.books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON public.books(author);
CREATE INDEX IF NOT EXISTS idx_books_subject ON public.books(subject);
CREATE INDEX IF NOT EXISTS idx_books_category ON public.books(category);

-- Book copies indexes
CREATE INDEX IF NOT EXISTS idx_book_copies_book_id ON public.book_copies(book_id);
CREATE INDEX IF NOT EXISTS idx_book_copies_rfid ON public.book_copies(rfid_uid);
CREATE INDEX IF NOT EXISTS idx_book_copies_status ON public.book_copies(status);

-- Borrows indexes
CREATE INDEX IF NOT EXISTS idx_borrows_user_id ON public.borrows(user_id);
CREATE INDEX IF NOT EXISTS idx_borrows_book_id ON public.borrows(book_id);
CREATE INDEX IF NOT EXISTS idx_borrows_status ON public.borrows(status);
CREATE INDEX IF NOT EXISTS idx_borrows_due_date ON public.borrows(due_date);
CREATE INDEX IF NOT EXISTS idx_borrows_return_date ON public.borrows(return_date);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON public.notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON public.notifications(type);

-- Resources indexes
CREATE INDEX IF NOT EXISTS idx_resources_subject ON public.resources(subject);
CREATE INDEX IF NOT EXISTS idx_resources_semester ON public.resources(semester);
CREATE INDEX IF NOT EXISTS idx_resources_type ON public.resources(type);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_copies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.borrows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.availability_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_config ENABLE ROW LEVEL SECURITY;

-- Helper function to check if user is admin (bypasses RLS to avoid recursion)
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.user_profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- User Profiles Policies
CREATE POLICY "Users can view their own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles" ON public.user_profiles
    FOR SELECT USING (is_admin());

-- Books Policies (public read, admin write)
CREATE POLICY "Anyone can view books" ON public.books
    FOR SELECT USING (true);

CREATE POLICY "Admins can manage books" ON public.books
    FOR ALL USING (is_admin());

-- Book Copies Policies
CREATE POLICY "Anyone can view book copies" ON public.book_copies
    FOR SELECT USING (true);

CREATE POLICY "Admins can manage book copies" ON public.book_copies
    FOR ALL USING (is_admin());

-- Borrows Policies
CREATE POLICY "Users can view their own borrows" ON public.borrows
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all borrows" ON public.borrows
    FOR SELECT USING (is_admin());

CREATE POLICY "System can insert borrows" ON public.borrows
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Admins can manage borrows" ON public.borrows
    FOR ALL USING (is_admin());

-- Notifications Policies
CREATE POLICY "Users can view their own notifications" ON public.notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own notifications" ON public.notifications
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "System can insert notifications" ON public.notifications
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Admins can manage all notifications" ON public.notifications
    FOR ALL USING (is_admin());

-- Fines Policies
CREATE POLICY "Users can view their own fines" ON public.fines
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage all fines" ON public.fines
    FOR ALL USING (is_admin());

-- Resources Policies
CREATE POLICY "Anyone can view resources" ON public.resources
    FOR SELECT USING (true);

CREATE POLICY "Admins can manage resources" ON public.resources
    FOR ALL USING (is_admin());

-- Availability Subscriptions Policies
CREATE POLICY "Users can view their own subscriptions" ON public.availability_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own subscriptions" ON public.availability_subscriptions
    FOR ALL USING (auth.uid() = user_id);

-- System Config Policies
CREATE POLICY "Anyone can view system config" ON public.system_config
    FOR SELECT USING (true);

CREATE POLICY "Admins can manage system config" ON public.system_config
    FOR ALL USING (is_admin());

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON public.books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_book_copies_updated_at BEFORE UPDATE ON public.book_copies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_borrows_updated_at BEFORE UPDATE ON public.borrows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fines_updated_at BEFORE UPDATE ON public.fines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON public.resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INSERT DEFAULT SYSTEM CONFIGURATION
-- ============================================

INSERT INTO public.system_config (key, value, description) VALUES
    ('borrow_duration_days', '14', 'Default number of days a book can be borrowed'),
    ('grace_period_days', '2', 'Grace period before fines start accumulating'),
    ('fine_per_day', '5', 'Fine amount per day for overdue books'),
    ('max_books_per_student', '3', 'Maximum number of books a student can borrow at once'),
    ('reminder_days_before_due', '3', 'Number of days before due date to send reminder')
ON CONFLICT (key) DO NOTHING;
