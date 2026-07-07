import pytest
import responses

from app.compliance import ComplianceChecker, ComplianceReport


@responses.activate
def test_all_compliant_when_matching(client):
    rules_data = {
        "protected_branches": [
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
        ],
        "merge_requests": {
            "merge_method": "merge", "pipeline_required": True,
            "discussions_resolved": True, "remove_source_branch": True,
        },
        "approval_rules": [
            {"name": "main-approval", "approvals_required": 2,
             "rule_type": "regular", "branch_name": "main"},
        ],
    }

    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=[{"name": "main", "push_access_level": 40, "merge_access_level": 40,
               "allow_force_push": False, "code_owner_approval_required": True}],
        status=200,
    )
    responses.get(
        f"{client.base_url}/projects/123/",
        json={"merge_method": "merge", "only_allow_merge_if_pipeline_succeeds": True,
              "only_allow_merge_if_all_discussions_are_resolved": True,
              "remove_source_branch_after_merge": True},
        status=200,
    )
    responses.get(
        f"{client.base_url}/projects/123/approval_rules",
        json=[{"id": 1, "name": "main-approval", "approvals_required": 2,
               "rule_type": "regular", "branch_name": "main"}],
        status=200,
    )

    checker = ComplianceChecker(client, rules_data)
    report = checker.check_all()
    assert report.total == 3
    assert report.compliant_count == 3
    assert report.non_compliant_count == 0
    assert report.all_compliant is True


@responses.activate
def test_non_compliant_detected(client):
    rules_data = {
        "protected_branches": [
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
        ],
        "merge_requests": {
            "merge_method": "merge", "pipeline_required": True,
            "discussions_resolved": True, "remove_source_branch": True,
        },
        "approval_rules": [
            {"name": "main-approval", "approvals_required": 2,
             "rule_type": "regular", "branch_name": "main"},
        ],
    }

    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=[{"name": "main", "push_access_level": 30, "merge_access_level": 40,
               "allow_force_push": False, "code_owner_approval_required": True}],
        status=200,
    )
    responses.get(
        f"{client.base_url}/projects/123/",
        json={"merge_method": "ff", "only_allow_merge_if_pipeline_succeeds": True,
              "only_allow_merge_if_all_discussions_are_resolved": True,
              "remove_source_branch_after_merge": True},
        status=200,
    )
    responses.get(
        f"{client.base_url}/projects/123/approval_rules",
        json=[{"id": 1, "name": "main-approval", "approvals_required": 1,
               "rule_type": "regular", "branch_name": "main"}],
        status=200,
    )

    checker = ComplianceChecker(client, rules_data)
    report = checker.check_all()
    assert report.total == 3
    assert report.compliant_count == 0
    assert report.non_compliant_count == 3
    assert report.all_compliant is False


@responses.activate
def test_not_found_rules(client):
    rules_data = {
        "protected_branches": [
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
        ],
        "merge_requests": {
            "merge_method": "merge", "pipeline_required": True,
            "discussions_resolved": True, "remove_source_branch": True,
        },
        "approval_rules": [
            {"name": "main-approval", "approvals_required": 2,
             "rule_type": "regular", "branch_name": "main"},
        ],
    }

    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=[],
        status=200,
    )
    responses.get(
        f"{client.base_url}/projects/123/",
        status=404,
    )
    responses.get(
        f"{client.base_url}/projects/123/approval_rules",
        json=[],
        status=200,
    )

    checker = ComplianceChecker(client, rules_data)
    report = checker.check_all()
    assert report.total == 3
    assert report.compliant_count == 0
    assert report.non_compliant_count == 3


@responses.activate
def test_empty_rules_data(client):
    checker = ComplianceChecker(client, {})
    report = checker.check_all()
    assert report.total == 0
    assert report.all_compliant is True


@responses.activate
def test_partial_compliance(client):
    rules_data = {
        "protected_branches": [
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
            {"name": "develop", "push_access_level": 30, "merge_access_level": 30,
             "allow_force_push": False, "code_owner_approval_required": False},
        ],
    }

    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=[
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
            {"name": "develop", "push_access_level": 20, "merge_access_level": 30,
             "allow_force_push": False, "code_owner_approval_required": False},
        ],
        status=200,
    )

    checker = ComplianceChecker(client, rules_data)
    report = checker.check_all()
    assert report.total == 2
    assert report.compliant_count == 1
    assert report.non_compliant_count == 1


@responses.activate
def test_report_properties(client):
    rules_data = {
        "protected_branches": [
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
        ],
    }

    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=[{"name": "main", "push_access_level": 40, "merge_access_level": 40,
               "allow_force_push": False, "code_owner_approval_required": True}],
        status=200,
    )

    checker = ComplianceChecker(client, rules_data)
    report = checker.check_all()
    assert report.total == 1
    assert report.compliant_count == 1
    assert report.non_compliant_count == 0
    assert report.all_compliant is True
    assert len(report.rules) == 1
    assert report.rules[0].compliant is True
    assert report.rules[0].rule_type == "protected_branch"
    assert report.rules[0].name == "main"


@responses.activate
def test_diff_details_in_report(client):
    rules_data = {
        "protected_branches": [
            {"name": "main", "push_access_level": 40, "merge_access_level": 40,
             "allow_force_push": False, "code_owner_approval_required": True},
        ],
    }

    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=[{"name": "main", "push_access_level": 30, "merge_access_level": 40,
               "allow_force_push": True, "code_owner_approval_required": True}],
        status=200,
    )

    checker = ComplianceChecker(client, rules_data)
    report = checker.check_all()
    assert report.non_compliant_count == 1
    assert len(report.rules[0].details) == 2
    assert any("push_access_level" in d for d in report.rules[0].details)
    assert any("allow_force_push" in d for d in report.rules[0].details)
