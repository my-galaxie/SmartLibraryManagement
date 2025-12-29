# Smart Library System - Setup Guide

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ and npm installed
- Supabase account and project created
- Git (optional)

## Quick Start Guide

### Step 1: Database Setup (Supabase)

1. **Go to your Supabase project** at [https://supabase.com/dashboard](https://supabase.com/dashboard)

2. **Navigate to SQL Editor** (left sidebar)

3. **Execute Database Schema**:
   - Copy the entire contents of `backend/database/schema.sql`
   - Paste into the SQL Editor
   - Click "Run" to create all tables, policies, and triggers

4. **Execute Seed Data** (Optional - for testing):
   - Copy the contents of `backend/database/seed.sql`
   - Paste into the SQL Editor
   - Click "Run" to populate sample data

### Step 2: Backend Setup

1. **Navigate to backend folder**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - The `.env` file already exists with your Supabase credentials
   - **IMPORTANT**: You may need to add your Supabase Service Role Key (optional, for admin features)
   - Find it in: Supabase Dashboard → Settings → API → service_role key (secret)

4. **Start the Backend Server**:
   ```bash
   python main.py
   ```
   
   OR using uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. **Verify Backend is Running**:
   - Open browser: http://localhost:8000/docs
   - You should see the FastAPI Swagger documentation

### Step 3: Frontend Setup

1. **Navigate to frontend folder**:
   ```bash
   cd Frontend/my-app
   ```

2. **Create Environment File**:
   Create a file named `.env.local` with:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://xxqqgltsrycvhkgqquek.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4cXFnbHRzcnljdmhrZ3FxdWVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NDY3OTEsImV4cCI6MjA3OTAyMjc5MX0.81gNAzUC9DcLBmX1alTS64lEIu0GESKzmwt0HNltuE0
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Install Dependencies** (if not already done):
   ```bash
   npm install
   ```

4. **Start the Frontend Server**:
   ```bash
   npm run dev
   ```

5. **Open the Application**:
   - Open browser: http://localhost:3000
   - You should see the Smart Library landing page

### Step 4: Test the Application

1. **Create an Account**:
   - Click "Login" → "Sign up"
   - Fill in your details
   - Choose role: Student or Admin
   - Click "Sign up"

2. **Login**:
   - You'll be automatically logged in after signup
   - Or use the login page with your credentials

3. **Test Student Features** (if you signed up as student):
   - View dashboard
   - Search for books
   - View notifications

4. **Test Admin Features** (if you signed up as admin):
   - View analytics dashboard
   - Manage books inventory
   - View borrow logs
   - Manage students

## Project Structure

```
dtl/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration
│   ├── database.py             # Supabase client
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── auth/                   # Authentication stack
│   │   ├── router.py
│   │   ├── service.py
│   │   └── models.py
│   ├── api/                    # Core application stack
│   │   ├── dependencies.py
│   │   ├── student/
│   │   ├── books/
│   │   ├── admin/
│   │   ├── resources/
│   │   ├── rules/
│   │   └── health.py
│   └── database/               # Database scripts
│       ├── schema.sql
│       └── seed.sql
│
└── Frontend/my-app/
    ├── app/                    # Next.js app directory
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── login/
    │   ├── signup/
    │   ├── student/
    │   └── admin/
    ├── components/             # React components
    │   ├── ui/
    │   ├── student-nav.tsx
    │   └── admin-nav.tsx
    ├── contexts/               # React contexts
    │   └── AuthContext.tsx
    ├── lib/                    # Utilities
    │   ├── supabase.ts
    │   └── api.ts
    ├── .env.local              # Frontend environment variables
    └── package.json
```

## API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints:

**Authentication** (`/auth`):
- POST `/auth/signup` - Register new user
- POST `/auth/login` - Login and get JWT
- GET `/auth/validate` - Validate JWT token
- POST `/auth/logout` - Logout

**Student** (`/api/student`):
- GET `/api/student/dashboard` - Dashboard summary
- GET `/api/student/books/current` - Currently borrowed books
- GET `/api/student/books/history` - Borrow history
- GET `/api/student/notifications` - Notifications
- PUT `/api/student/notifications/{id}/read` - Mark as read
- GET `/api/student/fines` - Fine summary

**Books** (`/api/books`):
- GET `/api/books/search` - Search books
- GET `/api/books/{id}` - Book details
- POST `/api/books/{id}/notify` - Subscribe to availability

**Admin** (`/api/admin`):
- GET `/api/admin/dashboard` - Analytics
- GET `/api/admin/logs` - Borrow/return logs
- GET/POST/PUT/DELETE `/api/admin/books` - Manage books
- GET `/api/admin/students` - List students
- GET `/api/admin/fines` - View fines
- POST `/api/admin/notifications/broadcast` - Send notifications

## Troubleshooting

### Backend Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database connection errors**: Check your Supabase URL and keys in `.env`

3. **Port already in use**: Change the port in `backend/.env`:
   ```
   API_PORT=8001
   ```

### Frontend Issues

1. **Module not found**: Install dependencies
   ```bash
   npm install
   ```

2. **Environment variables not loading**: Make sure `.env.local` exists and is properly formatted

3. **CORS errors**: Ensure backend is running and CORS is configured correctly in `main.py`

4. **Authentication not working**: Check that both backend and frontend are using the same Supabase credentials

## Next Steps

1. **Populate the database** with real book data
2. **Integrate with RFID hardware** (if available)
3. **Add email notifications** using SendGrid or similar
4. **Deploy to production** (backend to AWS Lambda, frontend to Vercel)

## Additional Notes

-  The user roles are: `student` and `admin`
- JWT tokens are stored in localStorage
- Protected routes are enforced client-side and server-side
- RLS (Row Level Security) is enabled in Supabase for data protection

## Support

If you encounter issues:
1. Check backend logs in the terminal
2. Check browser console for frontend errors
3. Verify database tables were created correctly in Supabase
4. Ensure all environment variables are set correctly
