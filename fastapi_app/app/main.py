from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.init_db import connect_to_mongo, close_mongo_connection
from .routes import user_routes, email_routes, auth_routes, admin_routes, settings_routes, logs_routes
from .middleware.admin_logging import AdminActionLoggingMiddleware

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5174",
        "https://application-form-seven-gamma.vercel.app",
        "https://e-cell-rec-admin-panel.vercel.app",
        "https://e-cell.in"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add event handlers
@app.on_event("startup")
async def startup_event():
    """Connect to database on startup"""
    await connect_to_mongo()
    # ensure admin logs index/collection exists (TTL/indexing could be added here later)

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()

# Attach admin logging middleware at module-level so it is registered before the app starts
app.add_middleware(AdminActionLoggingMiddleware)

# Include routers
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(admin_routes.router, prefix=settings.API_PREFIX)
app.include_router(user_routes.router, prefix=settings.API_PREFIX)
app.include_router(email_routes.router, prefix=settings.API_PREFIX)
app.include_router(logs_routes.router, prefix=settings.API_PREFIX)
app.include_router(settings_routes.router, prefix=settings.API_PREFIX)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Recruitment Portal API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy", 
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }
    
