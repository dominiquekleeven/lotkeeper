from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from lotkeeper.models.base.db_model import DbModel


class ServerRealmModel(DbModel):
    __tablename__ = "server_realms"
    __table_args__ = (
        Index("ix_server_realms_server_realm", "server", "realm"),
        UniqueConstraint("server", "realm", name="uq_server_realms_server_realm"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    server: Mapped[str] = mapped_column(index=True)
    realm: Mapped[str] = mapped_column(index=True)


class Realm(BaseModel):
    model_config = {"json_schema_extra": {"description": "A realm on a server"}}
    realm: str = Field(description="The name of the realm", min_length=3)
    realm_slug: str | None = Field(
        default=None, description="The normalized realm name (lowercase with hyphens instead of spaces)", min_length=3
    )

    def model_post_init(self, __context: Any) -> None:
        """Generate realm_slug from realm name after model initialization"""
        self.realm_slug = self.realm.replace(" ", "-").lower()


class ServerRealm(BaseModel):
    model_config = {"json_schema_extra": {"description": "A server and its realms"}}
    server: str = Field(description="The name of the server", min_length=3)
    server_slug: str | None = Field(
        default=None, description="The normalized server name (lowercase with hyphens instead of spaces)", min_length=3
    )
    realms: list[Realm] = Field(description="The realms on the server")

    def model_post_init(self, __context: Any) -> None:
        """Generate server_slug from server name after model initialization"""
        self.server_slug = self.server.replace(" ", "-").lower()


class ServerRealmFactory:
    @staticmethod
    def get_server_realms(server_realms: list[ServerRealmModel]) -> list[ServerRealm]:
        """Get the Server API models from a list of database models containing multiple realms

        Args:
            server_realms: The database models to convert to a Server Realm API models

        Returns:
            The Server Realm API models
        """

        distinct_servers = []

        # Get all unique servers
        for server_realm in server_realms:
            if server_realm.server not in distinct_servers:
                distinct_servers.append(server_realm.server)

        # Get all servers and add their realms to the server objects
        server_list = []
        for server_name in distinct_servers:
            server = ServerRealm(server=server_name, realms=[])
            # Add all realms for this server to the server object
            for server_realm in server_realms:
                if server_realm.server == server_name:
                    server.realms.append(Realm(realm=server_realm.realm))

            # Add the server object to the list
            server_list.append(server)

        return server_list

    @staticmethod
    def get(server_realm: ServerRealmModel) -> ServerRealm:
        """Get the Server API model from a database model only containing a singular realm

        Args:
            server_realm: The database model to convert to a Server Realm API model

        Returns:
            The Server Realm API model
        """
        return ServerRealm(server=server_realm.server, realms=[Realm(realm=server_realm.realm)])
