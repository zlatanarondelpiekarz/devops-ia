from typing import Any

import requests

from app.auth import GitLabAuth
from app.logger import setup_logger

logger = setup_logger(__name__)


class GitLabClient:
    def __init__(self, auth: GitLabAuth) -> None:
        self.auth = auth
        self.base_url = f"{auth.url.rstrip('/')}/api/v4"
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {auth.token}", "Content-Type": "application/json"}
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}/projects/{self.auth.project_id}/{path.lstrip('/')}"

    def get(self, path: str, params: dict | None = None) -> list[dict[str, Any]] | dict[str, Any]:
        response = self.session.get(self._url(path), params=params)
        response.raise_for_status()
        return response.json()

    def put(self, path: str, data: dict | None = None) -> dict[str, Any]:
        response = self.session.put(self._url(path), json=data or {})
        response.raise_for_status()
        return response.json()

    def post(self, path: str, data: dict | None = None) -> dict[str, Any]:
        response = self.session.post(self._url(path), json=data or {})
        response.raise_for_status()
        return response.json()

    def delete(self, path: str) -> None:
        response = self.session.delete(self._url(path))
        response.raise_for_status()

    def health_check(self) -> bool:
        try:
            resp = self.session.get(f"{self.base_url}/version")
            resp.raise_for_status()
            logger.info(
                "Connected to GitLab %s", resp.json().get("version", "unknown")
            )
            return True
        except requests.RequestException as e:
            logger.error("GitLab connection failed: %s", e)
            return False
