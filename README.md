# Backend README

## Smart Library Management System - Backend API

This is the FastAPI backend for the Smart Library Management System with Supabase authentication.

### Features

- **Auth Stack** (`/auth`)
  - User signup with role assignment
  - Login with JWT token generation
  - Token validation
  - Logout

- **Student APIs** (`/api/student`)
  - Dashboard with summary statistics
  - Current borrowed books
  - Borrow history
  - Notifications management
  - Fines summary

- **Book Discovery APIs** (`/api/books`)
  - Search books with filters
  - Book details
  - Availability subscription

- **Admin APIs** (`/api/admin`)
  - Dashboard analytics
  - Borrow/return logs
  - Book inventory management
  - Student management
  - Fine configuration
  - Broadcast notifications

- **Resources APIs** (`/api/resources`)
  - List academic resources
  - Download resources

- **Policy APIs** (`/api/rules`)
  - Borrow policy information

### Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials

3. **Set up Database**
   - Go to your Supabase project SQL Editor
   - Run `database/schema.sql`
   - Run `database/seed.sql` for sample data

4. **Run the Server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing

Test endpoints using curl:

```bash
# Test health check
curl http://localhost:8000/api/health

# Test signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"student","name":"Test User"}'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── database.py             # Supabase client setup
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .env.example            # Environment template
├── auth/                   # Authentication stack
│   ├── router.py           # Auth endpoints
│   ├── service.py          # Auth business logic
│   └── models.py           # Pydantic models
├── api/                    # Core application stack
│   ├── dependencies.py     # JWT verification, role guards
│   ├── student/            # Student endpoints
│   ├── books/              # Book endpoints
│   ├── admin/              # Admin endpoints
│   ├── resources/          # Resources endpoints
│   ├── rules/              # Policy endpoints
│   └── health.py           # Health check
└── database/               # Database scripts
    ├── schema.sql          # Database schema
    └── seed.sql            # Sample data
```

### Environment Variables

Required environment variables (see `.env.example`):

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SUPABASE_SERVICE_KEY` - Service role key (optional)
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `API_PORT` - Port to run the API (default: 8000)
- `FRONTEND_URL` - Frontend URL for CORS (default: http://localhost:3000)
