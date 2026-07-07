from typing import Any

from app.gitlab_client import GitLabClient
from app.logger import setup_logger

logger = setup_logger(__name__)

_COMPARISON_FIELDS = [
    "approvals_required",
    "rule_type",
    "branch_name",
]

_DEFAULTS: dict[str, Any] = {
    "approvals_required": 1,
    "rule_type": "regular",
    "branch_name": None,
}


class ApprovalRule:
    def __init__(self, client: GitLabClient, rule: dict[str, Any]) -> None:
        self.client = client
        self.rule = rule

    def apply(self) -> dict[str, Any] | None:
        name = self.rule.get("name", "default")
        logger.info("Applying approval rule: %s", name)
        existing = self._get_current()
        if existing:
            if self._matches(existing):
                logger.info("Approval rule %s already up-to-date, skipping", name)
                return existing
            return self._update(existing)
        return self._create()

    def _get_current(self) -> dict[str, Any] | None:
        rules = self.client.get("approval_rules")
        if isinstance(rules, list):
            for r in rules:
                if r["name"] == self.rule.get("name"):
                    return r
        return None

    def _matches(self, existing: dict[str, Any]) -> bool:
        for field in _COMPARISON_FIELDS:
            desired = self.rule.get(field, _DEFAULTS[field])
            actual = existing.get(field)
            if desired != actual:
                logger.debug(
                    "Field %s differs: desired=%s, actual=%s",
                    field, desired, actual,
                )
                return False
        return True

    def _build_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.rule["name"],
            "approvals_required": self.rule.get("approvals_required", 1),
            "rule_type": self.rule.get("rule_type", "regular"),
        }
        branch_name = self.rule.get("branch_name")
        if branch_name:
            payload["branch_name"] = branch_name
        return payload

    def _create(self) -> dict[str, Any]:
        logger.info("Creating approval rule: %s", self.rule.get("name"))
        return self.client.post("approval_rules", self._build_payload())

    def _update(self, existing: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "approvals_required": self.rule.get("approvals_required", 1),
            "rule_type": self.rule.get("rule_type", "regular"),
        }
        branch_name = self.rule.get("branch_name")
        if branch_name:
            payload["branch_name"] = branch_name
        logger.info("Updating approval rule: %s", self.rule.get("name"))
        return self.client.put(f"approval_rules/{existing['id']}", payload)

    def delete(self) -> None:
        existing = self._get_current()
        if existing:
            name = self.rule.get("name", "default")
            logger.info("Deleting approval rule: %s", name)
            self.client.delete(f"approval_rules/{existing['id']}")
