import asyncio
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import typer
import uvicorn
from aiocache import caches
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from lotkeeper.api import (
    agent_route,
    auction_datapoints_route,
    auctions_route,
    health_route,
    items_route,
    server_realms_route,
    web_route,
)
from lotkeeper.common.logging import propagate_logs, setup_loguru
from lotkeeper.config import DIRS, ENV
from lotkeeper.dependencies import get_db, get_rate_limiter
from lotkeeper.infra.db import DB
from lotkeeper.middlewares.dynrender import dynrender_lifespan, dynrender_middleware
from lotkeeper.middlewares.perf import add_performance_middleware

# --- Setup loguru ---
setup_loguru()
propagate_logs()

# --- Typer ---
cli = typer.Typer(help="Lotkeeper API")

# --- Cache ---
caches.set_config(
    {
        "default": {
            "cache": "aiocache.RedisCache",
            "endpoint": ENV.LOT_VALKEY_HOST,
            "port": int(ENV.LOT_VALKEY_PORT),
            "password": getattr(ENV, "LOT_VALKEY_PASSWORD", None),
            "timeout": 2,
            "namespace": "lotkeeper",
            "serializer": {"class": "aiocache.serializers.JsonSerializer"},
        }
    }
)

# --- Constants ---
HOST = "0.0.0.0"
PORT = 8007


# --- Lifespan ---
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    pid = os.getpid()
    logger.info(f"====== Lotkeeper - {ENV.LOT_ENVIRONMENT} - PID {pid} ======")

    if not DIRS.LOT_WEB_BUNDLE_DIR.exists():
        logger.warning(
            f"Note: Web UI Bundle is missing at {DIRS.LOT_WEB_BUNDLE_DIR}, meaning the web UI is not available"
        )

    # Connect DB
    db = get_db()
    await db.connect()

    if ENV.is_prod():  # add dynrender for production only
        async with dynrender_lifespan(_app):
            yield
    else:
        yield


# --- FastAPI app ---
app = FastAPI(
    default_response_class=ORJSONResponse,
    root_path="",
    title="Lotkeeper",
    description="A comprehensive auction house data and statistics service for WoW servers",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# --- Middlewares ---
if ENV.is_prod():
    app.middleware("http")(dynrender_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ENV.LOT_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance logging
add_performance_middleware(
    app,
    log_slow_requests=True,
    slow_request_threshold=1.0,
    log_all_requests=True,
    exclude_paths={"/health", "/metrics"},
)

# Rate limiter
app.state.limiter = get_rate_limiter()
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# --- Routes ---
app.include_router(health_route.router)
app.include_router(server_realms_route.router)
app.include_router(auctions_route.router)
app.include_router(items_route.router)
app.include_router(auction_datapoints_route.router)
app.include_router(agent_route.router)
app.include_router(web_route.router)

# --- Tags ---
app.openapi_tags = [
    {"name": "server-realms", "description": "Server and realm data"},
    {"name": "auctions", "description": "Raw auction listings and details"},
    {"name": "items", "description": "Item metadata"},
    {"name": "auction-datapoints", "description": "Buyout auction analytics and trends"},
    {"name": "health", "description": "Health check and other status related endpoints"},
]

# --- Extra guards for production ---
if ENV.is_prod() and ENV.LOT_ALLOWED_ORIGINS == ["*"]:
    logger.critical("ALLOWED_ORIGINS is set to * in production")
    raise ValueError("ALLOWED_ORIGINS is set to * in production")


# --- Commands ---
@cli.command()
def start() -> None:
    """Start the FastAPI application"""
    if ENV.is_prod():
        worker_count = os.cpu_count() or 1
    else:
        worker_count = 1

    uvicorn.run(
        "lotkeeper.main:app",
        host=HOST,
        port=PORT,
        reload=ENV.is_dev(),
        log_config=None,
        log_level=None,
        workers=worker_count,
    )


@cli.command()
def clean_db() -> None:
    """Clean the database for a fresh install"""

    async def clean() -> None:
        db = DB()
        async with db.engine.begin() as conn:
            await db._clean_database(conn)
        logger.info("clean-db command executed successfully")

    asyncio.run(clean())


# --- Default callback when no command is given ---
@cli.callback(invoke_without_command=True)
def _default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        start()


# --- Main ---
if __name__ == "__main__":
    cli()
