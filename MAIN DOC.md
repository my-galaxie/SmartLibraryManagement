Understood. Below is a **very detailed, structured functional specification document** for the **Smart Library Website**, covering **everything except Section 7 (Optional / Nice-to-Have features)**.

This document is written so that it can be:

- Included directly in your **project report**

- Used as a **development blueprint**

- Explained clearly to evaluators or guides

Technology assumptions are **Next.js + shadcn/ui + Supabase**, but this document is **feature-focused**, not code-focused.

---

# SMART LIBRARY MANAGEMENT WEBSITE

**Functional Feature Specification Document**

---

## 1. CORE WEBSITE CAPABILITIES (FOUNDATION)

### 1.1 Authentication & Access Control

The website must implement a secure, role-based authentication system using Supabase Auth.

**Key functionality:**

- Users authenticate using email/password or institutional credentials.

- Each authenticated user is assigned a **role** (`student` or `admin`).

- Sessions persist across page refreshes.

- Unauthorized users are redirected to the login page.

- Admin-only routes are protected both at:
  
  - UI level (hidden components)
  
  - Backend level (Supabase Row Level Security).

**Outcome:**

- Students can access only student features.

- Admins have elevated access without needing a separate website.

---

## 2. STUDENT-FACING FEATURES

---

### 2.1 Student Dashboard

The dashboard is the **primary landing page** after student login.

**Displayed information:**

- Student name and ID

- Number of books currently borrowed

- Number of books due soon

- Number of overdue books

- Total fine (if applicable)

- Recent notifications

**Purpose:**

- Provide a quick snapshot of the student’s library status.

- Reduce confusion and manual checking.

---

### 2.2 Borrowed Books Management

This module allows students to track all borrowing activity.

**Current Borrowed Books View:**

- Book title

- Author

- Borrow date

- Due date

- Remaining days to return

- Status indicator:
  
  - Green: Safe
  
  - Yellow: Due soon
  
  - Red: Overdue

**Borrow History View:**

- Complete list of previously borrowed books

- Borrow date and return date

- Status (returned on time / late)

**Purpose:**

- Transparency in borrowing activity.

- Proof of activity for disputes or verification.

---

### 2.3 Due-Date & Reminder System

This is a **core functional and showcase feature**.

**Due date logic:**

- Due date is calculated based on:
  
  - Borrow timestamp from IoT log
  
  - Configured borrowing duration (e.g., 7 or 14 days)

**Reminder triggers:**

- Reminder when:
  
  - Book is due in X days
  
  - Book is due tomorrow
  
  - Book is overdue

**Reminder delivery:**

- In-app notifications

- Optional email notifications

**Admin control:**

- Admin can configure:
  
  - Reminder timing
  
  - Grace period
  
  - Notification frequency

**Purpose:**

- Reduce overdue books.

- Demonstrate automation and intelligence.

---

### 2.4 Book Availability & Discovery

This module allows students to search and explore library resources.

**Search capabilities:**

- Search by:
  
  - Book title
  
  - Author
  
  - Subject
  
  - ISBN / UID

**Filters:**

- Availability status

- Category / department

- Semester relevance

**Book detail page:**

- Title, author, subject

- Availability count

- Borrowed or available state

**Purpose:**

- Improve discoverability.

- Reduce physical library queries.

---

### 2.5 Availability Notification System

Students can subscribe to unavailable books.

**Functionality:**

- “Notify me when available” button

- System monitors return logs

- Notification sent when book becomes available

- Reminder window:
  
  - “Available now – pick up soon”

**Expiry logic:**

- Notification expires if book is borrowed by someone else

- Subscription automatically cleared

**Purpose:**

- Fair access to popular books.

- Smart resource allocation.

---

### 2.6 Fine & Policy Awareness

This module ensures clarity around fines.

**Displayed information:**

- Current fine amount

- Days overdue

- Fine rate per day

- Grace period rules

**Fine behavior:**

- Fine is calculated automatically

- Display-only (no payment integration required)

**Library policy page:**

- Borrowing limits

- Return deadlines

- Fine rules

**Purpose:**

- Reduce disputes.

- Improve accountability.

---

### 2.7 Academic Resources (CIE Papers)

The website also functions as an academic resource portal.

**Features:**

- List of uploaded CIE papers

- Filter by:
  
  - Subject
  
  - Semester
  
  - Year

- Download access for students

**Admin control:**

- Upload and delete PDFs

- Manage visibility

**Purpose:**

- Extend usefulness beyond books.

- Increase system relevance.

---

### 2.8 External Resources & Utilities

**Features include:**

- Dummy redirect button for semester-end downloads

- Announcements board

- Holiday / maintenance notices

**Purpose:**

- Centralize academic communication.

- Add completeness to the platform.

---

## 3. NOTIFICATION & ALERT SYSTEM

---

### 3.1 Notification Types

Supported notifications include:

- Due date reminders

- Overdue alerts

- Book availability alerts

- Admin announcements

- System alerts

---

### 3.2 Notification Channels

**Channels:**

- In-app notification center

- Optional email notifications

**Notification management:**

- Read/unread status

- Notification history

**Purpose:**

- Timely communication.

- Improved engagement.

---

## 4. ADMIN-FACING FEATURES

---

### 4.1 Admin Dashboard (Analytics)

This is the **control center** of the system.

**Displayed metrics:**

- Total books

- Books currently borrowed

- Overdue count

- Active students

- Borrow trends (daily/weekly)

- Peak usage periods

**Visualization:**

- Charts and graphs

- Summary cards

**Purpose:**

- System monitoring.

- Decision support.

---

### 4.2 Borrow & Return Monitoring

Admins can monitor all activity.

**Features:**

- Real-time borrow/return logs

- Filter by:
  
  - Student
  
  - Book
  
  - Date range
  
  - Action type

**Audit nature:**

- Logs are IoT-driven

- Cannot be edited

**Purpose:**

- Transparency.

- Debugging and evaluation.

---

### 4.3 Fine Management

**Admin controls:**

- Configure:
  
  - Fine rate per day
  
  - Grace period

- View fine summaries per student

**Purpose:**

- Policy enforcement.

- Financial clarity.

---

### 4.4 Book Inventory Management

Admins manage book metadata.

**Features:**

- Add/edit book details

- Group multiple copies

- Track availability

- Logical inventory management

**Purpose:**

- Accurate availability calculation.

- Scalable data handling.

---

### 4.5 Student Management

Admins can view student activity.

**Features:**

- Student list

- Borrowing history

- Fine overview

- Warning/flag indicators (visual only)

**Purpose:**

- Monitor behavior.

- Academic accountability.

---

### 4.6 Academic Content Management

Admins manage uploaded resources.

**Capabilities:**

- Upload CIE papers

- Update or remove files

- Control access visibility

**Purpose:**

- Content governance.

- Academic support.

---

### 4.7 Notification Control Panel

Admins manage notification logic.

**Controls:**

- Configure reminder rules

- Broadcast announcements

- Manage templates

**Purpose:**

- Centralized communication control.

---

## 5. REPORTING & VISUALIZATION

---

### 5.1 Reports

Supported reports:

- Borrow frequency

- Overdue trends

- Popular books

- Department-wise usage

**Purpose:**

- Evaluation metrics.

- Project justification.

---

### 5.2 Data Export

Admins can export data in CSV format:

- Borrow logs

- Fine data

- Student activity

**Purpose:**

- External analysis.

- Academic submission.

---

## 6. SYSTEM & TECHNICAL FEATURES

---

### 6.1 Real-Time Updates

- Supabase Realtime integration

- Live availability updates

- Instant UI refresh on borrow/return

---

### 6.2 Role-Based UI Rendering

- Same codebase

- Dynamic UI rendering based on role

- Secure backend enforcement

---

### 6.3 Performance & UX Enhancements

- Skeleton loaders

- Responsive design

- Optimistic UI updates

---

## CONCLUSION

This website:

- Complements your IoT system

- Adds intelligence and automation

- Demonstrates full-stack capability

- Is ideal for academic evaluation

- Is realistic yet implementation-friendly

---

### Next Logical Steps

We can now:

1. Convert this into a **final project report section**

2. Map features to **Supabase tables**

3. Design **page-wise Next.js routing**

4. Define **RLS policies**

5. Create **UI component breakdown (shadcn)**

Tell me how you want to proceed.
