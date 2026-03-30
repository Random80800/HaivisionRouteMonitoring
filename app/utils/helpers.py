from typing import Any, Dict, List, Tuple


def safe(value: Any, default: str = "-") -> str:
    return default if value in (None, "") else str(value)


def parse_number(value: Any) -> float:
    if value in (None, "", "-"):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")
    filtered = "".join(ch for ch in text if ch.isdigit() or ch in ".-")
    if filtered in ("", ".", "-", "-."):
        return 0.0

    try:
        return float(filtered)
    except ValueError:
        return 0.0


def get_nested(data: Dict[str, Any], paths: List[Tuple[str, ...]]) -> Any:
    for path in paths:
        current: Any = data
        ok = True
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                ok = False
                break
        if ok:
            return current
    return None
