# Import all SQLAlchemy models so Alembic can detect them
from lotkeeper.models.auction import AuctionModel
from lotkeeper.models.auction_datapoint import AuctionDatapointModel
from lotkeeper.models.auction_realm_activity_datapoint import AuctionRealmActivityDatapointModel
from lotkeeper.models.item import ItemModel
from lotkeeper.models.server_realm import ServerRealmModel

# This ensures all models are registered with the metadata
__all__ = [
    "AuctionDatapointModel",
    "AuctionModel",
    "AuctionRealmActivityDatapointModel",
    "ItemModel",
    "ServerRealmModel",
]
