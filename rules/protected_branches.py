from typing import Any

from app.gitlab_client import GitLabClient
from app.logger import setup_logger

logger = setup_logger(__name__)

_COMPARISON_FIELDS = [
    "push_access_level",
    "merge_access_level",
    "allow_force_push",
    "code_owner_approval_required",
]


class ProtectedBranchRule:
    def __init__(self, client: GitLabClient, rule: dict[str, Any]) -> None:
        self.client = client
        self.rule = rule

    def apply(self) -> dict[str, Any] | None:
        name = self.rule["name"]
        logger.info("Applying protected branch rule: %s", name)
        existing = self._get_current()
        if existing:
            if self._matches(existing):
                logger.info("Branch %s already up-to-date, skipping", name)
                return existing
            return self._update(existing)
        return self._create()

    def delete(self) -> None:
        name = self.rule["name"]
        logger.info("Deleting protected branch rule: %s", name)
        self.client.delete(f"protected_branches/{name}")

    def _get_current(self) -> dict[str, Any] | None:
        branches = self.client.get("protected_branches")
        for b in branches:
            if b["name"] == self.rule["name"]:
                return b
        return None

    def _matches(self, existing: dict[str, Any]) -> bool:
        for field in _COMPARISON_FIELDS:
            desired = self.rule.get(field, self._default(field))
            actual = existing.get(field)
            if desired != actual:
                logger.debug(
                    "Field %s differs: desired=%s, actual=%s",
                    field, desired, actual,
                )
                return False
        return True

    def _build_payload(self) -> dict[str, Any]:
        return {
            "name": self.rule["name"],
            "push_access_level": self.rule.get("push_access_level", 40),
            "merge_access_level": self.rule.get("merge_access_level", 40),
            "allow_force_push": self.rule.get("allow_force_push", False),
            "code_owner_approval_required": self.rule.get(
                "code_owner_approval_required", False
            ),
        }

    def _create(self) -> dict[str, Any]:
        return self.client.post("protected_branches", self._build_payload())

    def _update(self, existing: dict[str, Any]) -> dict[str, Any]:
        payload = self._build_payload()
        payload.pop("name", None)
        logger.info("Branch %s already protected, updating", self.rule["name"])
        return self.client.put(
            f"protected_branches/{self.rule['name']}", payload
        )

    @staticmethod
    def _default(field: str) -> int | bool:
        defaults = {
            "push_access_level": 40,
            "merge_access_level": 40,
            "allow_force_push": False,
            "code_owner_approval_required": False,
        }
        return defaults[field]
