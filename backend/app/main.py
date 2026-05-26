from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.config import get_settings
from app.database import init_db, close_db
from app.core.memory_manager import memory_manager
from app.api.routes import chat, agents, memory, websocket
from app.utils.errors import register_exception_handlers
from app.utils.logging import setup_logging

# Setup logging
setup_logging()

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Lumina AI Agents", version=settings.APP_VERSION)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize memory manager
    await memory_manager.initialize()
    logger.info("Memory manager initialized")

    yield

    # Cleanup
    await memory_manager.close()
    await close_db()
    logger.info("Shutting down Lumina AI Agents")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI Operating System with multi-agent orchestration",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(websocket.router, tags=["websocket"])
