from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from lotkeeper.api.rate_limits import ITEMS_RATE_LIMIT, ITEMS_STRICT_RATE_LIMIT
from lotkeeper.dependencies import get_item_service, get_rate_limiter, get_server_realm_service
from lotkeeper.models.item import Item, ItemFilter
from lotkeeper.models.types import PaginatedResponse, PaginationFilter
from lotkeeper.services.item_service import ItemService
from lotkeeper.services.server_realm_service import ServerRealmService

router = APIRouter(
    prefix="/api/v1/items",
    tags=["items"],
)


# --- Constants ---
LIMIT_DEFAULT = 50
LIMIT_MIN = 1
LIMIT_MAX = 1000
OFFSET_DEFAULT = 0
OFFSET_MIN = 0


@router.get(
    "/{server}/{realm}",
    summary="Retrieve items for a realm, enforces pagination and allows optional filtering",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved filtered items. "
            "Returns a list of filtered items for the specified realm."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(ITEMS_RATE_LIMIT)
async def get_items_filtered(
    request: Request,
    server: str,
    realm: str,
    id: int | None = Query(None, ge=1, description="The ID of the item"),
    name: str | None = Query(None, min_length=1, description="The name of the item"),
    quality: int | None = Query(None, ge=0, description="The quality of the item"),
    level: int | None = Query(None, ge=0, description="The level of the item"),
    class_index: int | None = Query(None, ge=0, description="The index of the class of the item"),
    class_name: str | None = Query(None, min_length=1, description="The name of the class of the item"),
    limit: int = Query(LIMIT_DEFAULT, ge=LIMIT_MIN, le=LIMIT_MAX, description="Number of items per page"),
    offset: int = Query(OFFSET_DEFAULT, ge=OFFSET_MIN, description="Number of items to skip"),
    item_service: ItemService = Depends(get_item_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> PaginatedResponse[Item]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="Realm not found")

    filter = ItemFilter(
        id=id,
        name=name,
        quality=quality,
        level=level,
        class_index=class_index,
        class_name=class_name,
    )

    pagination = PaginationFilter(limit=limit, offset=offset)
    return await item_service.get_items_paginated(server_realm_id, pagination, filter)


@router.get(
    "/{server}/{realm}/bulk",
    summary="Retrieve all items in bulk for a realm. (2/minute rate limit enforced)",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved items. Returns a complete list of all items for the specified realm."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(ITEMS_STRICT_RATE_LIMIT)
async def get_bulk_items(
    request: Request,
    server: str,
    realm: str,
    item_service: ItemService = Depends(get_item_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[Item]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")

    items = await item_service.get_items(server_realm_id)
    return items


@router.get(
    "/{server}/{realm}/count",
    summary="Get the total amount of items for a realm",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved the total amount of items. "
            "Returns the total number of items in the specified realm."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(ITEMS_RATE_LIMIT)
async def get_items_count(
    request: Request,
    server: str,
    realm: str,
    item_service: ItemService = Depends(get_item_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> int:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")
    return await item_service.get_item_count(server_realm_id)
