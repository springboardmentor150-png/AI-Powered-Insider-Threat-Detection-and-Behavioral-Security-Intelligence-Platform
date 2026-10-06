"""
ITBIS - Day 17 ML Feature Engineering

This module converts raw activity logs from MongoDB into a clean,
numeric employee-per-day feature table for machine learning.

The resulting features are consumed by the Isolation Forest model
on Day 18.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from .mongo import activity_logs


INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")

FEATURE_COLUMNS = [
    "avg_login_hour",
    "download_count",
    "total_download_mb",
    "unique_devices",
    "total_events",
]


def build_feature_table() -> pd.DataFrame:
    """
    Build one numeric feature row per employee per day.

    Returns:
        pandas.DataFrame:
            Columns:
            - employee_code
            - date
            - avg_login_hour
            - download_count
            - total_download_mb
            - unique_devices
            - total_events
    """

    logs = list(activity_logs.find({}))

    if not logs:
        return pd.DataFrame(
            columns=["employee_code", "date", *FEATURE_COLUMNS]
        )

    df = pd.DataFrame(logs)

    # ---------------------------------------------------------
    # 1. Normalize timestamps
    # ---------------------------------------------------------
    #
    # MongoDB stores our activity timestamps as UTC.
    # Behavioral baselines were calculated using India time,
    # so ML features must use the same timezone.
    #
    def to_india_time(value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=ZoneInfo("UTC"))

            return value.astimezone(INDIA_TIMEZONE)

        return pd.NaT

    df["timestamp"] = df["timestamp"].apply(to_india_time)

    # Remove malformed records that cannot be assigned to a day.
    df = df.dropna(subset=["timestamp", "employee_code"])

    if df.empty:
        return pd.DataFrame(
            columns=["employee_code", "date", *FEATURE_COLUMNS]
        )

    # ---------------------------------------------------------
    # 2. Extract the local calendar date
    # ---------------------------------------------------------

    df["date"] = df["timestamp"].apply(lambda value: value.date())

    # ---------------------------------------------------------
    # 3. Calculate login hour
    # ---------------------------------------------------------
    #
    # Only login events receive a login_hour value.
    # Other event types remain missing and are ignored by mean().
    #

    df["login_hour"] = df.apply(
        lambda row: (
            row["timestamp"].hour
            + row["timestamp"].minute / 60
            + row["timestamp"].second / 3600
            if row["event_type"] == "login"
            else None
        ),
        axis=1,
    )

    # ---------------------------------------------------------
    # 4. Identify data-transfer events
    # ---------------------------------------------------------
    #
    # Our project uses data_transfer as the event representing
    # measurable data movement.
    #

    df["is_download"] = df["event_type"].eq("data_transfer")

    # ---------------------------------------------------------
    # 5. Normalize data volume
    # ---------------------------------------------------------
    #
    # Missing or malformed values become 0.
    #

    df["data_volume_mb"] = pd.to_numeric(
        df["data_volume_mb"],
        errors="coerce",
    ).fillna(0)

    # ---------------------------------------------------------
    # 6. Normalize device IDs
    # ---------------------------------------------------------
    #
    # Missing device IDs should not count as a real device.
    #

    df["device_id"] = df["device_id"].fillna("").astype(str).str.strip()

    # ---------------------------------------------------------
    # 7. Aggregate by employee and day
    # ---------------------------------------------------------

    features = (
        df.groupby(["employee_code", "date"])
        .agg(
            avg_login_hour=("login_hour", "mean"),
            download_count=("is_download", "sum"),
            total_download_mb=(
                "data_volume_mb",
                "sum",
            ),
            unique_devices=("device_id", "nunique"),
            total_events=("event_type", "count"),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # 8. Ensure all ML columns are numeric
    # ---------------------------------------------------------

    for column in FEATURE_COLUMNS:
        features[column] = pd.to_numeric(
            features[column],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # 9. Handle missing values
    # ---------------------------------------------------------
    #
    # Isolation Forest requires a fully numeric table without
    # NaN values.
    #

    features[FEATURE_COLUMNS] = features[FEATURE_COLUMNS].fillna(0)

    # ---------------------------------------------------------
    # 10. Sort for deterministic output
    # ---------------------------------------------------------

    features = features.sort_values(
        ["employee_code", "date"]
    ).reset_index(drop=True)

    return features