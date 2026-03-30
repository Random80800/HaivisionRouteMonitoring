import time
from typing import Dict, Any, List
from app.database.db import get_db
from app.config import METRIC_OPTIONS, METRIC_COLORS


DESTINATION_METRIC_OPTIONS = [
    "Used Bandwidth",
    "Reconnections",
    "Dropped Packets",
    "Clients",
]

DESTINATION_METRIC_COLORS = {
    "Used Bandwidth": "#2563eb",
    "Reconnections": "#dc2626",
    "Dropped Packets": "#7c3aed",
    "Clients": "#16a34a",
}


def save_metrics(ts: int, route_id: str, route_name: str, metrics: Dict[str, float]) -> None:
    rows = [(ts, route_id, route_name, metric_name, metric_value) for metric_name, metric_value in metrics.items()]
    with get_db() as conn:
        conn.executemany(
            """
            INSERT INTO route_metric_history (ts, route_id, route_name, metric_name, metric_value)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()


def save_destination_metrics(
    ts: int,
    route_id: str,
    destination_id: str,
    destination_name: str,
    metrics: Dict[str, float],
) -> None:
    rows = [
        (ts, route_id, destination_id, destination_name, metric_name, metric_value)
        for metric_name, metric_value in metrics.items()
    ]
    with get_db() as conn:
        conn.executemany(
            """
            INSERT INTO destination_metric_history
            (ts, route_id, destination_id, destination_name, metric_name, metric_value)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()


def prune_old_metrics(days: int = 7) -> None:
    cutoff = int(time.time()) - days * 24 * 3600
    with get_db() as conn:
        conn.execute("DELETE FROM route_metric_history WHERE ts < ?", (cutoff,))
        conn.execute("DELETE FROM destination_metric_history WHERE ts < ?", (cutoff,))
        conn.commit()


def downsample_points(rows: List[Any], max_points: int) -> List[Any]:
    if len(rows) <= max_points:
        return rows

    step = len(rows) / float(max_points)
    out = []
    idx = 0.0

    while int(idx) < len(rows) and len(out) < max_points:
        out.append(rows[int(idx)])
        idx += step

    if out and out[-1] != rows[-1]:
        out[-1] = rows[-1]

    return out


def get_multi_metric_history(route_id: str, window_minutes: int, max_points: int) -> Dict[str, Any]:
    cutoff = int(time.time()) - (window_minutes * 60)

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT ts, metric_name, metric_value
            FROM route_metric_history
            WHERE route_id = ? AND ts >= ? AND metric_name IN (?, ?, ?, ?, ?)
            ORDER BY ts ASC
            """,
            (
                route_id,
                cutoff,
                METRIC_OPTIONS[0],
                METRIC_OPTIONS[1],
                METRIC_OPTIONS[2],
                METRIC_OPTIONS[3],
                METRIC_OPTIONS[4],
            ),
        ).fetchall()

    if not rows:
        return {
            "labels": [],
            "datasets": [
                {
                    "label": metric_name,
                    "values": [],
                    "borderColor": METRIC_COLORS[metric_name],
                }
                for metric_name in METRIC_OPTIONS
            ],
        }

    timestamps = sorted({row["ts"] for row in rows})
    if len(timestamps) > max_points:
        sampled_ts = downsample_points([{"ts": ts} for ts in timestamps], max_points)
        timestamps = [row["ts"] for row in sampled_ts]

    value_map = {metric_name: {} for metric_name in METRIC_OPTIONS}
    for row in rows:
        ts = row["ts"]
        if ts in timestamps:
            value_map[row["metric_name"]][ts] = row["metric_value"]

    if window_minutes <= 1440:
        labels = [time.strftime("%H:%M", time.localtime(ts)) for ts in timestamps]
    else:
        labels = [time.strftime("%d %b %H:%M", time.localtime(ts)) for ts in timestamps]
    datasets = []

    for metric_name in METRIC_OPTIONS:
        datasets.append(
            {
                "label": metric_name,
                "values": [value_map[metric_name].get(ts, None) for ts in timestamps],
                "borderColor": METRIC_COLORS[metric_name],
            }
        )

    return {
        "labels": labels,
        "datasets": datasets,
    }


def get_destination_metric_history(
    route_id: str,
    destination_id: str,
    window_minutes: int,
    max_points: int,
) -> Dict[str, Any]:
    cutoff = int(time.time()) - (window_minutes * 60)

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT ts, metric_name, metric_value
            FROM destination_metric_history
            WHERE route_id = ? AND destination_id = ? AND ts >= ?
              AND metric_name IN (?, ?, ?, ?)
            ORDER BY ts ASC
            """,
            (
                route_id,
                destination_id,
                cutoff,
                DESTINATION_METRIC_OPTIONS[0],
                DESTINATION_METRIC_OPTIONS[1],
                DESTINATION_METRIC_OPTIONS[2],
                DESTINATION_METRIC_OPTIONS[3],
            ),
        ).fetchall()

    if not rows:
        return {
            "labels": [],
            "datasets": [
                {
                    "label": metric_name,
                    "values": [],
                    "borderColor": DESTINATION_METRIC_COLORS[metric_name],
                }
                for metric_name in DESTINATION_METRIC_OPTIONS
            ],
        }

    timestamps = sorted({row["ts"] for row in rows})
    if len(timestamps) > max_points:
        sampled_ts = downsample_points([{"ts": ts} for ts in timestamps], max_points)
        timestamps = [row["ts"] for row in sampled_ts]

    value_map = {metric_name: {} for metric_name in DESTINATION_METRIC_OPTIONS}
    for row in rows:
        ts = row["ts"]
        if ts in timestamps:
            value_map[row["metric_name"]][ts] = row["metric_value"]

    if window_minutes <= 1440:
        labels = [time.strftime("%H:%M", time.localtime(ts)) for ts in timestamps]
    else:
        labels = [time.strftime("%d %b %H:%M", time.localtime(ts)) for ts in timestamps]
    datasets = []

    for metric_name in DESTINATION_METRIC_OPTIONS:
        datasets.append(
            {
                "label": metric_name,
                "values": [value_map[metric_name].get(ts, None) for ts in timestamps],
                "borderColor": DESTINATION_METRIC_COLORS[metric_name],
            }
        )

    return {
        "labels": labels,
        "datasets": datasets,
    }