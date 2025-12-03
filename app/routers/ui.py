# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment 11: UI Router (Minimal Placeholder)
# File: app/routers/ui.py
# ----------------------------------------------------------
# Description:
# Provides a simple router that serves index.html.
# Required because main.py imports `router` from this file.
# ----------------------------------------------------------

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Serve the UI homepage."""
    return templates.TemplateResponse("index.html", {"request": request})
