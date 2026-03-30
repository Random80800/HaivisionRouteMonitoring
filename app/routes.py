import time
from flask import Blueprint, jsonify, render_template, request

from app.config import BASE_URL, DB_PATH, POLL_INTERVAL_SECONDS, WINDOW_OPTIONS, GRAPH_POINTS
from app.services.poller import get_snapshot
from app.services.metrics_service import build_chart_data
from app.database.history_repository import (
    get_multi_metric_history,
    get_destination_metric_history,
)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    window_minutes = int(request.args.get("window", "60"))

    if window_minutes not in WINDOW_OPTIONS:
        window_minutes = 60

    snapshot = get_snapshot()
    routes = list(snapshot.get("routes", []))

    if query:
        routes = [
            route for route in routes
            if query in route["route_name"].lower()
            or any(query in d["name"].lower() for d in route["destinations"])
        ]

    chart_data = build_chart_data(routes, window_minutes)
    collected = snapshot.get("collected") or int(time.time())
    collected_human = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(collected))

    return render_template(
        "index.html",
        base_url=BASE_URL,
        device_id=snapshot.get("device_id", "-"),
        routes=routes,
        chart_data=chart_data,
        collected_human=collected_human,
        poll_interval=POLL_INTERVAL_SECONDS,
        query=query,
        error=snapshot.get("error"),
        db_path=DB_PATH,
        window_minutes=window_minutes,
        window_options=WINDOW_OPTIONS,
    )


@main.route("/api/routes")
def api_routes():
    return jsonify(get_snapshot())


@main.route("/api/history/<route_id>")
def api_history(route_id: str):
    window_minutes = int(request.args.get("window", "60"))
    return jsonify(get_multi_metric_history(route_id, window_minutes, GRAPH_POINTS))


@main.route("/api/destination-history/<route_id>/<destination_id>")
def api_destination_history(route_id: str, destination_id: str):
    window_minutes = int(request.args.get("window", "60"))
    return jsonify(get_destination_metric_history(route_id, destination_id, window_minutes, GRAPH_POINTS))