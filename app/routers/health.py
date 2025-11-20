# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/19/2025
# Assignment-11: Health Check Router
# File: app/routers/health.py
# ----------------------------------------------------------
# Description:
# Minimal health endpoint for Docker and CI/CD.
# ----------------------------------------------------------

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy"}

