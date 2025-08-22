from sqlalchemy import func, select

from lotkeeper.infra.db import DB
from lotkeeper.models.server_realm import ServerRealmModel


class ServerRealmService:
    def __init__(self, db: DB):
        self.db = db

    async def get_server_realm_id(
        self,
        server: str,
        realm: str,
    ) -> int | None:
        """Get the realm ID for a given server and realm.

        Args:
            server: The server of the realm
            realm: The realm of the realm

        Returns:
            The ID of the realm
        """

        # handle the slug scenario - convert dashes to spaces for database lookup
        normalized_realm = realm.replace("-", " ")
        normalized_server = server.replace("-", " ")

        async with self.db.get_session() as session:
            # Use case-insensitive exact match to handle different cases
            statement = select(ServerRealmModel.id).where(
                func.lower(ServerRealmModel.server) == func.lower(normalized_server),
                func.lower(ServerRealmModel.realm) == func.lower(normalized_realm),
            )

            result = await session.execute(statement)
            return result.scalar_one_or_none()

    async def get_server_realms(self) -> list[ServerRealmModel]:
        """Get all realms

        Returns:
            A list of server realms
        """

        async with self.db.get_session() as session:
            statement = select(ServerRealmModel)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def get_server_realm_by_slugs(self, server_slug: str, realm_slug: str) -> ServerRealmModel | None:
        """Get a server realm by slugs

        Args:
            server_slug: The slug of the server
            realm_slug: The slug of the realm

        Returns:
            The server realm
        """
        # handle the slug scenario - convert dashes to spaces for database lookup
        normalized_server = server_slug.replace("-", " ")
        normalized_realm = realm_slug.replace("-", " ")

        async with self.db.get_session() as session:
            statement = select(ServerRealmModel).where(
                func.lower(ServerRealmModel.server) == func.lower(normalized_server),
                func.lower(ServerRealmModel.realm) == func.lower(normalized_realm),
            )

            result = await session.execute(statement)
            return result.scalar_one_or_none()

    async def create_server_realm(self, server: str, realm: str) -> ServerRealmModel:
        """Create a server realm

        Args:
            server: The server of the realm
            realm: The realm of the realm

        Returns:
            The created server realm
        """

        async with self.db.get_session() as session:
            async with session.begin():
                realm_model = ServerRealmModel(server=server, realm=realm)
                session.add(realm_model)
            return realm_model
