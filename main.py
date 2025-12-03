# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Modular API Architecture + Database Storage
# File: main.py
# ----------------------------------------------------------
# Description:
# Central FastAPI application entrypoint.
#
# Loads modular routers for:
#   • Authentication (JWT + Users)
#   • Calculator API (Factory + DB-backed)
#   • UI routes (index.html with Jinja2)
#   • Health check endpoint
#
# Features:
#   • Pydantic v2-ready configuration
#   • CORS middleware (development safe)
#   • Automatic DB initialization on startup
#   • Clean logging setup
# ----------------------------------------------------------

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import logging

# Core settings and DB initialization
from app.core.config import settings
from app.database.dbase import init_db

# Routers
from app.routers.auth import router as auth_router
from app.routers.calc import router as calc_router
from app.routers.ui import router as ui_router
from app.routers.health import router as health_router


# ----------------------------------------------------------
# Application Initialization
# ----------------------------------------------------------
app = FastAPI(
    title="FastAPI Modular Calculator",
    description="Assignment-11: Calculation Model + Factory + JWT + PostgreSQL",
    version="1.0.0",
)


# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("main")


# ----------------------------------------------------------
# Template Loader (UI)
# ----------------------------------------------------------
templates = Jinja2Templates(directory="templates")


# ----------------------------------------------------------
# CORS Settings (Dev-safe, open)
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------
# Include Routers
# IMPORTANT FIX:
#   calc_router already has prefix="/calc"
#   → so DO NOT prefix again!!
# ----------------------------------------------------------
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(calc_router, tags=["Calculations"])  # FIXED ✔
app.include_router(ui_router, prefix="/ui", tags=["UI"])
app.include_router(health_router, tags=["Health"])


# ----------------------------------------------------------
# Startup Hook (Initialize Database)
# ----------------------------------------------------------
@app.on_event("startup")
def on_startup():
    """Initialize database tables when FastAPI boots."""
    logger.info("Starting application… initializing database.")
    init_db()
    logger.info("Database initialized successfully.")


# ----------------------------------------------------------
# Root Homepage Route
# ----------------------------------------------------------
@app.get("/", tags=["Root"])
def home(request: Request):
    """
    Must return index.html.
    Required for:
      • E2E tests (Playwright)
      • Browser UI
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )
