import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

from api.database import database
from api.routers.user import router as user_router
from api.config import config
from api.logging_conf import configure_logging

logger = logging.getLogger(__name__)


# CORS settings
origins = [
    config.FRONTEND_URL,  # Add production frontend domain at some point
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting api")
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.add_middleware(CorrelationIdMiddleware)

# Include routers
app.include_router(user_router)

@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)