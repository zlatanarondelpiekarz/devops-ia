import os
from pathlib import Path
from typing import Any

import yaml


class Settings:
    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = config_path or str(
            Path(__file__).parent.parent / "config" / "settings.yaml"
        )
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        path = Path(self.config_path)
        if path.exists():
            with open(path) as f:
                self._data = yaml.safe_load(f) or {}
        self._data.setdefault("gitlab", {})
        self._data.setdefault("rules", {})

    @property
    def gitlab_url(self) -> str:
        return os.getenv(
            "GITLAB_URL",
            self._data.get("gitlab", {}).get("url", "https://gitlab.com"),
        )

    @property
    def gitlab_token(self) -> str:
        token = os.getenv("GITLAB_TOKEN") or self._data.get("gitlab", {}).get(
            "token"
        )
        if not token:
            raise ValueError(
                "GITLAB_TOKEN must be set in environment or settings.yaml"
            )
        return token

    @property
    def gitlab_project_id(self) -> str:
        return os.getenv(
            "GITLAB_PROJECT_ID",
            str(self._data.get("gitlab", {}).get("project_id", "")),
        )

    @property
    def rules_path(self) -> str:
        return str(
            Path(__file__).parent.parent
            / self._data.get("rules", {}).get(
                "path", "rules"
            )
        )

    def reload(self) -> None:
        self._load()
