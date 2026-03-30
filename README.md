Haivision Route Monitoring Dashboard

A lightweight Flask-based monitoring application for Haivision gateways.
It collects route and destination metrics, stores them in SQLite, and visualizes them with interactive charts.

Features
📡 Polls Haivision API for:
    Routes
    Sources
    Destinations
📊 Real-time and historical charts
📈 Multi-metric graphs:
    Bitrate
    Received Packets
    Used Bandwidth
    Reconnections
    Dropped Packets
🔎 Filter routes by name
⏱ Configurable time windows (up to multiple days)
💾 Persistent storage (SQLite)
🔁 Background polling service
🖥 Expandable destination-level charts



Configuration

Edit app/config.py:

BASE_URL → Haivision API URL
USERNAME / PASSWORD
POLL_INTERVAL_SECONDS
DB_PATH (optional)
