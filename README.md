# 📡 Haivision Route Monitoring Dashboard

A lightweight **Flask-based monitoring application** for Haivision gateways.
It collects route and destination metrics, stores them in **SQLite**, and visualizes them with **interactive charts**.

---

## 🚀 Features

* 📡 Polls Haivision API for:

  * Routes
  * Sources
  * Destinations

* 📊 Real-time and historical data visualization

* 📈 Multi-metric graphs:

  * Bitrate
  * Received Packets
  * Used Bandwidth
  * Reconnections
  * Dropped Packets

* 🔎 Filter routes by name

* ⏱ Configurable time windows (up to multiple days)

* 💾 Persistent storage using SQLite

* 🔁 Background polling service

* 🖥 Expandable destination-level charts

---

## ⚙️ Configuration

Edit the configuration file:

```bash
app/config.py
```

Set the following variables:

```python
BASE_URL = "http://your-haivision"
USERNAME = "your_username"
PASSWORD = "your_password"

POLL_INTERVAL_SECONDS = 10  # Adjust polling frequency
DB_PATH = "data.db"         # Optional custom DB path
```

---

## ▶️ Running the App

1. (Optional) Activate your virtual environment:

```bash
source HaivisionVenv/bin/activate
```

2. Run the application:

```bash
python3 run.py
```

3. Open your browser and navigate to:

```
http://localhost:5000
```

---

## 🗄️ Data Storage

* Uses **SQLite** for lightweight persistence
* Stores historical metrics for visualization and analysis

---

## 📌 Notes

* Ensure the Haivision API is accessible from your machine
* Adjust polling interval based on system performance and load
* Designed to be lightweight and easily extendable

---
