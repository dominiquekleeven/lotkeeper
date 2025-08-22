from fastapi import APIRouter, Request, status

from lotkeeper.api.rate_limits import HEALTH_RATE_LIMIT
from lotkeeper.dependencies import get_rate_limiter

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get(
    "",
    summary="Get the health status of the server",
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved health check. Returns a dictionary with the status of the server",
        },
    },
)
@get_rate_limiter().limit(HEALTH_RATE_LIMIT)
async def health_check(request: Request) -> dict[str, str]:
    return {"status": "ok"}
