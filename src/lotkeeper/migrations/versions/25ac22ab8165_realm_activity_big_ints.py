"""realm activity big ints

Revision ID: 25ac22ab8165
Revises: 09368752d130
Create Date: 2025-09-02 10:27:32.642060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision = "25ac22ab8165"
down_revision = "09368752d130"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.drop_table("auction_realm_activity_datapoints")

    op.create_table(
        "auction_realm_activity_datapoints",
        sa.Column("server_realm_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("total_auctions", sa.Integer(), nullable=False),
        sa.Column("total_quantity", sa.BigInteger(), nullable=False),
        sa.Column("total_market_value", sa.BigInteger(), nullable=False),
        sa.Column("estimated_market_value", sa.BigInteger(), nullable=False),
        sa.Column("datapoint_count", sa.Integer(), nullable=False),
        sa.Column("outlier_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["server_realm_id"], ["server_realms.id"]),
        sa.PrimaryKeyConstraint("server_realm_id", "ts"),
        sa.Index("idx_r_realm_ts", "server_realm_id", sa.text("ts DESC")),
    )

def downgrade() -> None:
    op.drop_table("auction_realm_activity_datapoints")

