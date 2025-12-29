-- Smart Library Management System - Seed Data
-- Execute this AFTER running schema.sql

-- ============================================
-- SAMPLE BOOKS
-- ============================================

INSERT INTO public.books (id, title, author, isbn, subject, category, department, semester, total_copies, available_copies, description) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 'Computer Science', 'Textbook', 'CSE', 3, 5, 5, 'Comprehensive guide to algorithms and data structures'),
    ('22222222-2222-2222-2222-222222222222', 'Clean Code', 'Robert C. Martin', '9780132350884', 'Software Engineering', 'Reference', 'CSE', 5, 3, 2, 'A handbook of agile software craftsmanship'),
    ('33333333-3333-3333-3333-333333333333', 'Database System Concepts', 'Abraham Silberschatz', '9780078022159', 'Database', 'Textbook', 'CSE', 4, 4, 4, 'Comprehensive database management systems textbook'),
    ('44444444-4444-4444-4444-444444444444', 'Digital Electronics', 'Morris Mano', '9780131725447', 'Electronics', 'Textbook', 'ECE', 2, 6, 5, 'Fundamentals of digital logic and design'),
    ('55555555-5555-5555-5555-555555555555', 'Operating System Concepts', 'Abraham Silberschatz', '9781118063330', 'Operating Systems', 'Textbook', 'CSE', 4, 5, 3, 'Operating systems principles and implementation'),
    ('66666666-6666-6666-6666-666666666666', 'Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', 'Networks', 'Textbook', 'CSE', 5, 4, 4, 'Computer networks and protocols'),
    ('77777777-7777-7777-7777-777777777777', 'Artificial Intelligence', 'Stuart Russell', '9780136042594', 'AI', 'Textbook', 'CSE', 6, 3, 3, 'Modern approach to artificial intelligence'),
    ('88888888-8888-8888-8888-888888888888', 'Data Structures and Algorithms in Python', 'Michael T. Goodrich', '9781118290279', 'Programming', 'Textbook', 'CSE', 2, 7, 6, 'Data structures using Python'),
    ('99999999-9999-9999-9999-999999999999', 'Machine Learning Yearning', 'Andrew Ng', '9780999289402', 'Machine Learning', 'Reference', 'CSE', 7, 2, 1, 'Practical guide to machine learning projects'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Microprocessors and Interfacing', 'Douglas V. Hall', '9780070617704', 'Microprocessors', 'Textbook', 'ECE', 3, 5, 5, 'Microprocessor architecture and interfacing');

-- ============================================
-- SAMPLE BOOK COPIES (RFID Tagged)
-- ============================================

INSERT INTO public.book_copies (book_id, rfid_uid, status) VALUES
    -- Introduction to Algorithms (5 copies)
    ('11111111-1111-1111-1111-111111111111', 'RFID001001', 'available'),
    ('11111111-1111-1111-1111-111111111111', 'RFID001002', 'available'),
    ('11111111-1111-1111-1111-111111111111', 'RFID001003', 'available'),
    ('11111111-1111-1111-1111-111111111111', 'RFID001004', 'available'),
    ('11111111-1111-1111-1111-111111111111', 'RFID001005', 'available'),
    
    -- Clean Code (3 copies, 1 borrowed)
    ('22222222-2222-2222-2222-222222222222', 'RFID002001', 'available'),
    ('22222222-2222-2222-2222-222222222222', 'RFID002002', 'available'),
    ('22222222-2222-2222-2222-222222222222', 'RFID002003', 'borrowed'),
    
    -- Database System Concepts (4 copies)
    ('33333333-3333-3333-3333-333333333333', 'RFID003001', 'available'),
    ('33333333-3333-3333-3333-333333333333', 'RFID003002', 'available'),
    ('33333333-3333-3333-3333-333333333333', 'RFID003003', 'available'),
    ('33333333-3333-3333-3333-333333333333', 'RFID003004', 'available'),
    
    -- Digital Electronics (6 copies, 1 borrowed)
    ('44444444-4444-4444-4444-444444444444', 'RFID004001', 'available'),
    ('44444444-4444-4444-4444-444444444444', 'RFID004002', 'available'),
    ('44444444-4444-4444-4444-444444444444', 'RFID004003', 'available'),
    ('44444444-4444-4444-4444-444444444444', 'RFID004004', 'available'),
    ('44444444-4444-4444-4444-444444444444', 'RFID004005', 'available'),
    ('44444444-4444-4444-4444-444444444444', 'RFID004006', 'borrowed'),
    
    -- Operating System Concepts (5 copies, 2 borrowed)
    ('55555555-5555-5555-5555-555555555555', 'RFID005001', 'available'),
    ('55555555-5555-5555-5555-555555555555', 'RFID005002', 'available'),
    ('55555555-5555-5555-5555-555555555555', 'RFID005003', 'available'),
    ('55555555-5555-5555-5555-555555555555', 'RFID005004', 'borrowed'),
    ('55555555-5555-5555-5555-555555555555', 'RFID005005', 'borrowed'),
    
    -- Machine Learning Yearning (2 copies, 1 borrowed)
    ('99999999-9999-9999-9999-999999999999', 'RFID009001', 'available'),
    ('99999999-9999-9999-9999-999999999999', 'RFID009002', 'borrowed');

-- ============================================
-- SAMPLE ACADEMIC RESOURCES
-- ============================================

INSERT INTO public.resources (title, type, subject, semester, year, file_url, file_size) VALUES
    ('CIE 1 - Data Structures', 'cie_paper', 'Data Structures', 3, 2024, 'https://example.com/resources/cie1_ds_2024.pdf', 524288),
    ('CIE 2 - Database Management', 'cie_paper', 'Database Management', 4, 2024, 'https://example.com/resources/cie2_dbms_2024.pdf', 612352),
    ('Algorithm Analysis Notes', 'notes', 'Algorithms', 3, 2024, 'https://example.com/resources/algo_notes.pdf', 1048576),
    ('Operating Systems Syllabus', 'syllabus', 'Operating Systems', 4, 2024, 'https://example.com/resources/os_syllabus.pdf', 204800),
    ('CIE 1 - Computer Networks', 'cie_paper', 'Computer Networks', 5, 2024, 'https://example.com/resources/cie1_cn_2024.pdf', 587520);

-- ============================================
-- NOTES FOR TESTING
-- ============================================

-- IMPORTANT: You'll need to manually create user accounts through Supabase Auth first
-- Then insert corresponding records in user_profiles table

-- Example (after creating users in Supabase Auth):
-- 
-- INSERT INTO public.user_profiles (id, email, name, role, student_id) VALUES
--     ('<user-uuid-from-supabase-auth>', 'student@test.com', 'Test Student', 'student', 'STU2024001'),
--     ('<user-uuid-from-supabase-auth>', 'admin@test.com', 'Test Admin', 'admin', NULL);

-- To create sample borrow transactions, you would need actual user IDs
-- Example:
-- 
-- INSERT INTO public.borrows (user_id, book_id, book_copy_id, due_date, status) VALUES
--     ('<student-user-id>', '22222222-2222-2222-2222-222222222222', 
--      (SELECT id FROM book_copies WHERE rfid_uid = 'RFID002003'), 
--      NOW() + INTERVAL '14 days', 'borrowed');

-- ============================================
-- DATA VERIFICATION QUERIES
-- ============================================

-- Count books by department
-- SELECT department, COUNT(*) as book_count FROM public.books GROUP BY department;

-- Check availability
-- SELECT title, total_copies, available_copies FROM public.books ORDER BY title;

-- List all resources
-- SELECT title, subject, semester, year FROM public.resources ORDER BY semester, subject;
