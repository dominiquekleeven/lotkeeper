from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from lotkeeper.api.rate_limits import AUCTION_DATAPOINTS_RATE_LIMIT
from lotkeeper.dependencies import get_datapoint_service, get_rate_limiter, get_server_realm_service
from lotkeeper.models.auction_datapoint import (
    AuctionItemActivityHourlySummary,
    AuctionItemPriceHourlySummary,
)
from lotkeeper.models.auction_realm_activity_datapoint import (
    AuctionRealmActivityDatapoint,
)
from lotkeeper.services.datapoint_service import DatapointService
from lotkeeper.services.server_realm_service import ServerRealmService

router = APIRouter(
    prefix="/api/v1/auctions/datapoints",
    tags=["auction-datapoints"],
)


def _get_timestamp_31_days_ago() -> int:
    return int((datetime.now() - timedelta(days=31)).timestamp())


def _get_current_timestamp() -> int:
    return int(datetime.now().timestamp())


@router.get(
    "/{server}/{realm}/{item_id}/price-hourly-summary",
    summary="Get hourly buyout price datapoints for an item within the given time period",
    responses={
        HTTPStatus.OK: {"description": "Successfully retrieved hourly price datapoints within the given time period."},
        HTTPStatus.NOT_FOUND: {"description": "The server realm combination could not be found"},
    },
)
@get_rate_limiter().limit(AUCTION_DATAPOINTS_RATE_LIMIT)
async def get_auction_item_price_hourly_summary(
    request: Request,
    server: str,
    realm: str,
    item_id: int,
    from_timestamp: int = Query(
        _get_timestamp_31_days_ago(), description="Start timestamp in epoch seconds, defaults to 31 days ago"
    ),
    to_timestamp: int = Query(
        _get_current_timestamp(), description="End timestamp in epoch seconds, defaults to current timestamp"
    ),
    datapoint_service: DatapointService = Depends(get_datapoint_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[AuctionItemPriceHourlySummary]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")

    # Create datetime objects from the epoch seconds
    from_dt = datetime.fromtimestamp(from_timestamp)
    to_dt = datetime.fromtimestamp(to_timestamp)

    return await datapoint_service.get_auction_item_price_hourly_summary(item_id, server_realm_id, from_dt, to_dt)


@router.get(
    "/{server}/{realm}/{item_id}/activity-hourly-summary",
    summary="Get hourly buyout activity datapoints for an item within the given time period",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved hourly buyout activity datapoints within the given time period."
        },
    },
)
@get_rate_limiter().limit(AUCTION_DATAPOINTS_RATE_LIMIT)
async def get_auction_item_activity_hourly_summary(
    request: Request,
    server: str,
    realm: str,
    item_id: int,
    from_timestamp: int = Query(
        _get_timestamp_31_days_ago(), description="Start timestamp in epoch seconds, defaults to 31 days ago"
    ),
    to_timestamp: int = Query(
        _get_current_timestamp(), description="End timestamp in epoch seconds, defaults to current timestamp"
    ),
    datapoint_service: DatapointService = Depends(get_datapoint_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[AuctionItemActivityHourlySummary]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")

    # Convert epoch timestamps to datetime objects
    from_dt = datetime.fromtimestamp(from_timestamp)
    to_dt = datetime.fromtimestamp(to_timestamp)

    return await datapoint_service.get_auction_item_activity_hourly_summary(item_id, server_realm_id, from_dt, to_dt)


@router.get(
    "/{server}/{realm}/activity-hourly-summary",
    summary="Get hourly realm buyout activity datapoints for all items within the given time period",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully retrieved hourly realm buyout activity datapoints within the given time period."
        },
    },
)
@get_rate_limiter().limit(AUCTION_DATAPOINTS_RATE_LIMIT)
async def get_auction_realm_activity_hourly_summary(
    request: Request,
    server: str,
    realm: str,
    from_timestamp: int = Query(
        _get_timestamp_31_days_ago(), description="Start timestamp in epoch seconds, defaults to 31 days ago"
    ),
    to_timestamp: int = Query(
        _get_current_timestamp(), description="End timestamp in epoch seconds, defaults to current timestamp"
    ),
    datapoint_service: DatapointService = Depends(get_datapoint_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[AuctionRealmActivityDatapoint]:
    server_realm_id = await server_realm_service.get_server_realm_id(server, realm)
    if not server_realm_id:
        raise HTTPException(status_code=404, detail="The server realm combination could not be found")

    # Convert epoch timestamps to datetime objects
    from_dt = datetime.fromtimestamp(from_timestamp)
    to_dt = datetime.fromtimestamp(to_timestamp)

    return await datapoint_service.get_auction_realm_activity_datapoints(server_realm_id, from_dt, to_dt)
