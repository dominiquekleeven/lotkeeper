from loguru import logger
from sqlalchemy import case, delete, func, select
from sqlalchemy.sql import Select

from lotkeeper.infra.db import DB
from lotkeeper.models.auction import Auction, AuctionData, AuctionFactory, AuctionFilter, AuctionModel
from lotkeeper.models.item import Item, ItemFactory, ItemModel
from lotkeeper.models.types import PaginatedResponse, PaginationFilter, PaginationInfo
from lotkeeper.services.datapoint_service import DatapointService


class AuctionService:
    def __init__(self, db: DB, datapoint_service: DatapointService):
        self.db = db
        self.datapoint_service = datapoint_service

    def _get_joined_auction_query(self, server_realm_id: int) -> Select[tuple[AuctionModel, ItemModel]]:
        """Get the base query that always joins auctions with item metadata.

        Args:
            server_realm_id: The ID of the server realm to get the auctions for

        Returns:
            A query that always joins auctions with item metadata
        """

        return (
            select(AuctionModel, ItemModel)
            .join(
                ItemModel,
                (AuctionModel.item_id == ItemModel.id) & (AuctionModel.server_realm_id == ItemModel.server_realm_id),
            )
            .where(AuctionModel.server_realm_id == server_realm_id)
        )

    def _get_joined_count_query(self, server_realm_id: int) -> Select[tuple[int]]:
        """Get a count query for auctions in a server realm.

        Args:
            server_realm_id: The ID of the server realm to get the count for

        Returns:
            A count of auctions
        """

        return (
            select(func.count(AuctionModel.id))
            .join(
                ItemModel,
                (AuctionModel.item_id == ItemModel.id) & (AuctionModel.server_realm_id == ItemModel.server_realm_id),
            )
            .where(AuctionModel.server_realm_id == server_realm_id)
        )

    async def get_auctions(self, server_realm_id: int) -> list[Auction]:
        """Get all auctions for a given realm

        Args:
            server_realm_id: The ID of the server realm to get the auctions for

        Returns:
            A list of auctions
        """
        async with self.db.get_session() as session:
            statement = self._get_joined_auction_query(server_realm_id)
            result = await session.execute(statement)
            auctions_with_metadata = list(result.all())

            # Convert database models to API models
            mapped_auctions = [
                AuctionFactory.get(auction, ItemFactory.get(item)) for auction, item in auctions_with_metadata
            ]
            return mapped_auctions

    async def get_auctions_paginated(
        self, server_realm_id: int, pagination: PaginationFilter, filter: AuctionFilter | None = None
    ) -> PaginatedResponse[Auction]:
        """Get all auctions for a given realm with pagination and filtering.

        Args:
            server_realm_id: The ID of the server realm to get the auctions for
            pagination: The pagination to apply to the auctions
            filter: The filter to apply to the auctions, optional

        Returns:
            A paginated response of auctions
        """
        async with self.db.get_session() as session:
            base_query = self._get_joined_auction_query(server_realm_id)
            count_query = self._get_joined_count_query(server_realm_id)

            if filter:
                if filter.item_id:
                    base_query = base_query.where(AuctionModel.item_id == filter.item_id)
                    count_query = count_query.where(AuctionModel.item_id == filter.item_id)

                if filter.item_name:
                    base_query = base_query.where(ItemModel.name.ilike(f"%{filter.item_name}%"))
                    count_query = count_query.where(ItemModel.name.ilike(f"%{filter.item_name}%"))

                if filter.item_quality:
                    base_query = base_query.where(ItemModel.quality == filter.item_quality)
                    count_query = count_query.where(ItemModel.quality == filter.item_quality)

                if filter.item_level:
                    base_query = base_query.where(ItemModel.level == filter.item_level)
                    count_query = count_query.where(ItemModel.level == filter.item_level)

                if filter.item_class_index:
                    base_query = base_query.where(ItemModel.class_index == filter.item_class_index)
                    count_query = count_query.where(ItemModel.class_index == filter.item_class_index)

                if filter.item_class_name:
                    base_query = base_query.where(ItemModel.class_name.ilike(f"%{filter.item_class_name}%"))
                    count_query = count_query.where(ItemModel.class_name.ilike(f"%{filter.item_class_name}%"))

            # Apply pagination only to data query
            if pagination:
                if pagination.limit:
                    base_query = base_query.limit(pagination.limit)

                if pagination.offset:
                    base_query = base_query.offset(pagination.offset)

            # Add ordering priority for name filter
            if filter and filter.item_name:
                base_query = base_query.add_columns(
                    case(
                        (ItemModel.name.ilike(filter.item_name), 0),  # Exact match = highest priority
                        (ItemModel.name.ilike(f"{filter.item_name}%"), 1),  # Starts with = medium priority
                        (ItemModel.name.ilike(f"%{filter.item_name}%"), 2),  # Contains = lowest priority
                        else_=3,  # No match
                    ).label("match_priority")
                ).order_by("match_priority", ItemModel.name)
            else:
                # else use default ordering by item name
                base_query = base_query.order_by(ItemModel.name)

            # execute the data and count queries
            data_result = await session.execute(base_query)
            count_result = await session.execute(count_query)

            if filter and filter.item_name:
                auctions_with_metadata = [row[:2] for row in data_result]  # Skip the match_priority column
            else:
                auctions_with_metadata = list(data_result.all())

            total_count = count_result.scalar_one()
            pagination_info = PaginationInfo(limit=pagination.limit, offset=pagination.offset, total=total_count)

            # Create the auction models and construct the paginated response
            mapped_auctions = [
                AuctionFactory.get(auction, ItemFactory.get(item)) for auction, item in auctions_with_metadata
            ]
            return PaginatedResponse(data=mapped_auctions, pagination=pagination_info)

    async def get_auctions_count(self, server_realm_id: int) -> int:
        """Get the number of active auctions for a given realm

        Args:
            server_realm_id: The ID of the server realm to get the number of auctions for

        Returns:
            The number of active auctions
        """

        async with self.db.get_session() as session:
            statement = select(func.count()).where(AuctionModel.server_realm_id == server_realm_id)
            result = await session.execute(statement)
            return result.scalar_one()

    async def get_total_value(self, server_realm_id: int) -> int:
        """Get the total value of all active auctions for a given realm

        Args:
            server_realm_id: The ID of the server realm to get the total value for

        Returns:
            The total value of all active auctions
        """

        async with self.db.get_session() as session:
            statement = select(
                func.sum(AuctionModel.auction_unit_buyout_price * AuctionModel.auction_quantity),
            ).where(
                AuctionModel.server_realm_id == server_realm_id,
                AuctionModel.auction_unit_buyout_price > 0,
                AuctionModel.auction_quantity > 0,
            )
            result = await session.execute(statement)
            return result.scalar_one_or_none() or 0

    async def get_auctions_below_vendor_price(self, server_realm_id: int) -> list[Auction]:
        """Get auctions where the buyout price is below the vendor price

        Args:
            server_realm_id: The ID of the server realm to get the auctions for

        Returns:
            A list of auctions below vendor price
        """
        async with self.db.get_session() as session:
            base_query = self._get_joined_auction_query(server_realm_id)

            # Add the vendor price filter - buyout must be less than vendor price
            base_query = base_query.where(
                AuctionModel.auction_unit_buyout_price < ItemModel.vendor_price,
                AuctionModel.auction_unit_buyout_price > 0,  # Exclude auctions with 0 buyout
                ItemModel.vendor_price > 0,  # Exclude items with 0 vendor price
            )

            # Order by savings (vendor_price - buyout_price) descending, then by item name
            base_query = base_query.order_by(
                (ItemModel.vendor_price - AuctionModel.auction_unit_buyout_price).desc(), ItemModel.name
            )

            # Execute the query
            data_result = await session.execute(base_query)
            auctions_with_metadata = list(data_result.all())

            # Create the auction models
            mapped_auctions = [
                AuctionFactory.get(auction, ItemFactory.get(item)) for auction, item in auctions_with_metadata
            ]
            return mapped_auctions

    async def truncate_and_insert_auctions(self, server_realm_id: int, data: AuctionData) -> None:
        """Delete all auctions for a realm and insert new active auctions

        Args:
            server_realm_id: The ID of the server realm to insert the auctions for
            data: The auctions to insert

        Returns:
            None
        """

        logger.info(f"Truncating and inserting auctions for server realm {server_realm_id}")

        # Extract unique items and convert to database models
        item_list = list({auction.item.id: auction.item for auction in data.auctions}.values())
        item_models = [ItemFactory.get_db_model(item, server_realm_id) for item in item_list]

        # Convert auctions to database models
        auctions = [AuctionFactory.get_db_model(auction, server_realm_id) for auction in data.auctions]
        auction_datapoints = self.datapoint_service.construct_auction_datapoints(auctions)

        async with self.db.get_session() as session:
            async with session.begin():
                # 1. Delete all auctions for the given realm
                statement = delete(AuctionModel).where(AuctionModel.server_realm_id == server_realm_id)
                await session.execute(statement)

                # 2. Replace existing item metadata for the given realm (merge will insert new or update existing)
                for item_model in item_models:
                    await session.merge(item_model)
                await session.flush()  # Flush to ensure item metadata exists before inserting auctions

                # 4. Insert the new active auctions
                session.add_all(auctions)

                # 5. Insert the auction entries for historical auction data
                session.add_all(auction_datapoints)

        logger.info(f"Truncated and inserted auctions for server realm {server_realm_id}")

    async def get_top_50_items_by_auction_count(self, server_realm_id: int) -> list[Item]:
        """Get top 50 items with the most auctions (most popular items)

        Args:
            server_realm_id: The ID of the server realm to get the items for

        Returns:
            A list of top 50 items ordered by auction count descending
        """
        async with self.db.get_session() as session:
            # Count auctions for each item and order by auction count
            statement = (
                select(ItemModel, func.count(AuctionModel.id).label("auction_count"))
                .join(AuctionModel, AuctionModel.item_id == ItemModel.id)
                .where(AuctionModel.server_realm_id == server_realm_id, ItemModel.server_realm_id == server_realm_id)
                .group_by(ItemModel.id, ItemModel.server_realm_id)
                .order_by(func.count(AuctionModel.id).desc())
                .limit(50)
            )

            result = await session.execute(statement)
            items_with_counts = list(result.all())

            # Convert database models to API models
            mapped_items = [ItemFactory.get(item) for item, _ in items_with_counts]
            return mapped_items
