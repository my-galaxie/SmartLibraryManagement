from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import logging

# Import routers
from auth.router import router as auth_router
from api.student.router import router as student_router
from api.books.router import router as books_router
from api.admin.router import router as admin_router
from api.resources.router import router as resources_router
from api.rules.router import router as rules_router
from api.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Library Management System API",
    description="Backend API for Smart Library System with Supabase Authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Auth Stack
app.include_router(auth_router)

# Core Application Stack
app.include_router(student_router, prefix="/api")
app.include_router(books_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(resources_router, prefix="/api")
app.include_router(rules_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Smart Library Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    logger.info("🚀 Smart Library API starting up...")
    logger.info(f"📚 Supabase URL: {settings.supabase_url}")
    logger.info(f"🌐 Frontend URL: {settings.frontend_url}")
    logger.info(f"🔧 API Port: {settings.api_port}")
    logger.info("✅ API ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    logger.info("👋 Smart Library API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
