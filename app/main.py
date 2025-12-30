"""
BoosterBoxPro FastAPI Application
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting BoosterBoxPro API...")
    try:
        await init_db()
        print("✅ Database connection initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize database: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down BoosterBoxPro API...")


# Create FastAPI application
app = FastAPI(
    title="BoosterBoxPro API",
    description="Market intelligence platform for sealed TCG booster boxes",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "BoosterBoxPro API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


@app.get("/admin")
async def admin_panel():
    """Redirect to admin panel"""
    from fastapi.responses import FileResponse
    import os
    
    admin_path = os.path.join("app", "static", "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    else:
        return {"message": "Admin panel not found. Access via /static/admin.html"}


# Mount static files (for admin panel)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
from app.routers import admin, booster_boxes
app.include_router(admin.router, prefix="/api/v1")
app.include_router(booster_boxes.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

