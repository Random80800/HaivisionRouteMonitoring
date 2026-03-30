import sqlite3
from app.config import DB_PATH


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS route_metric_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                route_id TEXT NOT NULL,
                route_name TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS destination_metric_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                route_id TEXT NOT NULL,
                destination_id TEXT NOT NULL,
                destination_name TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL
            )
            """
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_route_metric_ts "
            "ON route_metric_history(route_id, metric_name, ts)"
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_destination_metric_ts "
            "ON destination_metric_history(route_id, destination_id, metric_name, ts)"
        )

        conn.commit()