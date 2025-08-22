from dataclasses import dataclass

from pydantic import BaseModel, Field
from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from lotkeeper.models.base.db_model import DbModel
from lotkeeper.models.item import Item


class AuctionModel(DbModel):
    __tablename__ = "auctions"
    __table_args__ = (
        Index("ix_auctions_item_server_realm", "item_id", "server_realm_id"),
        ForeignKeyConstraint(["server_realm_id"], ["server_realms.id"]),
        ForeignKeyConstraint(["item_id", "server_realm_id"], ["items.id", "items.server_realm_id"]),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    server_realm_id: Mapped[int] = mapped_column(index=True)

    item_id: Mapped[int] = mapped_column(index=True)
    auction_unit_buyout_price: Mapped[int] = mapped_column(index=True)
    auction_unit_starting_bid_price: Mapped[int] = mapped_column(index=True)
    auction_quantity: Mapped[int]


class Auction(BaseModel):
    model_config = {"json_schema_extra": {"description": "An auction listing for an item"}}
    item: Item = Field(description="The item being auctioned")
    unit_buyout_price: int = Field(description="The buyout price in copper", ge=0)
    unit_starting_bid_price: int = Field(description="The starting bid price in copper", ge=0)
    quantity: int = Field(description="The quantity being auctioned", gt=0)


class AuctionData(BaseModel):
    model_config = {
        "json_schema_extra": {"description": "A snapshot of all auction listings for a given server and realm"}
    }

    server: str = Field(description="The server of the realm", min_length=3)
    realm: str = Field(description="The realm of the auctions", min_length=3)
    auctions: list[Auction] = Field(description="The auctions to insert")


@dataclass
class AuctionFilter:
    item_id: int | None = None
    item_name: str | None = None
    item_quality: int | None = None
    item_level: int | None = None
    item_class_index: int | None = None
    item_class_name: str | None = None


class AuctionFactory:
    @staticmethod
    def get(model: AuctionModel, item: Item) -> Auction:
        """Get the API model from a database model

        Args:
            model: The database model to convert to a API model
            item: The item for this auction

        Returns:
            The API model
        """
        return Auction(
            item=item,
            unit_buyout_price=model.auction_unit_buyout_price,
            unit_starting_bid_price=model.auction_unit_starting_bid_price,
            quantity=model.auction_quantity,
        )

    @staticmethod
    def get_db_model(view: Auction, server_realm_id: int) -> AuctionModel:
        """Get a database model from a API model

        Args:
            view: The API model to convert to a database model
            server_realm_id: The server realm ID

        Returns:
            The database model
        """
        return AuctionModel(
            server_realm_id=server_realm_id,
            item_id=view.item.id,
            auction_unit_buyout_price=view.unit_buyout_price,
            auction_unit_starting_bid_price=view.unit_starting_bid_price,
            auction_quantity=view.quantity,
        )
