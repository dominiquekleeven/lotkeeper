from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from loguru import logger

from lotkeeper.api.rate_limits import AGENT_RATE_LIMIT
from lotkeeper.config import ENV
from lotkeeper.dependencies import (
    get_auction_service,
    get_datapoint_service,
    get_rate_limiter,
    get_server_realm_service,
)
from lotkeeper.models.auction import AuctionData
from lotkeeper.security.agent_access import verify_agent_access_token
from lotkeeper.services.auction_service import AuctionService
from lotkeeper.services.datapoint_service import DatapointService
from lotkeeper.services.server_realm_service import ServerRealmService

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["agent"],
    include_in_schema=ENV.is_dev(),
    dependencies=[Depends(verify_agent_access_token)],
)


@dataclass
class AuctionDataValidationResult:
    valid: bool
    new_count: int
    previous_count: int | None
    threshold: int | None
    decrease_percentage: float | None
    reason: str


@router.post(
    "/auctions",
    summary="Submit a snapshot of all auction listings for a given server and realm",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Auction data has been submitted, processed and stored by the server."
        },
    },
)
@get_rate_limiter().limit(AGENT_RATE_LIMIT)
async def submit_auction_data(
    request: Request,
    data: AuctionData,
    background_tasks: BackgroundTasks,
    auction_service: AuctionService = Depends(get_auction_service),
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
    datapoint_service: DatapointService = Depends(get_datapoint_service),
) -> Response:
    server_realm_id = await server_realm_service.get_server_realm_id(data.server, data.realm)

    # If the realm does not exist, explicitly create it
    if not server_realm_id:
        logger.info(
            f"Received auction data for realm {data.server}/{data.realm} that does not exist, the realm will be created"
        )
        server_realm_id = (await server_realm_service.create_server_realm(data.server, data.realm)).id

    # Validate that the new total of active auctions is at least 80% of the previous total
    validation_result = await validate_auction_count(datapoint_service, server_realm_id, len(data.auctions))
    if not validation_result.valid:
        logger.warning(
            f"Auction count validation failed for server realm {server_realm_id} ({data.server}/{data.realm}): "
            f"new_count={validation_result.new_count}, "
            f"previous_count={validation_result.previous_count}, "
            f"threshold_80_percent={validation_result.threshold}, "
            f"decrease_percentage={validation_result.decrease_percentage:.1f}% - "
            f"this anomaly is not accepted"
        )
        return Response(status_code=status.HTTP_406_NOT_ACCEPTABLE)

    # Replace auctions for the given realm
    await auction_service.truncate_and_insert_auctions(server_realm_id, data)

    # Add bg task for upserting realm activity datapoints
    background_tasks.add_task(
        datapoint_service.upsert_auction_realm_activity_datapoints, server_realm_id, delay_seconds=30
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def validate_auction_count(
    datapoint_service: DatapointService, server_realm_id: int, new_total_auctions: int
) -> AuctionDataValidationResult:
    """
    Validate that the new total of active auctions is at least 80% of the previous total

    Returns:
        dict: Contains validation result with detailed metrics
    """

    # Get the last total auctions datapoint
    last_known_total = await datapoint_service.get_auction_realm_activity_datapoints(
        server_realm_id, datetime.now() - timedelta(hours=1), datetime.now()
    )

    # If no datapoint is found, then it's OK to submit
    if not last_known_total:
        return AuctionDataValidationResult(
            valid=True,
            new_count=new_total_auctions,
            previous_count=None,
            threshold=None,
            decrease_percentage=None,
            reason="No previous data available",
        )

    previous_count = last_known_total[0].total_auctions
    threshold = int(previous_count * 0.8)
    is_valid = new_total_auctions >= threshold
    decrease_percentage = ((previous_count - new_total_auctions) / previous_count) * 100 if previous_count > 0 else 0

    return AuctionDataValidationResult(
        valid=is_valid,
        new_count=new_total_auctions,
        previous_count=previous_count,
        threshold=threshold,
        decrease_percentage=decrease_percentage,
        reason="Validation completed",
    )
