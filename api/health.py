from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    System health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Smart Library API",
        "version": "1.0.0"
    }
