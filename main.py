from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import logging
from fastapi import Request
import time
import json
from starlette.middleware.base import BaseHTTPMiddleware


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Read body properly
        body = await request.body()
        
        # Re-inject body for next handler
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
        
        # Log Request
        log_msg = f"REQUEST: {request.method} {request.url}"
        try:
            if body:
                log_msg += f" Body: {body.decode()}"
        except:
            log_msg += " Body: (binary/unreadable)"
        
        logger.info(log_msg)
            
        # Process Request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log Response
            logger.info(f"RESPONSE: {response.status_code} ({process_time:.4f}s)")
                
            return response
        except Exception as e:
            logger.error(f"ERROR: {str(e)}")
            raise

app.add_middleware(LoggingMiddleware)

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
