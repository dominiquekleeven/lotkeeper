from datetime import datetime
from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from lotkeeper.api.rate_limits import WEB_RATE_LIMIT
from lotkeeper.config import DIRS
from lotkeeper.dependencies import get_auction_service, get_rate_limiter, get_server_realm_service
from lotkeeper.services.auction_service import AuctionService
from lotkeeper.services.server_realm_service import ServerRealmService

router = APIRouter(prefix="", include_in_schema=False)

if DIRS.LOT_WEB_BUNDLE_DIR.exists():
    router.mount("/static", StaticFiles(directory=str(DIRS.LOT_WEB_BUNDLE_DIR / "static")))


@router.get(
    "/",
    summary="Serve the index.html file from the web dist directory.",
    responses={
        HTTPStatus.OK: {"description": "Index.html file has been served"},
        HTTPStatus.NOT_FOUND: {"description": "Index.html file not found"},
    },
)
@get_rate_limiter().limit(WEB_RATE_LIMIT)
async def serve_index(request: Request) -> FileResponse:
    index_path = Path(DIRS.LOT_WEB_BUNDLE_DIR) / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Could not serve web contents due to misconfiguration",
        )
    return FileResponse(index_path)


@router.get(
    "/sitemap.xml",
    summary="Generate and serve XML sitemap",
    responses={
        HTTPStatus.OK: {"description": "XML sitemap has been generated and served"},
    },
)
@get_rate_limiter().limit(WEB_RATE_LIMIT)
async def serve_sitemap(
    request: Request,
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
    auction_service: AuctionService = Depends(get_auction_service),
) -> Response:
    """Generate and serve a dynamic XML sitemap with all available server realms."""
    server_realms = await server_realm_service.get_server_realms()

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Add main pages
    main_pages = [
        ("/", "1.0", "daily"),
        ("/docs", "0.8", "weekly"),
        ("/faq", "0.7", "monthly"),
        ("/disclaimer", "0.3", "yearly"),
        ("/api/docs", "0.6", "weekly"),
        ("/api/redoc", "0.6", "weekly"),
    ]

    current_date = datetime.now().strftime("%Y-%m-%d")

    for path, priority, changefreq in main_pages:
        sitemap_xml += "  <url>\n"
        sitemap_xml += f"    <loc>https://lotkeeper.net{path}</loc>\n"
        sitemap_xml += f"    <lastmod>{current_date}</lastmod>\n"
        sitemap_xml += f"    <changefreq>{changefreq}</changefreq>\n"
        sitemap_xml += f"    <priority>{priority}</priority>\n"
        sitemap_xml += "  </url>\n"

    # Add dynamic realm routes
    for server_realm in server_realms:
        server_slug = server_realm.server.replace(" ", "-").lower()
        realm_slug = server_realm.realm.replace(" ", "-").lower()

        # Get server realm ID for auction queries
        server_realm_id = await server_realm_service.get_server_realm_id(server_realm.server, server_realm.realm)

        if server_realm_id:
            # Main auction house page
            sitemap_xml += "  <url>\n"
            sitemap_xml += f"    <loc>https://lotkeeper.net/ah/{server_slug}/{realm_slug}</loc>\n"
            sitemap_xml += f"    <lastmod>{current_date}</lastmod>\n"
            sitemap_xml += "    <changefreq>hourly</changefreq>\n"
            sitemap_xml += "    <priority>0.9</priority>\n"
            sitemap_xml += "  </url>\n"

            # Search page
            sitemap_xml += "  <url>\n"
            sitemap_xml += f"    <loc>https://lotkeeper.net/ah/{server_slug}/{realm_slug}/search</loc>\n"
            sitemap_xml += f"    <lastmod>{current_date}</lastmod>\n"
            sitemap_xml += "    <changefreq>daily</changefreq>\n"
            sitemap_xml += "    <priority>0.8</priority>\n"
            sitemap_xml += "  </url>\n"

            # Get top 50 popular items for this realm
            try:
                popular_items = await auction_service.get_top_50_items_by_auction_count(server_realm_id)

                # Add item pages for popular items
                for item in popular_items:
                    if item.id:
                        item_slug = (
                            item.name.replace(" ", "-")
                            .lower()
                            .replace("'", "")
                            .replace('"', "")
                            .replace(":", "")
                            .replace(",", "")
                        )
                        sitemap_xml += "  <url>\n"
                        sitemap_xml += f"    <loc>https://lotkeeper.net/ah/{server_slug}/{realm_slug}/item/{item.id}/{item_slug}</loc>\n"
                        sitemap_xml += f"    <lastmod>{current_date}</lastmod>\n"
                        sitemap_xml += "    <changefreq>daily</changefreq>\n"
                        sitemap_xml += "    <priority>0.7</priority>\n"
                        sitemap_xml += "  </url>\n"
            except Exception:
                # If there's an error getting popular items, just skip item pages for this realm
                pass

    sitemap_xml += "</urlset>\n"

    return Response(content=sitemap_xml, media_type="text/xml", headers={"Content-Type": "text/xml; charset=utf-8"})


@router.get(
    "/{path:path}",
    summary="Serve static files or return index.html for SPA routing.",
    responses={
        HTTPStatus.OK: {"description": "Static file has been served"},
        HTTPStatus.NOT_FOUND: {"description": "Static file not found"},
    },
)
@get_rate_limiter().limit(WEB_RATE_LIMIT)
async def serve_spa(request: Request, path: str) -> FileResponse:
    # Ignore API routes, will only be hit if the endpoint actually doesn't exist
    if path.startswith("api/"):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="API endpoint not found")

    requested_path = Path(DIRS.LOT_WEB_BUNDLE_DIR) / path

    if requested_path.is_file():
        return FileResponse(requested_path)

    index_path = Path(DIRS.LOT_WEB_BUNDLE_DIR) / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Could not serve web contents due to misconfiguration",
        )
    return FileResponse(index_path)
