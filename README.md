# Smart Library Management System - Backend

RFID-based library management system with automated reminders and analytics.

## 🚀 Features

### Authentication & Authorization
- JWT-based authentication with Supabase
- Role-based access control (Student/Admin)
- Secure Row Level Security (RLS) policies

### Student Features
- 📊 Dashboard with summary statistics
- 📚 View currently borrowed books
- 📜 Complete borrow history
- 🔔 Real-time notifications
- 💰 Fine tracking and payment
- 🔍 Advanced book search
- ⏰ Availability subscriptions

### Admin Features
- 📈 Analytics dashboard with trends
- 📖 Complete book inventory management
- 👥 Student management and monitoring
- 📝 Borrow/return logs with filtering
- 💵 Fine management and configuration
- 📢 Broadcast notifications
- 📄 Academic resources management

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + JWT
- **API Documentation**: Swagger UI / ReDoc

## 📋 Prerequisites

- Python 3.8+
- Supabase account
- Git

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/my-galaxie/SmartLibraryManagement.git
cd SmartLibraryManagement
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Configuration
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Fine Configuration
FINE_PER_DAY=5
GRACE_PERIOD_DAYS=2
BORROW_DURATION_DAYS=14
```

### 4. Set Up Database

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run `database/schema.sql` to create tables and policies
4. (Optional) Run `database/seed.sql` for sample data

### 5. Run the Server

```bash
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

## 📚 API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── database.py             # Supabase client setup
├── requirements.txt        # Python dependencies
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
    ├── seed.sql            # Sample data
    └── reset_database.sql  # Reset script
```

## 🔌 API Endpoints

### Authentication (`/auth`)
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT
- `GET /auth/validate` - Validate JWT token
- `POST /auth/logout` - Logout

### Student (`/api/student`)
- `GET /api/student/dashboard` - Dashboard summary
- `GET /api/student/books/current` - Currently borrowed books
- `GET /api/student/books/history` - Borrow history
- `GET /api/student/notifications` - Get notifications
- `PUT /api/student/notifications/{id}/read` - Mark as read
- `GET /api/student/fines` - Fine summary

### Books (`/api/books`)
- `GET /api/books/search` - Search books
- `GET /api/books/{id}` - Book details
- `POST /api/books/{id}/notify` - Subscribe to availability

### Admin (`/api/admin`)
- `GET /api/admin/dashboard` - Analytics
- `GET /api/admin/logs` - Borrow/return logs
- `GET /api/admin/books` - List all books
- `POST /api/admin/books` - Add new book
- `PUT /api/admin/books/{id}` - Update book
- `DELETE /api/admin/books/{id}` - Delete book
- `GET /api/admin/students` - List students
- `GET /api/admin/students/{id}` - Student details
- `GET /api/admin/fines` - View fines
- `PUT /api/admin/fines/config` - Update fine configuration
- `POST /api/admin/notifications/broadcast` - Send broadcast

### Resources (`/api/resources`)
- `GET /api/resources` - List resources
- `GET /api/resources/{id}/download` - Download resource

### Rules (`/api/rules`)
- `GET /api/rules/borrow-policy` - Get borrow policy

## 🧪 Testing

### Using Postman

See `POSTMAN_TESTING_GUIDE.md` for complete testing instructions.

### Quick Test

1. **Health Check**:
```bash
curl http://localhost:8000/api/health
```

2. **Signup**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"student","name":"Test User"}'
```

3. **Login**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Row Level Security (RLS) in Supabase
- Password hashing via Supabase Auth
- Service role key for admin operations
- Protected endpoints with token verification

## 📝 Database Schema

### Main Tables
- `user_profiles` - User information and roles
- `books` - Book catalog
- `book_copies` - Individual RFID-tagged copies
- `borrows` - Borrowing transactions
- `notifications` - User notifications
- `fines` - Fine records
- `resources` - Academic resources
- `availability_subscriptions` - Book availability alerts
- `system_config` - System configuration

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **Sahana** - *Initial work* - [my-galaxie](https://github.com/my-galaxie)

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Supabase for backend infrastructure
- The open-source community

## 📞 Support

For support, email support@smartlibrary.com or open an issue on GitHub.

---

**Made with ❤️ for smart library management**
