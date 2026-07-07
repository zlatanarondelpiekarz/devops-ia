from typing import Any

from app.gitlab_client import GitLabClient
from app.logger import setup_logger

logger = setup_logger(__name__)

_FIELD_MAPPING: dict[str, str] = {
    "merge_method": "merge_method",
    "pipeline_required": "only_allow_merge_if_pipeline_succeeds",
    "discussions_resolved": "only_allow_merge_if_all_discussions_are_resolved",
    "remove_source_branch": "remove_source_branch_after_merge",
}

_DEFAULTS: dict[str, Any] = {
    "merge_method": "merge",
    "pipeline_required": True,
    "discussions_resolved": True,
    "remove_source_branch": True,
}


class MergeRequestRule:
    def __init__(self, client: GitLabClient, rule: dict[str, Any]) -> None:
        self.client = client
        self.rule = rule

    def apply(self) -> dict[str, Any]:
        logger.info("Applying merge request settings")
        existing = self._get_current()
        if existing:
            if self._matches(existing):
                logger.info("Merge request settings already up-to-date, skipping")
                return existing
            return self._update()
        return self._update()

    def _get_current(self) -> dict[str, Any] | None:
        try:
            project = self.client.get("")
            if isinstance(project, dict):
                return project
            return None
        except Exception as e:
            logger.error("Failed to get current project settings: %s", e)
            return None

    def _matches(self, existing: dict[str, Any]) -> bool:
        for yaml_field, api_field in _FIELD_MAPPING.items():
            desired = self.rule.get(yaml_field, _DEFAULTS[yaml_field])
            actual = existing.get(api_field)
            if desired != actual:
                logger.debug(
                    "Field %s differs: desired=%s, actual=%s",
                    yaml_field, desired, actual,
                )
                return False
        return True

    def _build_payload(self) -> dict[str, Any]:
        return {
            api_field: self.rule.get(yaml_field, _DEFAULTS[yaml_field])
            for yaml_field, api_field in _FIELD_MAPPING.items()
        }

    def _update(self) -> dict[str, Any]:
        payload = self._build_payload()
        logger.info("Updating merge request settings")
        return self.client.put("", payload)
