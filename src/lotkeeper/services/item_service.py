from sqlalchemy import case, func, select
from sqlalchemy.sql import Select

from lotkeeper.infra.db import DB
from lotkeeper.models.item import Item, ItemFactory, ItemFilter, ItemModel
from lotkeeper.models.types import PaginatedResponse, PaginationFilter, PaginationInfo


class ItemService:
    def __init__(self, db: DB):
        self.db = db

    def _get_base_item_query(self, server_realm_id: int) -> Select[tuple[ItemModel]]:
        """Get the base query for items in a server realm.

        Args:
            server_realm_id: The ID of the server realm to get the items for

        Returns:
            A query for items in a server realm
        """

        return select(ItemModel).where(ItemModel.server_realm_id == server_realm_id)

    def _get_count_query(self, server_realm_id: int) -> Select[tuple[int]]:
        """Get a count query for items in a server realm.

        Args:
            server_realm_id: The ID of the server realm to get the count for

        Returns:
            A count of items
        """

        return select(func.count(ItemModel.id)).where(ItemModel.server_realm_id == server_realm_id)

    async def get_items(self, server_realm_id: int) -> list[Item]:
        """Get all items for a given realm

        Args:
            server_realm_id: The ID of the server realm to get the items for

        Returns:
            A list of items
        """
        async with self.db.get_session() as session:
            statement = self._get_base_item_query(server_realm_id)
            result = await session.execute(statement)
            items = list(result.scalars().all())

            # Convert database models to API models
            mapped_items = [ItemFactory.get(item) for item in items]
            return mapped_items

    async def get_items_paginated(
        self, server_realm_id: int, pagination: PaginationFilter, filter: ItemFilter | None = None
    ) -> PaginatedResponse[Item]:
        """Get all items for a given realm with pagination and filtering.

        Args:
            server_realm_id: The ID of the server realm to get the items for
            pagination: The pagination to apply to the items
            filter: The filter to apply to the items, optional

        Returns:
            A paginated response of items
        """
        async with self.db.get_session() as session:
            base_query = self._get_base_item_query(server_realm_id)
            count_query = self._get_count_query(server_realm_id)

            if filter:
                if filter.id:
                    base_query = base_query.where(ItemModel.id == filter.id)
                    count_query = count_query.where(ItemModel.id == filter.id)

                if filter.name:
                    base_query = base_query.where(ItemModel.name.ilike(f"%{filter.name}%"))
                    count_query = count_query.where(ItemModel.name.ilike(f"%{filter.name}%"))

                if filter.quality:
                    base_query = base_query.where(ItemModel.quality == filter.quality)
                    count_query = count_query.where(ItemModel.quality == filter.quality)

                if filter.level:
                    base_query = base_query.where(ItemModel.level == filter.level)
                    count_query = count_query.where(ItemModel.level == filter.level)

                if filter.class_index:
                    base_query = base_query.where(ItemModel.class_index == filter.class_index)
                    count_query = count_query.where(ItemModel.class_index == filter.class_index)

                if filter.class_name:
                    base_query = base_query.where(ItemModel.class_name.ilike(f"%{filter.class_name}%"))
                    count_query = count_query.where(ItemModel.class_name.ilike(f"%{filter.class_name}%"))

            # Apply pagination only to data query
            if pagination:
                if pagination.limit:
                    base_query = base_query.limit(pagination.limit)

                if pagination.offset:
                    base_query = base_query.offset(pagination.offset)

            # Add ordering priority for name filter
            if filter and filter.name:
                base_query = base_query.add_columns(
                    case(
                        (ItemModel.name.ilike(filter.name), 0),  # Exact match = highest priority
                        (ItemModel.name.ilike(f"{filter.name}%"), 1),  # Starts with = medium priority
                        (ItemModel.name.ilike(f"%{filter.name}%"), 2),  # Contains = lowest priority
                        else_=3,  # No match
                    ).label("match_priority")
                ).order_by("match_priority", ItemModel.name)
            else:
                # else use default ordering by item name
                base_query = base_query.order_by(ItemModel.name)

            # execute the data and count queries
            data_result = await session.execute(base_query)
            count_result = await session.execute(count_query)

            if filter and filter.name:
                items = [row[0] for row in data_result]  # Get the ItemModel from the first column
            else:
                items = list(data_result.scalars().all())

            total_count = count_result.scalar_one()
            pagination_info = PaginationInfo(limit=pagination.limit, offset=pagination.offset, total=total_count)

            # Create the item models and construct the paginated response
            mapped_items = [ItemFactory.get(item) for item in items]
            return PaginatedResponse(data=mapped_items, pagination=pagination_info)

    async def get_item_count(self, server_realm_id: int) -> int:
        """Get the count of items for a given realm

        Args:
            server_realm_id: The ID of the server realm to get the count for

        Returns:
            The count of items
        """
        async with self.db.get_session() as session:
            statement = self._get_count_query(server_realm_id)
            result = await session.execute(statement)
            return result.scalar_one()
