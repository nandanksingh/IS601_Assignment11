# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-11: UI Router (HTML Templates)
# File: app/routers/ui.py
# ----------------------------------------------------------
# Description:
# Serves the interactive calculator UI (index.html).
# ----------------------------------------------------------

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/")
def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
