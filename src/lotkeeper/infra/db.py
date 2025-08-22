import os
import subprocess
import sys
from pathlib import Path

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine

from lotkeeper.common.logging import propagate_logs
from lotkeeper.config import ENV
from lotkeeper.models.base.db_model import DbModel
from lotkeeper.models.base.timescale_db_model import TimescaleDbModel


class DB:
    """Database connection and session management singleton."""

    def __init__(self, database_url: str = ENV.get_database_url()):
        self.engine = create_async_engine(database_url, echo=ENV.LOT_DB_ECHO, future=True)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        propagate_logs()  # Propagate stdlib logs to loguru

    async def connect(self) -> None:
        """Connect to the database and initialize it."""
        logger.info("Connecting to database...")

        # Try to acquire migration lock - only one worker should run migrations
        migration_lock_acquired = await self._try_acquire_migration_lock()

        if migration_lock_acquired:
            logger.info("Migration lock acquired - running migrations")
            await self._run_migrations_sync()

            # Create hypertables in the same worker that ran migrations
            async with self.engine.begin() as conn:
                logger.info("Creating hypertables if needed")
                await self._create_hypertables(conn)
                logger.info("Database has been set up and is ready to use")
        else:
            logger.warning("Migration lock not acquired - skipping migrations (another worker is handling them)")

            # Still connect but don't create hypertables
            async with self.engine.begin() as conn:
                logger.info("Connected, database setup handled by another worker")

    async def _run_migrations_sync(self) -> None:
        """Run database migrations using Alembic (sync)."""
        try:
            logger.info("Running database migrations...")

            sync_url = ENV.get_database_url_sync()
            current_file = Path(__file__)
            migrations_dir = current_file.parent.parent

            # Set environment variable for Alembic to use
            env = os.environ.copy()
            env["DB_URL"] = sync_url

            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                check=False,
                cwd=migrations_dir,
                capture_output=True,
                text=True,
                env=env,
            )

            if result.returncode == 0:
                logger.info("Migrations completed successfully")
                if result.stdout:
                    logger.info(f"Migration output: {result.stdout}")
            else:
                logger.error(f"Migration failed with return code: {result.returncode}")
                logger.error(f"Migration stdout: {result.stdout}")
                logger.error(f"Migration stderr: {result.stderr}")

                if ENV.is_prod():
                    raise Exception(f"Migration failed in production: {result.stderr}")
                else:
                    logger.warning("Migration failed, continuing in development mode")

        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            if ENV.is_prod():
                raise e

    async def _create_tables(self, conn: AsyncConnection) -> None:
        await conn.run_sync(DbModel.metadata.create_all)

    async def _create_hypertables(self, conn: AsyncConnection) -> None:
        models = TimescaleDbModel.__subclasses__()

        for clazz in models:
            await clazz.create_hypertable(conn)

    async def _clean_database(self, conn: AsyncConnection) -> None:
        """
        Clean the database by dropping all tables in dependency order.
        """

        logger.info("Cleaning database...")

        # Drop all tables with CASCADE to handle foreign key dependencies
        drop_all_statement = text("""
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                -- Drop all tables in the public schema
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;

                -- Drop all sequences
                FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
                    EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
                END LOOP;
            END $$;
        """)

        await conn.execute(drop_all_statement)
        logger.info("Database cleaned successfully")

    async def _try_acquire_migration_lock(self) -> bool:
        """Try to acquire a migration lock using PostgreSQL advisory lock."""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT pg_try_advisory_lock(12345)"))
                lock_acquired = result.scalar()
                return bool(lock_acquired)
        except Exception as e:
            logger.warning(f"Failed to acquire migration lock: {e}")
            return False

    def get_session(self) -> AsyncSession:
        """Get a async database session"""

        return self.async_session()
