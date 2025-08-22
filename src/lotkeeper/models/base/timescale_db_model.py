from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from lotkeeper.models.base.db_model import DbModel


class TimescaleDbModel(DbModel):
    """Base class for TimescaleDB models with automatic hypertable, compression, and retention."""

    __abstract__ = True

    # Hypertable config
    __time_column_name__: str = "timestamp"
    __chunk_time_interval__: str = "1 day"

    # Compression policy (enabled by default)
    __compression_after__: str = "14 days"
    __enable_compression__: bool = True

    # Retention policy (auto purge) — enabled by default
    __enable_retention__: bool = True
    __retention_after__: str = "3 months"

    @classmethod
    async def create_hypertable(cls, conn: AsyncConnection) -> None:
        """
        Ensure hypertable exists and (optionally) set compression + retention policies.
        Idempotent: safe to call multiple times.
        """
        table_name = cls.__tablename__
        column_name = cls.__time_column_name__

        # 1) Create (or ensure) hypertable
        await conn.execute(
            text(f"""
            SELECT create_hypertable(
                '{table_name}',
                '{column_name}',
                if_not_exists => TRUE,
                chunk_time_interval => INTERVAL '{cls.__chunk_time_interval__}'
            );
        """)
        )

        # 2) Enable + policy: compression (optional)
        if cls.__enable_compression__:
            # Enable compression on the table (no-op if already set)
            await conn.execute(
                text(f"""
                ALTER TABLE {table_name} SET (
                    timescaledb.compress = true
                );
            """)
            )

            # Add compression policy (idempotent)
            await conn.execute(
                text(f"""
                SELECT add_compression_policy(
                    '{table_name}',
                    if_not_exists => TRUE,
                    compress_after => INTERVAL '{cls.__compression_after__}'
                );
            """)
            )

        # 3) Retention policy (auto-purge old chunks) — optional
        if cls.__enable_retention__:
            await conn.execute(
                text(f"""
                SELECT add_retention_policy(
                    '{table_name}',
                    INTERVAL '{cls.__retention_after__}',
                    if_not_exists => TRUE
                );
            """)
            )

    @classmethod
    async def drop_hypertable(cls, conn: AsyncConnection) -> None:
        """Drop the hypertable (table + chunks)."""
        table_name = cls.__tablename__
        await conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
