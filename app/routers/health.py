# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: Health Check Router
# File: app/routers/health.py
# ----------------------------------------------------------
# Description:
# Provides a minimal health check endpoint used by:
#   • Docker container HEALTHCHECK
#   • GitHub Actions CI pipeline
#   • Local debugging and uptime monitoring
#
# Must return a simple JSON object:
#       {"status": "healthy"}
# ----------------------------------------------------------

from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health():
    """Simple endpoint confirming that the API is running."""
    return {"status": "healthy"}
