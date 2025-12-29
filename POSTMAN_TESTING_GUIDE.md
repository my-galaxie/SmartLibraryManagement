# Smart Library API - Postman Testing Guide

Complete guide to test all API endpoints using Postman.

---

## 🚀 Base URL

```
http://localhost:8000
```

---

## 📋 Testing Flow (Follow This Order)

### Step 1: Health Check
### Step 2: Create Student Account (Signup)
### Step 3: Login as Student (Get JWT Token)
### Step 4: Test Student Endpoints
### Step 5: Create Admin Account
### Step 6: Login as Admin
### Step 7: Test Admin Endpoints

---

## 1️⃣ Health Check

**No authentication required**

### GET `/api/health`

**Request:**
```
GET http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T18:56:38.123456"
}
```

---

## 2️⃣ Authentication Endpoints

### A. Signup (Create New User)

**POST `/auth/signup`**

**Headers:**
```
Content-Type: application/json
```

**Body (Student):**
```json
{
  "email": "student@test.com",
  "password": "password123",
  "role": "student",
  "name": "Test Student",
  "student_id": "STU2024001"
}
```

**Body (Admin):**
```json
{
  "email": "admin@test.com",
  "password": "admin123",
  "role": "admin",
  "name": "Test Admin"
}
```

**Expected Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "user_id": "uuid-here",
    "email": "student@test.com",
    "role": "student",
    "name": "Test Student"
  }
}
```

---

### B. Login (Get JWT Token)

**POST `/auth/login`**

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "student@test.com",
  "password": "password123"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "student@test.com",
  "role": "student",
  "name": "Test Student"
}
```

**⚠️ IMPORTANT: Copy the `access_token` value! You'll need it for all protected endpoints.**

---

### C. Validate Token

**GET `/auth/validate`**

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Expected Response:**
```json
{
  "valid": true,
  "user_id": "uuid-here",
  "email": "student@test.com",
  "role": "student"
}
```

---

## 3️⃣ Student Endpoints

**All student endpoints require authentication!**

**Headers for ALL student requests:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

### A. Student Dashboard

**GET `/api/student/dashboard`**

**Expected Response:**
```json
{
  "summary": {
    "currently_borrowed": 0,
    "due_soon": 0,
    "overdue": 0,
    "total_fine": 0
  }
}
```

---

### B. Current Borrowed Books

**GET `/api/student/books/current`**

**Expected Response:**
```json
{
  "books": []
}
```

*(Empty initially - no books borrowed yet)*

---

### C. Borrow History

**GET `/api/student/books/history`**

**Expected Response:**
```json
{
  "history": []
}
```

---

### D. Get Notifications

**GET `/api/student/notifications`**

**Expected Response:**
```json
{
  "notifications": [],
  "unread_count": 0
}
```

---

### E. Get Fines

**GET `/api/student/fines`**

**Expected Response:**
```json
{
  "total_fine": 0,
  "fines": []
}
```

---

## 4️⃣ Books Endpoints

**Authentication required (student or admin)**

### A. Search Books

**GET `/api/books/search`**

**Query Parameters (all optional):**
- `title` - Search by title
- `author` - Search by author
- `subject` - Search by subject
- `category` - Filter by category
- `available` - true/false

**Examples:**

1. **Get all books:**
```
GET http://localhost:8000/api/books/search
```

2. **Search by title:**
```
GET http://localhost:8000/api/books/search?title=Introduction
```

3. **Search available books only:**
```
GET http://localhost:8000/api/books/search?available=true
```

4. **Search by author:**
```
GET http://localhost:8000/api/books/search?author=Adams
```

**Expected Response:**
```json
{
  "books": [
    {
      "id": "uuid",
      "title": "Introduction to Algorithms",
      "author": "Thomas H. Cormen",
      "isbn": "9780262033848",
      "category": "Computer Science",
      "subject": "Algorithms",
      "publisher": "MIT Press",
      "publication_year": 2009,
      "total_copies": 5,
      "available_copies": 5,
      "description": "Comprehensive guide to algorithms",
      "cover_image_url": null
    }
  ],
  "total": 1
}
```

---

### B. Get Book Details

**GET `/api/books/{book_id}`**

**Example:**
```
GET http://localhost:8000/api/books/uuid-of-book
```

**Expected Response:**
```json
{
  "book": {
    "id": "uuid",
    "title": "Introduction to Algorithms",
    "author": "Thomas H. Cormen",
    "isbn": "9780262033848",
    "category": "Computer Science",
    "subject": "Algorithms",
    "publisher": "MIT Press",
    "publication_year": 2009,
    "total_copies": 5,
    "available_copies": 5,
    "description": "Comprehensive guide to algorithms"
  },
  "copies": [
    {
      "id": "copy-uuid",
      "rfid_code": "RFID001",
      "status": "available"
    }
  ],
  "user_subscribed": false
}
```

---

### C. Subscribe to Book Availability

**POST `/api/books/{book_id}/notify`**

**Example:**
```
POST http://localhost:8000/api/books/uuid-of-book/notify
```

**Expected Response:**
```json
{
  "message": "Subscription created successfully"
}
```

---

## 5️⃣ Admin Endpoints

**All admin endpoints require admin role!**

**Headers for ALL admin requests:**
```
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

### A. Admin Dashboard

**GET `/api/admin/dashboard`**

**Expected Response:**
```json
{
  "summary": {
    "total_books": 10,
    "total_copies": 50,
    "borrowed_today": 0,
    "active_borrows": 0,
    "overdue_borrows": 0,
    "total_students": 1,
    "total_fines": 0
  },
  "recent_borrows": [],
  "borrow_trends": []
}
```

---

### B. Get All Books (Admin)

**GET `/api/admin/books`**

**Expected Response:**
```json
{
  "books": [
    {
      "id": "uuid",
      "title": "Introduction to Algorithms",
      "author": "Thomas H. Cormen",
      "isbn": "9780262033848",
      "category": "Computer Science",
      "subject": "Algorithms",
      "total_copies": 5,
      "available_copies": 5
    }
  ],
  "total": 10
}
```

---

### C. Add New Book

**POST `/api/admin/books`**

**Body:**
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "category": "Computer Science",
  "subject": "Software Engineering",
  "publisher": "Prentice Hall",
  "publication_year": 2008,
  "total_copies": 3,
  "description": "A handbook of agile software craftsmanship"
}
```

**Expected Response:**
```json
{
  "message": "Book added successfully",
  "book_id": "new-uuid"
}
```

---

### D. Update Book

**PUT `/api/admin/books/{book_id}`**

**Body:**
```json
{
  "title": "Clean Code - Updated Edition",
  "total_copies": 5
}
```

**Expected Response:**
```json
{
  "message": "Book updated successfully"
}
```

---

### E. Delete Book

**DELETE `/api/admin/books/{book_id}`**

**Expected Response:**
```json
{
  "message": "Book deleted successfully"
}
```

---

### F. Get All Students

**GET `/api/admin/students`**

**Expected Response:**
```json
{
  "students": [
    {
      "id": "uuid",
      "email": "student@test.com",
      "name": "Test Student",
      "student_id": "STU2024001",
      "active_borrows": 0,
      "total_fines": 0
    }
  ],
  "total": 1
}
```

---

### G. Get Student Details

**GET `/api/admin/students/{student_id}`**

**Expected Response:**
```json
{
  "student": {
    "id": "uuid",
    "email": "student@test.com",
    "name": "Test Student",
    "student_id": "STU2024001"
  },
  "active_borrows": [],
  "borrow_history": [],
  "fines": [],
  "statistics": {
    "total_borrows": 0,
    "active_borrows": 0,
    "total_fines": 0
  }
}
```

---

### H. Get Borrow Logs

**GET `/api/admin/logs`**

**Query Parameters (all optional):**
- `student_id` - Filter by student
- `book_id` - Filter by book
- `status` - Filter by status (borrowed/returned/overdue)
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)

**Examples:**

1. **All logs:**
```
GET http://localhost:8000/api/admin/logs
```

2. **Filter by status:**
```
GET http://localhost:8000/api/admin/logs?status=borrowed
```

**Expected Response:**
```json
{
  "logs": [],
  "total": 0
}
```

---

### I. Get All Fines

**GET `/api/admin/fines`**

**Expected Response:**
```json
{
  "fines": [],
  "total_amount": 0,
  "total_count": 0
}
```

---

### J. Broadcast Notification

**POST `/api/admin/notifications/broadcast`**

**Body:**
```json
{
  "title": "Library Announcement",
  "message": "The library will be closed on Sunday for maintenance.",
  "type": "info"
}
```

**Expected Response:**
```json
{
  "message": "Notification sent to all students",
  "count": 1
}
```

---

## 6️⃣ Resources Endpoints

### A. List Resources

**GET `/api/resources`**

**Query Parameters:**
- `subject` - Filter by subject
- `year` - Filter by year

**Example:**
```
GET http://localhost:8000/api/resources?subject=Computer Science
```

**Expected Response:**
```json
{
  "resources": [
    {
      "id": "uuid",
      "title": "Data Structures Question Paper 2023",
      "description": "CIE examination paper",
      "subject": "Computer Science",
      "type": "question_paper",
      "year": 2023
    }
  ],
  "total": 1
}
```

---

### B. Download Resource

**GET `/api/resources/{resource_id}/download`**

**Expected Response:**
```json
{
  "download_url": "https://supabase-url/storage/...",
  "filename": "paper.pdf"
}
```

---

## 7️⃣ Rules Endpoints

### Get Borrow Policy

**GET `/api/rules/borrow-policy`**

**Expected Response:**
```json
{
  "fine_per_day": 5,
  "grace_period_days": 2,
  "borrow_duration_days": 14,
  "max_books_per_student": 3
}
```

---

## 🔧 Postman Setup Guide

### 1. Create Environment

In Postman:
1. Click "Environments" (left sidebar)
2. Click "Create Environment"
3. Name it "Smart Library Local"
4. Add variables:
   - `base_url` = `http://localhost:8000`
   - `token` = (leave empty, will be set after login)

### 2. Use Variables in Requests

**URL:**
```
{{base_url}}/auth/login
```

**Headers:**
```
Authorization: Bearer {{token}}
```

### 3. Save Token After Login

After logging in:
1. Go to the login response
2. Copy the `access_token` value
3. Go to Environment
4. Paste into `token` variable
5. Save

Now all requests will automatically use your token!

---

## 📝 Testing Checklist

- [ ] Health check works
- [ ] Can create student account
- [ ] Can create admin account
- [ ] Can login as student (save token!)
- [ ] Can login as admin (save token!)
- [ ] Student can view dashboard
- [ ] Student can search books
- [ ] Student can view book details
- [ ] Admin can view dashboard
- [ ] Admin can add new book
- [ ] Admin can view all books
- [ ] Admin can view all students
- [ ] Admin can send broadcast notification

---

## 🐛 Troubleshooting

### "Unauthorized" Error
- Make sure you copied the token after login
- Check that you're using `Bearer <token>` format
- The token might have expired (24 hours) - login again

### "Forbidden" Error
- You're trying to access admin endpoint with student token
- Login with admin account for admin endpoints

### "404 Not Found"
- Check the URL is correct
- Make sure backend is running on port 8000

### "500 Internal Server Error"
- Check backend terminal for error details
- Make sure database schema was executed correctly

---

## 🎯 Quick Test Sequence

1. **Signup as Student** → Copy response
2. **Login as Student** → Copy `access_token`
3. **Get Student Dashboard** → Should show summary
4. **Search Books** → Should return book list
5. **Signup as Admin**
6. **Login as Admin** → Copy `access_token`
7. **Get Admin Dashboard** → Should show analytics
8. **Add New Book** → Should create book
9. **View All Books** → Should include new book

---

## 📚 API Documentation

For interactive API docs, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test endpoints directly in Swagger UI!
