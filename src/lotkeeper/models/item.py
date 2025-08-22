from dataclasses import dataclass

from pydantic import BaseModel, Field
from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from lotkeeper.models.base.db_model import DbModel


class ItemModel(DbModel):
    __tablename__ = "items"
    __table_args__ = (
        PrimaryKeyConstraint("id", "server_realm_id"),
        Index("ix_items_server_realm", "server_realm_id"),
        ForeignKeyConstraint(["server_realm_id"], ["server_realms.id"]),
    )

    id: Mapped[int] = mapped_column(index=True)  # The item ID
    server_realm_id: Mapped[int] = mapped_column(index=True)  # For which server-realm this item is available
    name: Mapped[str]
    link: Mapped[str]
    icon: Mapped[str]
    level: Mapped[int]
    quality: Mapped[int] = mapped_column(index=True)
    max_stack_size: Mapped[int]
    vendor_price: Mapped[int]
    class_index: Mapped[int]
    class_name: Mapped[str]


class Item(BaseModel):
    model_config = {"json_schema_extra": {"description": "Details for an item in a specific server-realm"}}

    id: int = Field(description="The ID of the item", gt=0)
    name: str = Field(description="The name of the item", min_length=1)
    link: str = Field(description="The link of the item", min_length=0)
    icon: str = Field(description="The icon of the item", min_length=0)
    level: int = Field(description="The level of the item", ge=0)
    quality: int = Field(description="The quality of the item", ge=0)
    max_stack_size: int = Field(description="The maximum stack size of the item", ge=0)
    vendor_price: int = Field(description="The vendor price of the item", ge=0)
    class_index: int = Field(description="The index of the class of the item", ge=0)
    class_name: str = Field(description="The name of the class of the item", min_length=1)


@dataclass
class ItemFilter:
    id: int | None = None
    name: str | None = None
    quality: int | None = None
    level: int | None = None
    class_index: int | None = None
    class_name: str | None = None


class ItemFactory:
    @staticmethod
    def get(model: ItemModel) -> Item:
        """Get the API model from a database model

        Args:
            model: The database model to convert to a API model

        Returns:
            The API model
        """
        return Item(
            id=model.id,
            name=model.name,
            link=model.link,
            icon=model.icon,
            level=model.level,
            quality=model.quality,
            max_stack_size=model.max_stack_size,
            vendor_price=model.vendor_price,
            class_index=model.class_index,
            class_name=model.class_name,
        )

    @staticmethod
    def get_db_model(view: Item, server_realm_id: int) -> ItemModel:
        """Get a database model from a API model

        Args:
            view: The API model to convert to a database model
            server_realm_id: The server realm ID

        Returns:
            The database model
        """
        return ItemModel(
            server_realm_id=server_realm_id,
            id=view.id,
            name=view.name,
            link=view.name,
            icon=view.icon,
            level=view.level,
            quality=view.quality,
            max_stack_size=view.max_stack_size,
            vendor_price=view.vendor_price,
            class_index=view.class_index,
            class_name=view.class_name,
        )
