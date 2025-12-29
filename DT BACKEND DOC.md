

- **FastAPI** (framework)

- **AWS Lambda** (deployment via SAM)

- **Supabase (PostgreSQL)** as the database

- **Two separate backend stacks**:
  
  1. **Auth Stack** (Authentication & Authorization)
  
  2. **Core Application Stack** (Library logic, analytics, notifications, admin tools)

This document is written as:

- A **technical blueprint**

- A **project report–ready backend section**

- A **clear contract between frontend and backend**

No frontend logic is repeated here; this strictly defines **API responsibilities and routes**.

---

# SMART LIBRARY SYSTEM

## BACKEND API DESIGN DOCUMENT

**FastAPI + AWS Lambda + Supabase**

---

# OVERALL BACKEND ARCHITECTURE

### Stack Separation (Very Important)

You will deploy **two independent Lambda stacks**:

### 1. AUTH STACK

- Handles authentication & role resolution

- No business logic

- Stateless

### 2. CORE STACK

- Handles all library operations

- Book logic, notifications, analytics

- Talks to Supabase tables directly

This separation improves:

- Security

- Maintainability

- Evaluation clarity

---

# STACK 1: AUTHENTICATION STACK

## Base URL

```
/auth
```

---

## 1. USER AUTHENTICATION APIs

### 1.1 User Signup

**POST** `/auth/signup`

**Purpose:**

- Register new users (students/admins)

**Request Body:**

```json
{
  "email": "user@email.com",
  "password": "password",
  "role": "student | admin",
  "student_id": "optional",
  "name": "User Name"
}
```

**Response:**

```json
{
  "message": "Signup successful"
}
```

---

### 1.2 User Login

**POST** `/auth/login`

**Purpose:**

- Authenticate user

- Issue JWT

**Request Body:**

```json
{
  "email": "user@email.com",
  "password": "password"
}
```

**Response:**

```json
{
  "access_token": "jwt_token",
  "role": "student | admin",
  "user_id": "uuid"
}
```

---

### 1.3 Token Validation

**GET** `/auth/validate`

**Purpose:**

- Validate JWT from frontend

**Headers:**

```
Authorization: Bearer <token>
```

**Response:**

```json
{
  "valid": true,
  "role": "student"
}
```

---

### 1.4 Logout (Optional)

**POST** `/auth/logout`

**Purpose:**

- Stateless logout acknowledgment

---

# STACK 2: CORE APPLICATION STACK

## Base URL

```
/api
```

---

## 2. STUDENT APIs

---

### 2.1 Student Dashboard Summary

**GET** `/api/student/dashboard`

**Purpose:**

- Populate student dashboard cards

**Response:**

```json
{
  "borrowed_count": 3,
  "due_soon": 1,
  "overdue": 0,
  "total_fine": 20
}
```

---

### 2.2 Get Current Borrowed Books

**GET** `/api/student/books/current`

**Purpose:**

- Display currently borrowed books

---

### 2.3 Get Borrow History

**GET** `/api/student/books/history`

**Purpose:**

- Borrow history table

---

### 2.4 Student Notifications

**GET** `/api/student/notifications`

**Purpose:**

- Fetch all notifications

---

### 2.5 Mark Notification as Read

**PUT** `/api/student/notifications/{notification_id}/read`

---

---

## 3. BOOK DISCOVERY & AVAILABILITY APIs

---

### 3.1 Search Books

**GET** `/api/books/search`

**Query Params:**

```
title
author
category
availability
```

---

### 3.2 Get Book Details

**GET** `/api/books/{book_id}`

---

### 3.3 Subscribe to Availability Notification

**POST** `/api/books/{book_id}/notify`

**Purpose:**

- Notify student when book becomes available

---

---

## 4. DUE DATE, FINE & POLICY APIs

---

### 4.1 Calculate Due Dates

**GET** `/api/rules/borrow-policy`

**Purpose:**

- Return borrowing duration, grace period

---

### 4.2 Student Fine Summary

**GET** `/api/student/fines`

---

---

## 5. ACADEMIC RESOURCES (CIE PAPERS)

---

### 5.1 List Resources

**GET** `/api/resources`

**Query Params:**

```
subject
semester
year
```

---

### 5.2 Download Resource

**GET** `/api/resources/{resource_id}/download`

---

---

## 6. ADMIN APIs

---

## 6.1 Admin Dashboard Analytics

**GET** `/api/admin/dashboard`

**Purpose:**

- Metrics & charts data

---

## 6.2 Borrow & Return Logs

**GET** `/api/admin/logs`

**Filters:**

```
student_id
book_id
date_from
date_to
action
```

---

## 6.3 Book Inventory Management

### Get All Books

**GET** `/api/admin/books`

### Add Book

**POST** `/api/admin/books`

### Update Book

**PUT** `/api/admin/books/{book_id}`

### Delete Book

**DELETE** `/api/admin/books/{book_id}`

---

## 6.4 Student Management

### List Students

**GET** `/api/admin/students`

### Student Detail

**GET** `/api/admin/students/{student_id}`

---

## 6.5 Fine Management

### Get All Fines

**GET** `/api/admin/fines`

### Update Fine Rules

**PUT** `/api/admin/fines/config`

---

## 6.6 Academic Content Management

### Upload Resource

**POST** `/api/admin/resources`

### Delete Resource

**DELETE** `/api/admin/resources/{resource_id}`

---

## 6.7 Notification Control Panel

### Broadcast Announcement

**POST** `/api/admin/notifications/broadcast`

---

## 7. REPORTING & EXPORT APIs

---

### Export Borrow Logs

**GET** `/api/admin/reports/borrow-logs/export`

### Export Student Activity

**GET** `/api/admin/reports/students/export`

---

## 8. SYSTEM & SUPPORT APIs

---

### Health Check

**GET** `/api/health`

---

### Real-Time Trigger Hooks (Internal)

- Borrow return event listener

- Availability notification trigger

- Reminder scheduler (cron / Lambda event)

---

# SECURITY & ACCESS CONTROL

- JWT required for all `/api/*`

- Role-based guards:
  
  - Student APIs → student only
  
  - Admin APIs → admin only

- No direct DB access from frontend

---

# DEPLOYMENT MODEL (AWS)

- Each stack deployed independently using:
  
  ```
  sam build
  sam deploy
  ```

- API Gateway routes mapped to Lambda

- Supabase credentials stored in AWS Secrets Manager

---

## CONCLUSION

This backend:

- Fully supports **every frontend feature**

- Cleanly separates auth and business logic

- Is Lambda-friendly and cost-efficient

- Is evaluation-ready and scalable

---


