from dataclasses import dataclass, field
from typing import Any

from app.gitlab_client import GitLabClient
from app.logger import setup_logger
from rules.protected_branches import ProtectedBranchRule
from rules.merge_requests import MergeRequestRule
from rules.approvals import ApprovalRule

logger = setup_logger(__name__)


@dataclass
class RuleStatus:
    rule_type: str
    name: str
    compliant: bool
    status: str
    details: list[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    rules: list[RuleStatus] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.rules)

    @property
    def compliant_count(self) -> int:
        return sum(1 for r in self.rules if r.compliant)

    @property
    def non_compliant_count(self) -> int:
        return sum(1 for r in self.rules if not r.compliant)

    @property
    def all_compliant(self) -> bool:
        return self.non_compliant_count == 0

    def print_report(self) -> None:
        logger.info("=" * 50)
        logger.info("COMPLIANCE REPORT")
        logger.info("=" * 50)
        for rule in self.rules:
            icon = "✓" if rule.compliant else "✗"
            logger.info("  %s [%s] %s — %s", icon, rule.rule_type, rule.name, rule.status)
            for detail in rule.details:
                logger.info("      %s", detail)
        logger.info("-" * 50)
        logger.info(
            "Total: %d | Compliant: %d | Non-compliant: %d",
            self.total, self.compliant_count, self.non_compliant_count,
        )
        logger.info("=" * 50)


class ComplianceChecker:
    def __init__(self, client: GitLabClient, rules_data: dict[str, Any]) -> None:
        self.client = client
        self.rules_data = rules_data

    def check_all(self) -> ComplianceReport:
        report = ComplianceReport()
        self._check_protected_branches(report)
        self._check_merge_requests(report)
        self._check_approval_rules(report)
        return report

    def _check_protected_branches(self, report: ComplianceReport) -> None:
        for rule_data in self.rules_data.get("protected_branches", []):
            rule = ProtectedBranchRule(self.client, rule_data)
            name = rule_data.get("name", "unknown")
            current = rule._get_current()
            if current is None:
                report.rules.append(RuleStatus(
                    rule_type="protected_branch",
                    name=name,
                    compliant=False,
                    status="NOT FOUND — will be created",
                ))
            elif rule._matches(current):
                report.rules.append(RuleStatus(
                    rule_type="protected_branch",
                    name=name,
                    compliant=True,
                    status="Compliant",
                ))
            else:
                diffs = self._diff_protected_branch(rule_data, current)
                report.rules.append(RuleStatus(
                    rule_type="protected_branch",
                    name=name,
                    compliant=False,
                    status="NON-COMPLIANT — will be updated",
                    details=diffs,
                ))

    def _check_merge_requests(self, report: ComplianceReport) -> None:
        mr_data = self.rules_data.get("merge_requests")
        if not mr_data:
            return
        rule = MergeRequestRule(self.client, mr_data)
        current = rule._get_current()
        if current is None:
            report.rules.append(RuleStatus(
                rule_type="merge_requests",
                name="project settings",
                compliant=False,
                status="NOT FOUND — will be created",
            ))
        elif rule._matches(current):
            report.rules.append(RuleStatus(
                rule_type="merge_requests",
                name="project settings",
                compliant=True,
                status="Compliant",
            ))
        else:
            diffs = self._diff_mr(mr_data, current)
            report.rules.append(RuleStatus(
                rule_type="merge_requests",
                name="project settings",
                compliant=False,
                status="NON-COMPLIANT — will be updated",
                details=diffs,
            ))

    def _check_approval_rules(self, report: ComplianceReport) -> None:
        for rule_data in self.rules_data.get("approval_rules", []):
            rule = ApprovalRule(self.client, rule_data)
            name = rule_data.get("name", "unknown")
            current = rule._get_current()
            if current is None:
                report.rules.append(RuleStatus(
                    rule_type="approval_rule",
                    name=name,
                    compliant=False,
                    status="NOT FOUND — will be created",
                ))
            elif rule._matches(current):
                report.rules.append(RuleStatus(
                    rule_type="approval_rule",
                    name=name,
                    compliant=True,
                    status="Compliant",
                ))
            else:
                diffs = self._diff_approval(rule_data, current)
                report.rules.append(RuleStatus(
                    rule_type="approval_rule",
                    name=name,
                    compliant=False,
                    status="NON-COMPLIANT — will be updated",
                    details=diffs,
                ))

    @staticmethod
    def _diff_protected_branch(
        desired: dict[str, Any], current: dict[str, Any],
    ) -> list[str]:
        diffs: list[str] = []
        fields = ["push_access_level", "merge_access_level", "allow_force_push", "code_owner_approval_required"]
        defaults = {"push_access_level": 40, "merge_access_level": 40, "allow_force_push": False, "code_owner_approval_required": False}
        for f in fields:
            d = desired.get(f, defaults[f])
            a = current.get(f)
            if d != a:
                diffs.append(f"{f}: desired={d}, actual={a}")
        return diffs

    @staticmethod
    def _diff_mr(desired: dict[str, Any], current: dict[str, Any]) -> list[str]:
        diffs: list[str] = []
        mapping = {
            "merge_method": "merge_method",
            "pipeline_required": "only_allow_merge_if_pipeline_succeeds",
            "discussions_resolved": "only_allow_merge_if_all_discussions_are_resolved",
            "remove_source_branch": "remove_source_branch_after_merge",
        }
        defaults = {"merge_method": "merge", "pipeline_required": True, "discussions_resolved": True, "remove_source_branch": True}
        for yaml_field, api_field in mapping.items():
            d = desired.get(yaml_field, defaults[yaml_field])
            a = current.get(api_field)
            if d != a:
                diffs.append(f"{yaml_field}: desired={d}, actual={a}")
        return diffs

    @staticmethod
    def _diff_approval(desired: dict[str, Any], current: dict[str, Any]) -> list[str]:
        diffs: list[str] = []
        fields = ["approvals_required", "rule_type", "branch_name"]
        defaults = {"approvals_required": 1, "rule_type": "regular", "branch_name": None}
        for f in fields:
            d = desired.get(f, defaults[f])
            a = current.get(f)
            if d != a:
                diffs.append(f"{f}: desired={d}, actual={a}")
        return diffs
