import threading
import time
from typing import Any, Dict, List

from app.config import POLL_INTERVAL_SECONDS
from app.services.haivision_client import HMGClient
from app.services.metrics_service import extract_metric_bundle, severity_from_route
from app.database.history_repository import (
    save_metrics,
    save_destination_metrics,
    prune_old_metrics,
)
from app.utils.helpers import safe, parse_number

snapshot_lock = threading.Lock()
last_snapshot: Dict[str, Any] = {
    "device_id": "-",
    "routes": [],
    "collected": None,
    "error": None,
}


def get_snapshot() -> Dict[str, Any]:
    with snapshot_lock:
        return {
            "device_id": last_snapshot.get("device_id", "-"),
            "routes": list(last_snapshot.get("routes", [])),
            "collected": last_snapshot.get("collected"),
            "error": last_snapshot.get("error"),
        }


def poll_once() -> Dict[str, Any]:
    client = HMGClient()
    client.login()
    devices = client.get_devices()

    if not devices:
        raise RuntimeError("No HMG devices returned by /api/devices")

    routes: List[Dict[str, Any]] = []
    ts = int(time.time())
    all_device_ids: List[str] = []

    for device in devices:
        device_id = device.get("_id")
        device_name = device.get("name", "-")

        if not device_id:
            continue

        all_device_ids.append(str(device_id))

        try:
            route_configs = client.get_routes(device_id)
        except Exception:
            continue

        for route_cfg in route_configs:
            route_id = route_cfg.get("_id") or route_cfg.get("id")

            if not route_id:
                continue

            try:
                route_stats = client.get_route_statistics(device_id, route_id)
            except Exception:
                continue

            route = route_stats.get("route", {})
            source = route.get("source", {})
            source_id = source.get("id")

            source_stats: Dict[str, Any] = {}
            if source_id:
                try:
                    source_stats = client.get_source_statistics(device_id, route_id, source_id)
                except Exception:
                    source_stats = {}

            detailed_destinations = []
            destination_stats_payloads = []

            for dst in route.get("destinations", []):
                dst_id = dst.get("id")
                dst_stats: Dict[str, Any] = {}

                if dst_id:
                    try:
                        dst_stats = client.get_destination_statistics(device_id, route_id, dst_id)
                        destination_stats_payloads.append(dst_stats)
                    except Exception:
                        dst_stats = {}

                dst_payload = dst_stats.get("destination", {}) if isinstance(dst_stats, dict) else {}

                destination_name = safe(dst.get("name"))
                destination_id = safe(dst.get("id"))
                clients_value = parse_number(dst.get("clientConnections"))
                bandwidth_value = parse_number(dst.get("usedBandwidth") or dst_payload.get("usedBandwidth"))
                reconnections_value = parse_number(dst_payload.get("reconnections"))
                dropped_packets_value = parse_number(
                    dst_payload.get("droppedPackets") or dst_payload.get("packetDrops")
                )

                if destination_id != "-":
                    try:
                        save_destination_metrics(
                            ts=ts,
                            route_id=safe(route.get("id"), safe(route_id)),
                            destination_id=destination_id,
                            destination_name=destination_name,
                            metrics={
                                "Used Bandwidth": bandwidth_value,
                                "Reconnections": reconnections_value,
                                "Dropped Packets": dropped_packets_value,
                                "Clients": clients_value,
                            },
                        )
                    except Exception:
                        pass

                detailed_destinations.append(
                    {
                        "id": destination_id,
                        "name": destination_name,
                        "state": safe(dst.get("state")),
                        "status": safe(dst.get("summaryStatusCode")),
                        "clients": safe(dst.get("clientConnections"), "0"),
                        "bandwidth": safe(dst.get("usedBandwidth") or dst_payload.get("usedBandwidth")),
                        "reconnections": safe(dst_payload.get("reconnections")),
                        "dropped_packets": safe(
                            dst_payload.get("droppedPackets") or dst_payload.get("packetDrops")
                        ),
                        "route_stats": dst,
                        "destination_stats": dst_stats,
                    }
                )

            try:
                metrics = extract_metric_bundle(route_stats, source_stats, destination_stats_payloads)
            except Exception:
                continue

            route_name = safe(route.get("name"), safe(route_cfg.get("name")))
            final_route_id = safe(route.get("id"), safe(route_id))

            try:
                save_metrics(ts, final_route_id, route_name, metrics)
            except Exception:
                pass

            route_row = {
                "route_id": final_route_id,
                "route_name": route_name,
                "route_state": safe(route.get("state")),
                "elapsed": safe(route.get("elapsedRunningTime")),
                "source_id": safe(source.get("id")),
                "source_name": safe(source.get("name")),
                "source_state": safe(source.get("state")),
                "destination_count": len(detailed_destinations),
                "destinations": detailed_destinations,
                "metrics": metrics,
                "severity": severity_from_route(
                    safe(route.get("state")),
                    safe(source.get("state")),
                    route.get("destinations", []),
                ),
                "raw": {
                    "device_id": device_id,
                    "device_name": device_name,
                    "route_statistics": route_stats,
                    "source_statistics": source_stats,
                    "destination_statistics": destination_stats_payloads,
                },
            }
            routes.append(route_row)

    return {
        "device_id": ", ".join(all_device_ids) if all_device_ids else "-",
        "routes": routes,
        "collected": ts,
        "error": None,
    }


def background_poller() -> None:
    global last_snapshot
    prune_counter = 0

    while True:
        try:
            snapshot = poll_once()
            with snapshot_lock:
                last_snapshot = snapshot

            prune_counter += 1
            if prune_counter >= 20:
                prune_old_metrics(days=7)
                prune_counter = 0

        except Exception as exc:
            with snapshot_lock:
                last_snapshot = {
                    "device_id": last_snapshot.get("device_id", "-"),
                    "routes": last_snapshot.get("routes", []),
                    "collected": int(time.time()),
                    "error": str(exc),
                }

        time.sleep(POLL_INTERVAL_SECONDS)


def start_background_poller() -> None:
    thread = threading.Thread(target=background_poller, daemon=True)
    thread.start()