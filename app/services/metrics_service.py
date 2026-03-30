from typing import Any, Dict, List

from app.utils.helpers import parse_number, get_nested
from app.database.history_repository import get_multi_metric_history
from app.config import GRAPH_POINTS


def extract_metric_bundle(
    route_stats: Dict[str, Any],
    source_stats: Dict[str, Any],
    destination_stats_list: List[Dict[str, Any]],
) -> Dict[str, float]:
    route = route_stats.get("route", {}) if isinstance(route_stats, dict) else {}
    source_route = route.get("source", {}) if isinstance(route, dict) else {}
    source_payload = source_stats.get("source", {}) if isinstance(source_stats, dict) else {}

    bitrate = parse_number(get_nested(source_payload, [
        ("bitrate",),
        ("outputBitrate",),
        ("inputBitrate",),
        ("statistics", "bitrate"),
    ]) or get_nested(source_route, [
        ("bitrate",),
        ("usedBandwidth",),
    ]))

    received_packets = parse_number(get_nested(source_payload, [
        ("receivedPackets",),
        ("packetCount",),
        ("statistics", "receivedPackets"),
    ]))

    used_bandwidth = parse_number(get_nested(source_payload, [
        ("usedBandwidth",),
        ("bandwidth",),
        ("statistics", "usedBandwidth"),
    ]) or get_nested(source_route, [
        ("usedBandwidth",),
    ]))

    reconnections = parse_number(get_nested(source_payload, [
        ("reconnections",),
        ("reconnectCount",),
        ("statistics", "reconnections"),
    ]))

    dropped_packets = parse_number(get_nested(source_payload, [
        ("droppedPackets",),
        ("packetDrops",),
        ("statistics", "droppedPackets"),
    ]))

    for dst_stats in destination_stats_list:
        dst_payload = dst_stats.get("destination", {}) if isinstance(dst_stats, dict) else {}
        if not received_packets:
            received_packets += parse_number(get_nested(dst_payload, [
                ("receivedPackets",),
                ("packetCount",),
            ]))
        used_bandwidth += parse_number(get_nested(dst_payload, [
            ("usedBandwidth",),
            ("bandwidth",),
        ]))
        reconnections += parse_number(get_nested(dst_payload, [
            ("reconnections",),
            ("reconnectCount",),
        ]))
        dropped_packets += parse_number(get_nested(dst_payload, [
            ("droppedPackets",),
            ("packetDrops",),
        ]))
        if not bitrate:
            bitrate += parse_number(get_nested(dst_payload, [
                ("bitrate",),
                ("outputBitrate",),
            ]))

    return {
        "Bitrate": round(bitrate, 3),
        "Received Packets": round(received_packets, 3),
        "Used Bandwidth": round(used_bandwidth, 3),
        "Reconnections": round(reconnections, 3),
        "Dropped Packets": round(dropped_packets, 3),
    }


def severity_from_route(route_state: str, source_state: str, destinations: List[Dict[str, Any]]) -> str:
    rs = route_state.lower()
    ss = source_state.lower()

    if rs not in ("running", "idle", "stopped"):
        return "warn"
    if ss not in ("connected", "started", "listening", "-"):
        return "error"

    problems = 0
    warnings = 0

    for d in destinations:
        st = str(d.get("state", "-")).lower()
        if st in ("connected", "started", "listening", "running"):
            continue
        if st in ("waiting for data", "idle", "-"):
            warnings += 1
        else:
            problems += 1

    if problems:
        return "error"
    if warnings:
        return "warn"
    return "ok"


def build_chart_data(routes: List[Dict[str, Any]], window_minutes: int) -> List[Dict[str, Any]]:
    return [
        {
            "route_id": route["route_id"],
            **get_multi_metric_history(route["route_id"], window_minutes, GRAPH_POINTS),
        }
        for route in routes
    ]