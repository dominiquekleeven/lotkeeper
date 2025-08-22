"""Application dependencies.

Contains global dependencies for the application, they are used for dependency injection
"""

from functools import lru_cache

from slowapi import Limiter
from slowapi.util import get_remote_address

from lotkeeper.config import ENV
from lotkeeper.services.auction_service import AuctionService
from lotkeeper.services.datapoint_service import DatapointService
from lotkeeper.services.item_service import ItemService
from lotkeeper.services.server_realm_service import ServerRealmService

from .infra.db import DB


# --- Dependencies ---
def get_rate_limiter() -> Limiter:
    """Get the rate limiter instance"""

    return Limiter(key_func=get_remote_address, storage_uri=f"redis://{ENV.LOT_VALKEY_HOST}:{ENV.LOT_VALKEY_PORT}")


@lru_cache(maxsize=1)
def get_db() -> DB:
    """Get the database manager instance"""

    return DB()


@lru_cache(maxsize=1)
def get_datapoint_service() -> DatapointService:
    """Get the auction datapoint service instance"""

    return DatapointService(get_db())


@lru_cache(maxsize=1)
def get_auction_service() -> AuctionService:
    """Get the auction service instance"""

    return AuctionService(get_db(), get_datapoint_service())


@lru_cache(maxsize=1)
def get_item_service() -> ItemService:
    """Get the item service instance"""

    return ItemService(get_db())


@lru_cache(maxsize=1)
def get_server_realm_service() -> ServerRealmService:
    """Get the server realm service instance"""

    return ServerRealmService(get_db())
