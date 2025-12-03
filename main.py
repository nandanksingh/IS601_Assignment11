# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: FastAPI Application Entrypoint 
# File: main.py
# ----------------------------------------------------------
# Description:
# Main entrypoint for the FastAPI Modular Calculator project.
#
# Responsibilities:
#   • Create FastAPI app instance
#   • Enable CORS middleware for UI & Playwright
#   • Register routers: auth, health, calc, ui
#   • Initialize database tables on startup
#   • Seed default user (ONLY outside pytest)
#   • Serve templates/index.html at "/"
# ----------------------------------------------------------

import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.database.dbase import init_db, seed_default_user

# Routers
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.calc import router as calc_router
from app.routers.ui import router as ui_router


# ----------------------------------------------------------
# Create FastAPI app
# ----------------------------------------------------------
app = FastAPI(
    title="FastAPI Modular Calculator",
    description="Assignment-11: Calculation Model • Factory Pattern • Pydantic v2",
    version="1.0.0",
)

# ----------------------------------------------------------
# Logging Setup
# ----------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# ----------------------------------------------------------
# Template Loader
# ----------------------------------------------------------
templates = Jinja2Templates(directory="templates")

# ----------------------------------------------------------
# CORS Middleware
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# Register Routers
# ----------------------------------------------------------
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(health_router, tags=["Health"])
app.include_router(calc_router, tags=["Calculator"])  # final: /calc/compute
app.include_router(ui_router, prefix="/ui", tags=["UI"])

# ----------------------------------------------------------
# Startup Event — DB Initialization + Conditional Seeding
# ----------------------------------------------------------
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()

    # VERY IMPORTANT:
    # Prevent seeding during pytest so we avoid duplicate users
    if os.getenv("ENV", "").lower() != "testing":
        logger.info("Seeding default user...")
        seed_default_user()

    logger.info("Startup sequence complete.")


# ----------------------------------------------------------
# Serve Root UI — GET /
# ----------------------------------------------------------
@app.get("/", tags=["UI"])
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )
