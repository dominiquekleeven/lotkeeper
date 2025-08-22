from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP, BigInteger, ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text as sa_text

from lotkeeper.models.base.timescale_db_model import TimescaleDbModel


class AuctionRealmActivityDatapointModel(TimescaleDbModel):
    __tablename__ = "auction_realm_activity_datapoints"
    __table_args__ = (
        ForeignKeyConstraint(["server_realm_id"], ["server_realms.id"]),
        Index("idx_r_realm_ts", "server_realm_id", sa_text("ts DESC")),
    )

    __time_column_name__ = "ts"
    __chunk_time_interval__ = "1 day"
    __compression_after__ = "14 days"

    server_realm_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    ts: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)

    # Aggregates
    total_auctions: Mapped[int] = mapped_column(nullable=False)
    total_quantity: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_market_value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    estimated_market_value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    datapoint_count: Mapped[int] = mapped_column(nullable=False)
    outlier_count: Mapped[int] = mapped_column(nullable=False)


class AuctionRealmActivityDatapoint(BaseModel):
    model_config = {
        "json_schema_extra": {
            "description": "A datapoint containing the activity of a realms auction house at that current UTC hour"
        }
    }

    ts: datetime = Field(description="The timestamp of the datapoint", ge=datetime.min)
    total_auctions: int = Field(description="The total number of auctions", ge=0)
    total_quantity: int = Field(description="The total quantity of auctions", ge=0)
    total_market_value: int = Field(description="The total market value of auctions", ge=0)
    estimated_market_value: int = Field(description="The estimated market value of auctions", ge=0)
    datapoint_count: int = Field(description="The number of datapoints", ge=0)
    outlier_count: int = Field(description="The number of outliers", ge=0)


class AuctionRealmActivityDatapointFactory:
    @staticmethod
    def get(model: AuctionRealmActivityDatapointModel) -> AuctionRealmActivityDatapoint:
        return AuctionRealmActivityDatapoint(
            ts=model.ts,
            total_auctions=model.total_auctions,
            total_quantity=model.total_quantity,
            total_market_value=model.total_market_value,
            estimated_market_value=model.estimated_market_value,
            datapoint_count=model.datapoint_count,
            outlier_count=model.outlier_count,
        )
