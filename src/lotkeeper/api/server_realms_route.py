from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from lotkeeper.api.rate_limits import SERVER_REALMS_RATE_LIMIT
from lotkeeper.dependencies import get_rate_limiter, get_server_realm_service
from lotkeeper.models.server_realm import ServerRealm, ServerRealmFactory
from lotkeeper.services.server_realm_service import ServerRealmService

router = APIRouter(
    prefix="/api/v1/server-realms",
    tags=["server-realms"],
)


@router.get(
    "",
    summary="Get all server and realm combinations",
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved all server realms. Returns a list of server and realm combinations",
        },
    },
)
@get_rate_limiter().limit(SERVER_REALMS_RATE_LIMIT)
async def get_server_realms(
    request: Request,
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
) -> list[ServerRealm]:
    realms = await server_realm_service.get_server_realms()
    views = ServerRealmFactory.get_server_realms(realms)

    return views


@router.get(
    "/{server_slug}/{realm_slug}",
    summary="Get the server realm for a given combination of server-slug and realm-slug",
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved the server realm",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The server realm combination could not be found",
        },
    },
)
async def get_specific_server_realm_combination(
    request: Request,
    server_realm_service: ServerRealmService = Depends(get_server_realm_service),
    server_slug: str = Path(..., description="The slug of the server (server-name)"),
    realm_slug: str = Path(..., description="The slug of the realm (realm-name)"),
) -> ServerRealm:
    server_realm = await server_realm_service.get_server_realm_by_slugs(server_slug, realm_slug)

    if server_realm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The server realm combination could not be found"
        )

    return ServerRealmFactory.get(server_realm)
