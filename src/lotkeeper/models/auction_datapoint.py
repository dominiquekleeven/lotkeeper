from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP, ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text as sa_text

from lotkeeper.models.base.timescale_db_model import TimescaleDbModel


class AuctionDatapointModel(TimescaleDbModel):
    __tablename__ = "auction_datapoints"
    __table_args__ = (
        ForeignKeyConstraint(["server_realm_id"], ["server_realms.id"]),
        # Composite index item market activity
        Index(
            "idx_a_item_server_realm_ts",
            "item_id",
            "server_realm_id",
            sa_text("timestamp DESC"),
        ),
        # Composite index realm market activity
        Index(
            "idx_adp_realm_time_cover_price",
            "server_realm_id",
            "timestamp",
            postgresql_include=("buyout_price", "quantity"),
            postgresql_where=sa_text("buyout_price > 0"),
        ),
    )

    # Timescale hypertable config
    __time_column_name__ = "timestamp"
    __chunk_time_interval__ = "1 day"
    __compression_after__ = "14 days"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)

    server_realm_id: Mapped[int] = mapped_column()
    item_id: Mapped[int] = mapped_column()

    buyout_price: Mapped[int] = mapped_column()
    starting_bid_price: Mapped[int] = mapped_column()  # stored but not used
    count: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column()


class AuctionItemPriceHourlySummary(BaseModel):
    model_config = {"json_schema_extra": {"description": "A hourly summary of the buyout price of an item in copper"}}

    timestamp: datetime = Field(description="The timestamp of the buyout price summary (UTC)", ge=datetime.min)
    min_buyout_price: int = Field(description="The minimum buyout price of the item in copper", ge=0)
    max_buyout_price: int = Field(description="The maximum buyout price of the item in copper", ge=0)
    median_buyout_price: int = Field(description="The median buyout price of the item in copper", ge=0)
    avg_buyout_price: int = Field(description="The average buyout price of the item in copper", ge=0)
    p25_buyout_price: int = Field(description="The 25th percentile buyout price of the item in copper", ge=0)
    p75_buyout_price: int = Field(description="The 75th percentile buyout price of the item in copper", ge=0)
    p10_buyout_price: int = Field(description="The 10th percentile buyout price of the item in copper", ge=0)
    p90_buyout_price: int = Field(description="The 90th percentile buyout price of the item in copper", ge=0)
    outlier_count: int = Field(description="The number of datapoints that are outliers", ge=0)
    datapoint_count: int = Field(description="The number of datapoints for the hour", ge=0)


class AuctionItemActivityHourlySummary(BaseModel):
    model_config = {"json_schema_extra": {"description": "A hourly summary of the market buyout activity of an item"}}

    timestamp: datetime = Field(
        description="The timestamp of the market buyout activity summary (UTC)", gt=datetime.min
    )
    total_auctions: int = Field(description="The total number of buyout auctions for the item", ge=0)
    total_quantity: int = Field(description="The total quantity of the item available via buyout auctions", ge=0)
    total_market_value: int = Field(
        description="The total market buyout value of all auctions in copper (includes outliers)", ge=0
    )
    estimated_market_value: int = Field(
        description="The estimated market buyout value using median buyout price times total quantity", ge=0
    )
    datapoint_count: int = Field(description="The number of datapoints for the hour", ge=0)
    outlier_count: int = Field(description="The number of datapoints that are outliers", ge=0)


class AuctionDatapointFactory:
    @staticmethod
    def get_price_hourly_summary(
        timestamp: datetime,
        min_buyout: int,
        max_buyout: int,
        median_buyout: int,
        avg_buyout: int,
        p25_buyout: int,
        p75_buyout: int,
        p10_buyout: int,
        p90_buyout: int,
        datapoint_count: int,
        outlier_count: int,
    ) -> AuctionItemPriceHourlySummary:
        """Get a datapoint containing hourly price summary data

        Args:
            timestamp: The timestamp of the buyout price summary (UTC)
            min_buyout: The minimum buyout price in copper
            max_buyout: The maximum buyout price in copper
            median_buyout: The median buyout price in copper
            q25_buyout: The 25th percentile buyout price in copper
            q75_buyout: The 75th percentile buyout price in copper
            datapoint_count: The number of datapoints for the hour

        Returns:
            The hourly price summary view model
        """
        return AuctionItemPriceHourlySummary(
            timestamp=timestamp,
            min_buyout_price=min_buyout,
            max_buyout_price=max_buyout,
            median_buyout_price=median_buyout,
            avg_buyout_price=avg_buyout,
            p25_buyout_price=p25_buyout,
            p75_buyout_price=p75_buyout,
            p10_buyout_price=p10_buyout,
            p90_buyout_price=p90_buyout,
            outlier_count=outlier_count,
            datapoint_count=datapoint_count,
        )

    @staticmethod
    def get_market_activity_hourly_summary(
        timestamp: datetime,
        total_auctions: int,
        total_quantity: int,
        total_market_value: int,
        estimated_market_value: int,
        datapoint_count: int,
        outlier_count: int,
    ) -> AuctionItemActivityHourlySummary:
        """Get a datapoint containing hourly market buyout activity summary data

        Args:
            timestamp: The timestamp of the market buyout activity summary (UTC)
            total_auctions: The total number of buyout auctions
            total_quantity: The total quantity available via buyout auctions
            total_market_value: The total market buyout value in copper (includes outliers)
            estimated_market_value: The estimated market buyout value using median buyout price times total quantity
            datapoint_count: The number of datapoints for the hour
            outlier_count: The number of datapoints that are outliers

        Returns:
            The hourly market buyout activity summary view model
        """
        return AuctionItemActivityHourlySummary(
            timestamp=timestamp,
            total_auctions=total_auctions,
            total_quantity=total_quantity,
            total_market_value=total_market_value,
            estimated_market_value=estimated_market_value,
            datapoint_count=datapoint_count,
            outlier_count=outlier_count,
        )
