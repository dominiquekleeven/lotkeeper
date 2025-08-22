from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from lotkeeper.api.rate_limits import AUCTIONS_RATE_LIMIT, AUCTIONS_STRICT_RATE_LIMIT
from lotkeeper.dependencies import get_auction_service, get_rate_limiter, get_server_realm_service
from lotkeeper.models.auction import Auction, AuctionFilter
from lotkeeper.models.types import PaginatedResponse, PaginationFilter
from lotkeeper.services.auction_service import AuctionService
from lotkeeper.services.server_realm_service import ServerRealmService

router = APIRouter(
    prefix="/api/v1/auctions",
    tags=["auctions"],
)


# --- Constants ---
LIMIT_DEFAULT = 50
LIMIT_MIN = 1
LIMIT_MAX = 1000
OFFSET_DEFAULT = 0
OFFSET_MIN = 0


@router.get(
    "/{server}/{realm}",
    summary="Retrieve auctions for a realm, enforces pagination and allows optional filtering",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved filtered auctions. "
            "Returns a list of filtered auctions for the specified realm."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(AUCTIONS_RATE_LIMIT)
async def get_auctions_filtered(
    request: Request,
    server: str,
    realm: str,
    item_id: int | None = Query(None, ge=1, description="The ID of the item being auctioned"),
    item_name: str | None = Query(None, min_length=1, description="The name of the item being auctioned"),
    item_quality: int | None = Query(None, ge=0, description="The quality of the item being auctioned"),
    item_level: int | None = Query(None, ge=0, description="The level of the item being auctioned"),
    item_class_index: int | None = Query(None, ge=0, description="The index of the class of the item being auctioned"),
    item_class_name: str | None = Query(
        None, min_length=1, description="The name of the class of the item being auctioned"
    ),
    limit: int = Query(LIMIT_DEFAULT, ge=LIMIT_MIN, le=LIMIT_MAX, description="Number of items per page"),
    offset: int = Query(OFFSET_DEFAULT, ge=OFFSET_MIN, description="Number of items to skip"),
    auction_service: AuctionService = Depends(get_auction_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> PaginatedResponse[Auction]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="Realm not found")

    filter = AuctionFilter(
        item_id=item_id,
        item_name=item_name,
        item_quality=item_quality,
        item_level=item_level,
        item_class_index=item_class_index,
        item_class_name=item_class_name,
    )

    pagination = PaginationFilter(limit=limit, offset=offset)
    return await auction_service.get_auctions_paginated(server_realm_id, pagination, filter)


@router.get(
    "/{server}/{realm}/bulk",
    summary="Retrieve all auctions in bulk for a realm. (2/minute rate limit enforced)",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved auctions. "
            "Returns a complete list of all auction listings for the specified realm."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(AUCTIONS_STRICT_RATE_LIMIT)
async def get_bulk_auctions(
    request: Request,
    server: str,
    realm: str,
    auction_service: AuctionService = Depends(get_auction_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[Auction]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")

    auctions = await auction_service.get_auctions(server_realm_id)
    return auctions


@router.get(
    "/{server}/{realm}/count",
    summary="Get the total amount of auctions for a realm",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved the total amount of auctions. "
            "Returns the total number of auction listings in the specified realm."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(AUCTIONS_RATE_LIMIT)
async def get_auctions_count(
    request: Request,
    server: str,
    realm: str,
    auction_service: AuctionService = Depends(get_auction_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> int:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")
    return await auction_service.get_auctions_count(server_realm_id)


@router.get(
    "/{server}/{realm}/value",
    summary="Get the total market value for a realm",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved the total market value. "
            "Returns the combined buyout value of all auction listings in the specified realm in copper."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(AUCTIONS_RATE_LIMIT)
async def get_auctions_value(
    request: Request,
    server: str,
    realm: str,
    auction_service: AuctionService = Depends(get_auction_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> int:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")
    return await auction_service.get_total_value(server_realm_id)


@router.get(
    "/{server}/{realm}/below-vendor-price",
    summary="Retrieve auctions where buyout price is below vendor price",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved auctions below vendor price. "
            "Returns auctions where the buyout price is less than the vendor price, ordered by savings amount."
        },
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(AUCTIONS_RATE_LIMIT)
async def get_below_vendor_price(
    request: Request,
    server: str,
    realm: str,
    auction_service: AuctionService = Depends(get_auction_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[Auction]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="Realm not found")

    return await auction_service.get_auctions_below_vendor_price(server_realm_id)
