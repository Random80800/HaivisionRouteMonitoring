from typing import Any, Dict, List
import requests
import urllib3

from app.config import BASE_URL, USERNAME, PASSWORD, VERIFY_SSL, REQUEST_TIMEOUT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HMGClient:
    def __init__(
        self,
        base_url: str = BASE_URL,
        username: str = USERNAME,
        password: str = PASSWORD,
        verify_ssl: bool = VERIFY_SSL,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()

    def login(self) -> None:
        response = self.session.post(
            f"{self.base_url}/api/session",
            json={"username": self.username, "password": self.password},
            timeout=REQUEST_TIMEOUT,
            verify=self.verify_ssl,
        )
        response.raise_for_status()

    def get_devices(self) -> List[Dict[str, Any]]:
        response = self.session.get(
            f"{self.base_url}/api/devices",
            timeout=REQUEST_TIMEOUT,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def get_routes(self, device_id: str) -> List[Dict[str, Any]]:
        all_routes: List[Dict[str, Any]] = []
        page = 1

        while True:
            response = self.session.get(
                f"{self.base_url}/api/gateway/{device_id}/routes",
                params={"page": page},
                timeout=REQUEST_TIMEOUT,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                all_routes.extend(data)
                break

            if not isinstance(data, dict):
                break

            page_routes = data.get("data", [])
            if not isinstance(page_routes, list) or not page_routes:
                break

            all_routes.extend(page_routes)

            num_pages = data.get("numPages")
            if isinstance(num_pages, int) and page >= num_pages:
                break

            if len(page_routes) == 0:
                break

            page += 1

        print(f"[DEBUG get_routes] fetched total routes for device {device_id}: {len(all_routes)}")
        return all_routes

    def get_route_statistics(self, device_id: str, route_id: str) -> Dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/gateway/{device_id}/statistics",
            params={"routeID": route_id},
            timeout=REQUEST_TIMEOUT,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def get_source_statistics(self, device_id: str, route_id: str, source_id: str) -> Dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/gateway/{device_id}/statistics",
            params={"routeID": route_id, "sourceID": source_id},
            timeout=REQUEST_TIMEOUT,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def get_destination_statistics(self, device_id: str, route_id: str, destination_id: str) -> Dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/api/gateway/{device_id}/statistics",
            params={"routeID": route_id, "destinationID": destination_id},
            timeout=REQUEST_TIMEOUT,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()