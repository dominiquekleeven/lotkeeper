# --- Base Images for Parallel Builds ------------------------------------------
FROM node:20-slim AS frontend-base
WORKDIR /app/frontend
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

FROM python:3.13-slim AS python-base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# --- Frontend Build Phase -----------------------------------------------------
FROM frontend-base AS frontend-builder
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN rm -rf node_modules package-lock.json && npm install && npm run build:prod

# --- Python Dependencies Phase ------------------------------------------------
FROM python-base AS python-deps
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-cache-dir --no-install-project

# --- Python Source Phase ------------------------------------------------------
FROM python-deps AS python-builder
COPY src/ ./src/

# --- Runtime Phase ------------------------------------------------------------
FROM python:3.13-slim

WORKDIR /app
ARG ENVIRONMENT

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    ENVIRONMENT=${ENVIRONMENT:-production} \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Runtime system deps (including Playwright browser dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcups2 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libx11-6 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxkbcommon0 \
        libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# uv at runtime
RUN pip install uv

# Copy only what runtime needs
COPY pyproject.toml uv.lock README.md ./

# Playwright browsers will be mounted at runtime via Docker Compose

# App code
COPY src/ ./src/
RUN uv sync --no-cache-dir

# Frontend bundle
COPY --from=frontend-builder /app/frontend/dist/ ./data/web/dist/
RUN rm -rf /app/frontend || true

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl --fail --silent http://localhost:8007/health || exit 1

# Run
CMD ["uv", "run", "python", "-m", "lotkeeper.main"]    