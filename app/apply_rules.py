import sys
from pathlib import Path

import yaml

from app.auth import GitLabAuth
from app.config import Settings
from app.gitlab_client import GitLabClient
from app.logger import setup_logger
from rules.protected_branches import ProtectedBranchRule
from rules.merge_requests import MergeRequestRule
from rules.approvals import ApprovalRule

logger = setup_logger(__name__)


def load_rules(rules_path: str) -> dict:
    path = Path(rules_path)
    if not path.exists():
        logger.warning("Rules path %s not found, skipping", rules_path)
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    settings = Settings()
    auth = GitLabAuth.from_settings(settings)
    client = GitLabClient(auth)

    if not client.health_check():
        logger.error("Cannot connect to GitLab")
        return 1

    rules_data = load_rules(settings.rules_path)

    for branch_rule in rules_data.get("protected_branches", []):
        rule = ProtectedBranchRule(client, branch_rule)
        rule.apply()

    if "merge_requests" in rules_data:
        rule = MergeRequestRule(client, rules_data["merge_requests"])
        rule.apply()

    for approval_rule in rules_data.get("approval_rules", []):
        rule = ApprovalRule(client, approval_rule)
        rule.apply()

    logger.info("All rules applied successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
