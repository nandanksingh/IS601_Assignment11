# ----------------------------------------------------------
# Author: Nandan Kumar
# Assignment-11: Dockerfile 
# ----------------------------------------------------------
# Description:
#   • Production-ready container for Calculator project
#   • FastAPI application with SQLAlchemy + PostgreSQL client
#   • Playwright + Chromium for E2E tests
#   • Non-root execution for security
# ----------------------------------------------------------

FROM python:3.12-slim

# ----------------------------------------------------------
# Environment Variables
# ----------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# ----------------------------------------------------------
# Install System Dependencies (Chromium Runtime Libraries)
# ----------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libffi-dev \
        postgresql-client \
        curl wget gnupg ca-certificates procps \
        libnss3 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libxkbcommon0 libxcomposite1 libxdamage1 \
        libxfixes3 libxrandr2 libgbm1 libasound2 \
        libpangocairo-1.0-0 libpango-1.0-0 \
        libgtk-3-0 libx11-xcb1 xvfb \
        fonts-unifont fonts-dejavu fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Create Application User
# ----------------------------------------------------------
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -m appuser

# ----------------------------------------------------------
# Install Python Dependencies
# ----------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ----------------------------------------------------------
# Install Playwright (Python package only)
# ----------------------------------------------------------
RUN pip install playwright

# ----------------------------------------------------------
# Install Chromium Browsers (as appuser — critical step)
# ----------------------------------------------------------
USER appuser
RUN mkdir -p /home/appuser/.cache/ms-playwright && \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright \
    playwright install chromium

# ----------------------------------------------------------
# Copy Application Source Code
# ----------------------------------------------------------
USER root
COPY . .
RUN chown -R appuser:appgroup /app

# ----------------------------------------------------------
# Switch to Runtime User
# ----------------------------------------------------------
USER appuser

# ----------------------------------------------------------
# Expose Application Port
# ----------------------------------------------------------
EXPOSE 8000

# ----------------------------------------------------------
# Health Check (always uses localhost:8000)
# ----------------------------------------------------------
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ----------------------------------------------------------
# Default Application Command
# ----------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
