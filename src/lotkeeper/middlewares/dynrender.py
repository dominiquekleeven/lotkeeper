# app/middleware_dynrender.py
import asyncio
import hashlib
import os
import re
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from aiocache import Cache, caches
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from loguru import logger
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    Route,
    async_playwright,
)

ALLOWED_HOSTS: set[str] = {"lotkeeper.net", "www.lotkeeper.net"}

# Rendering
RENDER_TIMEOUT_MS: int = 8_000
HEAD_SETTLE_MS: int = 500

# Cache
CACHE_TTL: int = 3600

# Concurrency (pages are created per request)
CONCURRENCY: int = 2

# Resource blocking
BLOCK_RESOURCE_TYPES: set[str] = {"image", "media", "font", "stylesheet"}
BLOCK_URL_PATTERNS: tuple[str, ...] = (
    r"google-analytics\.com",
    r"gtag/js",
    r"clarity\.ms",
    r"facebook\.net",
    r"doubleclick\.net",
    r"googletagmanager\.com",
    r"optimize\.google\.com",
)

# Bot detection
BOT_UA_SUBSTRINGS: tuple[str, ...] = (
    "discordbot",
    "twitterbot",
    "slackbot",
    "facebookexternalhit",
    "linkedinbot",
    "whatsapp",
    "telegrambot",
    "embedly",
    "pinterest",
    "quora link preview",
    "googlebot",
    "bingbot",
    "duckduckbot",
    "baiduspider",
    "yandex",
    "slurp",
)
USER_AGENT: str = "Mozilla/5.0 (compatible; LotkeeperDynamicRenderer/1.3; +https://lotkeeper.net)"

_browser: Browser | None = None
_context: BrowserContext | None = None
_pw: Playwright | None = None

_render_sem = asyncio.Semaphore(CONCURRENCY)


# Helpers
def _is_bot(req: Request) -> bool:
    ua: str = (req.headers.get("user-agent") or "").lower()
    accept: str = (req.headers.get("accept") or "").lower()
    return "text/html" in accept and any(b in ua for b in BOT_UA_SUBSTRINGS)


def _allowed(request: Request) -> bool:
    url = request.url
    if url.hostname not in ALLOWED_HOSTS:
        return False
    path = url.path.lower()
    if any(
        path.endswith(ext)
        for ext in (
            ".js",
            ".css",
            ".map",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".svg",
            ".ico",
            ".json",
            ".txt",
            ".xml",
            ".pdf",
            ".woff",
            ".woff2",
            ".ttf",
            ".otf",
            ".mp4",
            ".webm",
            ".mp3",
            ".wav",
            ".ogg",
        )
    ):
        return False
    return True


def _cache_key(url: str) -> str:
    h: str = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return f"dynrender:{h}"


async def _ensure_browser() -> Browser:
    global _browser, _pw  # noqa: PLW0603
    if _browser:
        return _browser

    worker_pid = os.getpid()
    logger.info(f"Dynrender: starting browser (pid {worker_pid})")

    _pw = await async_playwright().start()

    _browser = await _pw.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-first-run",
            "--no-zygote",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI,BackForwardCache,VizDisplayCompositor",
            "--disable-sync",
            "--disable-default-apps",
            "--mute-audio",
            "--hide-scrollbars",
            "--js-flags=--max-old-space-size=128",
            "--renderer-process-limit=2",
        ],
    )

    logger.info(f"Dynrender: browser ready (pid {worker_pid})")
    return _browser


async def _ensure_context() -> BrowserContext:
    global _context  # noqa: PLW0603
    if _context:
        return _context

    browser = await _ensure_browser()
    _context = await browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1024, "height": 768},
        device_scale_factor=1,
        java_script_enabled=True,
        service_workers="block",
        bypass_csp=True,
    )

    # Route filter
    block_re: re.Pattern[str] | None = re.compile("|".join(BLOCK_URL_PATTERNS)) if BLOCK_URL_PATTERNS else None

    async def _route_filter(route: Route) -> None:
        req = route.request
        if req.resource_type in BLOCK_RESOURCE_TYPES:
            await route.abort()
            return
        if block_re and block_re.search(req.url):
            await route.abort()
            return
        await route.continue_()

    await _context.route("**/*", _route_filter)
    return _context


async def _warm_assets_once() -> None:
    """Navigate once to seed the HTTP cache in the context, then close the temp page."""
    context = await _ensure_context()
    try:
        p = await context.new_page()
        await p.goto("https://lotkeeper.net/", wait_until="domcontentloaded", timeout=5_000)
        await p.wait_for_timeout(200)
        await p.close()
        logger.info("Dynrender: warmed homepage assets into context cache")
    except Exception as exc:
        logger.warning(f"Dynrender warmup failed: {exc}")


async def _close_browser() -> None:
    global _browser, _context, _pw  # noqa: PLW0603

    try:
        if _context:
            await _context.close()
    except Exception:
        pass
    finally:
        _context = None

    try:
        if _browser:
            await _browser.close()
    except Exception:
        pass
    finally:
        _browser = None

    if _pw:
        try:
            await _pw.stop()
        except Exception:
            pass
        finally:
            _pw = None


async def _render_current_url(request: Request) -> str:
    start_time = time.time()
    async with _render_sem:
        sem_wait = time.time() - start_time

        # fresh page per request
        context = await _ensure_context()
        page_t0 = time.time()
        page: Page = await context.new_page()
        page_get = time.time() - page_t0

        try:
            goto_t0 = time.time()
            await page.goto(str(request.url), wait_until="domcontentloaded", timeout=RENDER_TIMEOUT_MS)
            goto_t = time.time() - goto_t0

            # We only need <title> / meta description / OG tags
            wait_t0 = time.time()
            try:
                await page.wait_for_selector(
                    'meta[property="og:title"], meta[name="description"], title',
                    timeout=600,
                )
            except Exception:
                await page.wait_for_timeout(HEAD_SETTLE_MS)
            wait_t = time.time() - wait_t0

            content_t0 = time.time()
            html: str = await page.content()
            content_t = time.time() - content_t0

            total = time.time() - start_time
            worker_pid = os.getpid()
            ua = request.headers.get("user-agent", "unknown")
            logger.info(
                f"Dynrender {request.url.path} - Total: {total:.3f}s - "
                f"SemWait: {sem_wait:.3f}s - PageNew: {page_get:.3f}s - "
                f"Goto: {goto_t:.3f}s - Wait: {wait_t:.3f}s - Content: {content_t:.3f}s - "
                f"PID: {worker_pid} - UA: {ua}"
            )
            return html
        finally:
            try:
                await page.close()
            except Exception:
                pass


async def dynrender_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    if request.method != "GET" or not _allowed(request) or not _is_bot(request):
        return await call_next(request)

    url: str = str(request.url)
    key: str = _cache_key(url)
    cache: Cache = caches.get("default")

    cached_html: str | None = await cache.get(key)
    if cached_html:
        return HTMLResponse(cached_html, headers={"Cache-Control": f"public, max-age={CACHE_TTL}"})

    try:
        html: str = await _render_current_url(request)
        await cache.set(key, html, ttl=CACHE_TTL)
        return HTMLResponse(html, headers={"Cache-Control": f"public, max-age={CACHE_TTL}"})
    except Exception as exc:
        logger.warning(f"Dynrender: fallback to app for {url}: {exc}")
        return await call_next(request)


@asynccontextmanager
async def dynrender_lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # Start browser/context and seed cache once
    await _ensure_context()
    await _warm_assets_once()
    try:
        yield
    finally:
        await _close_browser()
