# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/15/2025
# Assignment-11: Calculation Model, Pydantic Validation,
#                Factory Pattern & Docker Deployment
# File: Dockerfile
# ----------------------------------------------------------
# Description:
# Production-grade Dockerfile for the FastAPI Modular Calculator.
#
# Features:
#   • Python 3.12-slim (small + fast)
#   • PostgreSQL client installed (fixes pg_isready error)
#   • Non-root secure user (appuser)
#   • Layer-cached pip dependency installation
#   • CI/CD-friendly
#   • Healthcheck hitting /health
#   • Uvicorn (2 workers) optimized for API apps
# ----------------------------------------------------------


# ----------------------------------------------------------
# 1. Base Image
# ----------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app


# ----------------------------------------------------------
# 2. Install System Dependencies
# ----------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*


# ----------------------------------------------------------
# 3. Security: Create Non-root User
# ----------------------------------------------------------
RUN groupadd -r appgroup && useradd -r -g appgroup appuser


# ----------------------------------------------------------
# 4. Install Python Dependencies
# ----------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


# ----------------------------------------------------------
# 5. Copy Application Source Code
# ----------------------------------------------------------
# Includes:
#   • main.py (root)
#   • app/ folder
#   • templates/
#   • .env (optional)
COPY . .


# ----------------------------------------------------------
# 6. File Permissions
# ----------------------------------------------------------
RUN chown -R appuser:appgroup /app
USER appuser


# ----------------------------------------------------------
# 7. Expose port + Healthcheck
# ----------------------------------------------------------
EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1


# ----------------------------------------------------------
# 8. Entrypoint — start FastAPI with Uvicorn
# ----------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
