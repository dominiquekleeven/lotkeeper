import asyncio
import datetime
from typing import Any

from loguru import logger
from sqlalchemy import text

from lotkeeper.infra.db import DB
from lotkeeper.models.auction import AuctionModel
from lotkeeper.models.auction_datapoint import (
    AuctionDatapointFactory,
    AuctionDatapointModel,
    AuctionItemActivityHourlySummary,
    AuctionItemPriceHourlySummary,
)
from lotkeeper.models.auction_realm_activity_datapoint import (
    AuctionRealmActivityDatapoint,
    AuctionRealmActivityDatapointFactory,
    AuctionRealmActivityDatapointModel,
)


def _ensure_utc(dt: datetime.datetime) -> datetime.datetime:
    """Ensure datetime is tz-aware UTC; assume UTC if naive."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt.astimezone(datetime.UTC)


def _build_cache_key(method_name: str, *args: Any) -> str:
    """Build a cache key from method name and arguments."""
    # Convert datetime objects to ISO format strings
    formatted_args = []
    for arg in args:
        if isinstance(arg, datetime.datetime):
            formatted_args.append(arg.isoformat())
        else:
            formatted_args.append(str(arg))

    return f"{method_name}:{':'.join(formatted_args)}"


class DatapointService:
    def __init__(self, db: DB):
        self.db = db

    def construct_auction_datapoints(self, auctions: list[AuctionModel]) -> list[AuctionDatapointModel]:
        """Turn raw auctions into auction datapoints (unit prices etc).

        args:
            auctions: The list of auctions to construct datapoints from

        returns:
            A list of AuctionDatapointModel objects
        """
        now = datetime.datetime.now(datetime.UTC)
        return [
            AuctionDatapointModel(
                server_realm_id=a.server_realm_id,
                item_id=a.item_id,
                timestamp=now,
                buyout_price=a.auction_unit_buyout_price,
                starting_bid_price=a.auction_unit_starting_bid_price,
                count=1,
                quantity=a.auction_quantity,
            )
            for a in auctions
        ]

    async def upsert_auction_realm_activity_datapoints(self, server_realm_id: int, delay_seconds: int = 0) -> None:
        """
        Realm activity for the *current UTC hour*, with per-item outlier filtering.
        - ts is date_trunc('hour', now() at UTC) so at most one row per realm per hour.
        - estimated_market_value uses per-item MAD (fallback IQR).
        """

        if delay_seconds > 0:
            logger.info(
                f"Delayed upsert ({delay_seconds} seconds) of auction realm activity datapoints for server realm {server_realm_id}"
            )
            await asyncio.sleep(delay_seconds)

        logger.info(f"Upserting auction realm activity datapoints for server realm {server_realm_id}")
        mad_threshold = 10
        mad_k = 3.0
        iqr_k = 1.5

        table = AuctionRealmActivityDatapointModel.__tablename__
        auctions_table = AuctionModel.__tablename__

        query = f"""
        WITH ts_now AS (
            SELECT date_trunc('hour', timezone('UTC', now())) AS ts_hour
        ),
        src AS (
            SELECT
                a.item_id,
                a.auction_unit_buyout_price::numeric AS p,
                a.auction_quantity::bigint          AS q
            FROM {auctions_table} a
            WHERE a.server_realm_id = :server_realm_id
            AND a.auction_unit_buyout_price > 0
        ),
        have_src AS (
            SELECT CASE WHEN EXISTS (SELECT 1 FROM src) THEN 1 ELSE 0 END AS has_rows
        ),
        per_item_stats AS (
            SELECT
                item_id,
                COUNT(*)::bigint                                   AS n,
                COALESCE(SUM(q), 0)::bigint                        AS total_q,
                COALESCE(SUM(p * q), 0)::numeric                   AS total_mv,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY p)     AS med,
                percentile_cont(0.25) WITHIN GROUP (ORDER BY p)    AS q1,
                percentile_cont(0.75) WITHIN GROUP (ORDER BY p)    AS q3
            FROM src
            GROUP BY item_id
        ),
        per_item_mad AS (
            SELECT
                s.item_id,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY abs(s.p - st.med)) AS mad
            FROM src s
            JOIN per_item_stats st USING (item_id)
            GROUP BY s.item_id, st.med
        ),
        per_item_bounds AS (
            SELECT
                st.item_id, st.n, st.total_q, st.total_mv, st.med, st.q1, st.q3,
                m.mad,
                (1.4826 * m.mad) AS sigma_mad,
                (st.q3 - st.q1)  AS iqr,
                CASE
                    WHEN st.n < GREATEST(3, :mad_threshold) OR m.mad IS NULL OR m.mad = 0
                        THEN FALSE
                    ELSE TRUE
                END AS use_mad
            FROM per_item_stats st
            JOIN per_item_mad   m USING (item_id)
        ),
        labeled AS (
            SELECT
                s.item_id, s.p, s.q, b.use_mad, b.sigma_mad, b.iqr, b.med, b.q1, b.q3,
                NOT (
                    ((b.use_mad AND b.sigma_mad > 0) OR ((NOT b.use_mad) AND b.iqr > 0))
                    AND (
                        s.p < CASE WHEN b.use_mad THEN b.med - (:mad_k * b.sigma_mad)
                                ELSE b.q1 - (:iqr_k * b.iqr) END
                    OR s.p > CASE WHEN b.use_mad THEN b.med + (:mad_k * b.sigma_mad)
                                ELSE b.q3 + (:iqr_k * b.iqr) END
                    )
                ) AS is_inlier
            FROM src s
            JOIN per_item_bounds b USING (item_id)
        ),
        per_item_agg AS (
            SELECT
                item_id,
                COUNT(*)::bigint                                                 AS datapoint_count,
                SUM(CASE WHEN NOT is_inlier THEN 1 ELSE 0 END)::bigint          AS outlier_count,
                SUM(q)::bigint                                                  AS total_quantity,
                SUM(p * q)::numeric                                             AS total_market_value,
                SUM(CASE WHEN is_inlier THEN p * q ELSE 0 END)::numeric         AS estimated_market_value
            FROM labeled
            GROUP BY item_id
        ),
        realm_agg AS (
            SELECT
                SUM(datapoint_count)::bigint        AS total_auctions,
                SUM(total_quantity)::bigint         AS total_quantity,
                COALESCE(SUM(total_market_value), 0)::numeric      AS total_market_value,
                COALESCE(SUM(estimated_market_value), 0)::numeric  AS estimated_market_value,
                SUM(outlier_count)::bigint          AS outlier_count
            FROM per_item_agg
        )
        INSERT INTO {table} (
            server_realm_id,
            ts,
            total_auctions,
            total_quantity,
            total_market_value,
            estimated_market_value,
            datapoint_count,
            outlier_count
        )
        SELECT
            :server_realm_id,
            (SELECT ts_hour FROM ts_now),
            ra.total_auctions,
            ra.total_quantity,
            ra.total_market_value::bigint,
            ra.estimated_market_value::bigint,
            ra.total_auctions,         -- datapoint_count == number of auctions considered
            ra.outlier_count
        FROM realm_agg ra
        WHERE (SELECT has_rows FROM have_src) = 1
        ON CONFLICT (server_realm_id, ts)
        DO UPDATE SET
            total_auctions       = EXCLUDED.total_auctions,
            total_quantity       = EXCLUDED.total_quantity,
            total_market_value   = EXCLUDED.total_market_value,
            estimated_market_value = EXCLUDED.estimated_market_value,
            datapoint_count      = EXCLUDED.datapoint_count,
            outlier_count        = EXCLUDED.outlier_count
        ;
        """

        async with self.db.get_session() as session:
            async with session.begin():
                await session.execute(
                    text(query),
                    {
                        "server_realm_id": server_realm_id,
                        "mad_threshold": mad_threshold,
                        "mad_k": mad_k,
                        "iqr_k": iqr_k,
                    },
                )

        logger.info(f"Done, upserted auction realm activity datapoints for server realm {server_realm_id}")

    async def get_auction_realm_activity_datapoints(
        self,
        server_realm_id: int,
        from_timestamp: datetime.datetime,
        to_timestamp: datetime.datetime,
    ) -> list[AuctionRealmActivityDatapoint]:
        """Get hourly auction realm activity datapoints (bucketed to 1h).
        args:
            server_realm_id: The server and realm ID
            from_timestamp: Start timestamp (UTC, timezone-aware or naive assumed UTC)
            to_timestamp: End timestamp (UTC, timezone-aware or naive assumed UTC; exclusive)

        returns:
            A list of AuctionRealmActivityDatapoint objects
        """
        from_ts = _ensure_utc(from_timestamp)
        to_ts = _ensure_utc(to_timestamp)

        query = """
        SELECT
            server_realm_id,
            time_bucket('1 hour', ts) AS bucket,
            SUM(total_auctions)        AS total_auctions,
            SUM(total_quantity)        AS total_quantity,
            SUM(total_market_value)    AS total_market_value,
            SUM(estimated_market_value) AS estimated_market_value,
            SUM(datapoint_count)       AS datapoint_count,
            SUM(outlier_count)         AS outlier_count
        FROM auction_realm_activity_datapoints
        WHERE server_realm_id = :server_realm_id
        AND ts >= :from_ts
        AND ts <  :to_ts
        GROUP BY server_realm_id, bucket
        ORDER BY bucket;
        """

        async with self.db.get_session() as session:
            result = await session.execute(
                text(query),
                {"server_realm_id": server_realm_id, "from_ts": from_ts, "to_ts": to_ts},
            )
            rows = result.all()

        return [
            AuctionRealmActivityDatapointFactory.get(
                AuctionRealmActivityDatapointModel(
                    server_realm_id=row.server_realm_id,
                    ts=row.bucket,
                    total_auctions=row.total_auctions,
                    total_quantity=row.total_quantity,
                    total_market_value=row.total_market_value,
                    estimated_market_value=row.estimated_market_value,
                    datapoint_count=row.datapoint_count,
                    outlier_count=row.outlier_count,
                )
            )
            for row in rows
        ]

    async def get_auction_item_price_hourly_summary(
        self,
        item_id: int,
        server_realm_id: int,
        from_timestamp: datetime.datetime,
        to_timestamp: datetime.datetime,
    ) -> list[AuctionItemPriceHourlySummary]:
        """
        Hourly price summary computed from filtered unit prices.
        Filtering: prefer MAD; if bucket n < threshold or MAD==0 -> fallback to IQR.
        """
        from_ts = _ensure_utc(from_timestamp)
        to_ts = _ensure_utc(to_timestamp)

        mad_threshold = 10
        mad_k = 3.0
        iqr_k = 1.5

        async with self.db.get_session() as session:
            query = f"""
            WITH base AS (
                SELECT
                    time_bucket('1 hour', p.timestamp) AS bucket,
                    p.buyout_price::numeric AS price,
                    p.quantity::numeric AS qty
                FROM {AuctionDatapointModel.__tablename__} p
                WHERE p.item_id = :item_id
                AND p.server_realm_id = :server_realm_id
                AND p.timestamp >= :from_ts
                AND p.timestamp < :to_ts
                AND p.buyout_price > 0
            ),
            base_counts AS (
                SELECT bucket, COUNT(*) AS n
                FROM base
                GROUP BY bucket
            ),
            med AS (
                SELECT bucket,
                    percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS med
                FROM base
                GROUP BY bucket
            ),
            dev AS (
                SELECT b.bucket, b.price, b.qty, m.med,
                    abs(b.price - m.med) AS abs_dev
                FROM base b
                JOIN med m USING (bucket)
            ),
            mad AS (
                SELECT bucket,
                    percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
                FROM dev
                GROUP BY bucket
            ),
            iqr AS (
                SELECT bucket,
                    percentile_cont(0.25) WITHIN GROUP (ORDER BY price) AS q1,
                    percentile_cont(0.75) WITHIN GROUP (ORDER BY price) AS q3
                FROM base
                GROUP BY bucket
            ),
            bounds AS (
                SELECT
                    bc.bucket,
                    bc.n,
                    m.med,
                    i.q1, i.q3,
                    a.mad,
                    (1.4826 * a.mad) AS sigma_mad,
                    (i.q3 - i.q1) AS iqr,
                    CASE
                        WHEN bc.n < GREATEST(3, :mad_threshold) OR a.mad IS NULL OR a.mad = 0
                            THEN FALSE
                        ELSE TRUE
                    END AS use_mad
                FROM base_counts bc
                JOIN med m USING (bucket)
                JOIN iqr i USING (bucket)
                JOIN mad a USING (bucket)
            ),
            cutoffs AS (
                SELECT
                    b.bucket, b.n, b.med, b.q1, b.q3, b.mad, b.sigma_mad, b.iqr, b.use_mad,
                    CASE
                        WHEN b.use_mad AND b.sigma_mad > 0 THEN b.med - (:mad_k * b.sigma_mad)
                        WHEN NOT b.use_mad AND b.iqr > 0 THEN b.q1 - (:iqr_k * b.iqr)
                        ELSE b.q1
                    END AS lower_cut,
                    CASE
                        WHEN b.use_mad AND b.sigma_mad > 0 THEN b.med + (:mad_k * b.sigma_mad)
                        WHEN NOT b.use_mad AND b.iqr > 0 THEN b.q3 + (:iqr_k * b.iqr)
                        ELSE b.q3
                    END AS upper_cut
                FROM bounds b
            ),
            kept AS (
                SELECT d.bucket, d.price, d.qty
                FROM dev d
                JOIN cutoffs c USING (bucket)
                WHERE
                    (c.use_mad AND c.sigma_mad > 0 AND abs(d.price - c.med) <= (:mad_k * c.sigma_mad))
                OR ((NOT c.use_mad) AND c.iqr > 0 AND d.price BETWEEN c.lower_cut AND c.upper_cut)
                OR (c.use_mad AND COALESCE(c.sigma_mad, 0) = 0)
                OR ((NOT c.use_mad) AND COALESCE(c.iqr, 0) = 0)
            ),
            kept_counts AS (
                SELECT bucket, COUNT(*) AS kept_count
                FROM kept
                GROUP BY bucket
            )
            SELECT
                k.bucket AS timestamp,
                MIN(k.price)::integer AS min_buyout_price,
                MAX(k.price)::integer AS max_buyout_price,
                (percentile_cont(0.10) WITHIN GROUP (ORDER BY k.price))::integer AS p10_buyout_price,
                (percentile_cont(0.25) WITHIN GROUP (ORDER BY k.price))::integer AS p25_buyout_price,
                (percentile_cont(0.50) WITHIN GROUP (ORDER BY k.price))::integer AS median_buyout_price,
                (percentile_cont(0.75) WITHIN GROUP (ORDER BY k.price))::integer AS p75_buyout_price,
                (percentile_cont(0.90) WITHIN GROUP (ORDER BY k.price))::integer AS p90_buyout_price,
                AVG(k.price)::integer AS avg_buyout_price,
                COALESCE(kc.kept_count, 0) AS datapoint_count,
                (bc.n - COALESCE(kc.kept_count, 0)) AS outlier_count
            FROM kept k
            JOIN base_counts bc ON bc.bucket = k.bucket
            LEFT JOIN kept_counts kc ON kc.bucket = k.bucket
            GROUP BY k.bucket, bc.n, kc.kept_count
            ORDER BY k.bucket;
            """

            result = await session.execute(
                text(query),
                {
                    "from_ts": from_ts,
                    "to_ts": to_ts,
                    "item_id": item_id,
                    "server_realm_id": server_realm_id,
                    "mad_threshold": mad_threshold,
                    "mad_k": mad_k,
                    "iqr_k": iqr_k,
                },
            )

            return [
                AuctionDatapointFactory.get_price_hourly_summary(
                    timestamp=row.timestamp,
                    min_buyout=row.min_buyout_price,
                    max_buyout=row.max_buyout_price,
                    median_buyout=row.median_buyout_price,
                    avg_buyout=row.avg_buyout_price,  # NEW
                    p25_buyout=row.p25_buyout_price,
                    p75_buyout=row.p75_buyout_price,
                    p10_buyout=row.p10_buyout_price,
                    p90_buyout=row.p90_buyout_price,
                    datapoint_count=row.datapoint_count,
                    outlier_count=row.outlier_count,
                )
                for row in result
            ]

    async def get_auction_item_activity_hourly_summary(
        self,
        item_id: int,
        server_realm_id: int,
        from_timestamp: datetime.datetime,
        to_timestamp: datetime.datetime,
    ) -> list[AuctionItemActivityHourlySummary]:
        """
        Hourly market activity summary (value and liquidity).
        Counts & quantities are PRE-FILTERED (raw). Outlier filtering is used
        only to derive a robust price for estimated_market_value.

        returns:
            List[AuctionItemActivityHourlySummary]
        """
        from_ts = _ensure_utc(from_timestamp)
        to_ts = _ensure_utc(to_timestamp)

        # Tunables for robust price only:
        mad_threshold = 10
        mad_k = 3.0
        iqr_k = 1.5

        async with self.db.get_session() as session:
            query = f"""
            WITH base AS (
                SELECT
                    time_bucket('1 hour', p.timestamp) AS bucket,
                    p.buyout_price::numeric AS price,
                    p.quantity::numeric     AS qty
                FROM {AuctionDatapointModel.__tablename__} p
                WHERE p.item_id = :item_id
                AND p.server_realm_id = :server_realm_id
                AND p.timestamp >= :from_ts
                AND p.timestamp <  :to_ts
                AND p.buyout_price > 0
            ),
            base_counts AS (
                SELECT bucket, COUNT(*) AS n
                FROM base
                GROUP BY bucket
            ),
            base_value AS (
                SELECT bucket, SUM(price * qty) AS raw_total_market_value
                FROM base
                GROUP BY bucket
            ),
            base_qty AS (
                SELECT bucket, SUM(qty) AS raw_total_quantity
                FROM base
                GROUP BY bucket
            ),
            med AS (
                SELECT bucket,
                    percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS med
                FROM base
                GROUP BY bucket
            ),
            dev AS (
                SELECT b.bucket, b.price, b.qty, m.med,
                    abs(b.price - m.med) AS abs_dev
                FROM base b
                JOIN med  m USING (bucket)
            ),
            mad AS (
                SELECT bucket,
                    percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
                FROM dev
                GROUP BY bucket
            ),
            iqr AS (
                SELECT bucket,
                    percentile_cont(0.25) WITHIN GROUP (ORDER BY price) AS q1,
                    percentile_cont(0.75) WITHIN GROUP (ORDER BY price) AS q3
                FROM base
                GROUP BY bucket
            ),
            bounds AS (
                SELECT
                    bc.bucket,
                    bc.n,
                    m.med,
                    i.q1, i.q3,
                    a.mad,
                    (1.4826 * a.mad) AS sigma_mad,
                    (i.q3 - i.q1) AS iqr,
                    CASE
                        WHEN bc.n < GREATEST(3, :mad_threshold) OR a.mad IS NULL OR a.mad = 0
                            THEN FALSE -- use IQR
                        ELSE TRUE     -- use MAD
                    END AS use_mad
                FROM base_counts bc
                JOIN med m USING (bucket)
                JOIN iqr i USING (bucket)
                JOIN mad a USING (bucket)
            ),
            cutoffs AS (
                SELECT
                    b.bucket, b.n, b.med, b.q1, b.q3, b.mad, b.sigma_mad, b.iqr, b.use_mad,
                    CASE
                        WHEN b.use_mad AND b.sigma_mad > 0 THEN b.med - (:mad_k * b.sigma_mad)
                        WHEN NOT b.use_mad AND b.iqr > 0 THEN b.q1 - (:iqr_k * b.iqr)
                        ELSE b.q1
                    END AS lower_cut,
                    CASE
                        WHEN b.use_mad AND b.sigma_mad > 0 THEN b.med + (:mad_k * b.sigma_mad)
                        WHEN NOT b.use_mad AND b.iqr > 0 THEN b.q3 + (:iqr_k * b.iqr)
                        ELSE b.q3
                    END AS upper_cut
                FROM bounds b
            ),
            kept AS (
                -- rows used only to compute a robust price
                SELECT d.bucket, d.price
                FROM dev d
                JOIN cutoffs c USING (bucket)
                WHERE
                    (c.use_mad AND c.sigma_mad > 0 AND abs(d.price - c.med) <= (:mad_k * c.sigma_mad))
                    OR ((NOT c.use_mad) AND c.iqr > 0 AND d.price BETWEEN c.lower_cut AND c.upper_cut)
                    OR (c.use_mad AND COALESCE(c.sigma_mad, 0) = 0)
                    OR ((NOT c.use_mad) AND COALESCE(c.iqr, 0) = 0)
            ),
            agg_price AS (
                SELECT
                    bucket AS timestamp,
                    percentile_cont(0.5) WITHIN GROUP (ORDER BY price) AS med_price_filtered,
                    COUNT(*) AS kept_count
                FROM kept
                GROUP BY bucket
            )
            SELECT
                m.bucket                                        AS timestamp,
                bc.n                                            AS total_auctions,
                bq.raw_total_quantity::bigint                   AS total_quantity,
                bv.raw_total_market_value::bigint               AS total_market_value,
                ((COALESCE(ap.med_price_filtered, m.med)) * bq.raw_total_quantity)::bigint
                                                            AS estimated_market_value,
                COALESCE(ap.kept_count, 0)                      AS datapoint_count,
                (bc.n - COALESCE(ap.kept_count, 0))             AS outlier_count
            FROM med m
            JOIN base_counts bc ON bc.bucket = m.bucket
            JOIN base_value  bv ON bv.bucket = m.bucket
            JOIN base_qty    bq ON bq.bucket = m.bucket
            LEFT JOIN agg_price ap ON ap.timestamp = m.bucket
            ORDER BY m.bucket;
            """

            result = await session.execute(
                text(query),
                {
                    "from_ts": from_ts,
                    "to_ts": to_ts,
                    "item_id": item_id,
                    "server_realm_id": server_realm_id,
                    "mad_threshold": mad_threshold,
                    "mad_k": mad_k,
                    "iqr_k": iqr_k,
                },
            )

            return [
                AuctionDatapointFactory.get_market_activity_hourly_summary(
                    timestamp=row.timestamp,
                    total_auctions=row.total_auctions,
                    total_quantity=row.total_quantity,
                    total_market_value=row.total_market_value,
                    estimated_market_value=row.estimated_market_value,
                    datapoint_count=row.datapoint_count,
                    outlier_count=row.outlier_count,
                )
                for row in result
            ]
