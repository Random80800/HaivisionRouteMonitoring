import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_bool(env_var: str, default: bool = False) -> bool:
    return os.getenv(env_var, str(default)).lower() in ("true", "1", "yes")


def get_int(env_var: str, default: int) -> int:
    try:
        return int(os.getenv(env_var, str(default)))
    except ValueError:
        return default


BASE_URL = os.getenv("HMG_BASE_URL")
USERNAME = os.getenv("HMG_USERNAME")
PASSWORD = os.getenv("HMG_PASSWORD")

if not BASE_URL:
    raise ValueError("HMG_BASE_URL must be set in app/.env")

if not USERNAME or not PASSWORD:
    raise ValueError("HMG_USERNAME and HMG_PASSWORD must be set in app/.env")

VERIFY_SSL = get_bool("HMG_VERIFY_SSL", False)
REQUEST_TIMEOUT = get_int("HMG_TIMEOUT", 15)
POLL_INTERVAL_SECONDS = get_int("HMG_POLL_INTERVAL", 15)
DB_PATH = os.getenv("HMG_DB_PATH", "haivision_stats.db")
GRAPH_POINTS = get_int("HMG_GRAPH_POINTS", 60)

METRIC_OPTIONS = [
    "Bitrate",
    "Received Packets",
    "Used Bandwidth",
    "Reconnections",
    "Dropped Packets",
]

METRIC_COLORS = {
    "Bitrate": "#2563eb",
    "Received Packets": "#16a34a",
    "Used Bandwidth": "#f59e0b",
    "Reconnections": "#dc2626",
    "Dropped Packets": "#7c3aed",
}

WINDOW_OPTIONS = [15, 30, 60, 180, 360, 720, 1440, 2880, 4320, 10080]