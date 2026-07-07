import pytest
import responses

from rules.approvals import ApprovalRule

RULE_URL = "approval_rules"


def _make_rule(client, overrides: dict | None = None) -> ApprovalRule:
    defaults = {
        "name": "main-approval",
        "approvals_required": 2,
        "rule_type": "regular",
        "branch_name": "main",
    }
    if overrides:
        defaults.update(overrides)
    return ApprovalRule(client, defaults)


def _existing_rule(**overrides) -> dict:
    defaults = {
        "id": 1,
        "name": "main-approval",
        "approvals_required": 2,
        "rule_type": "regular",
        "branch_name": "main",
    }
    defaults.update(overrides)
    return defaults


@responses.activate
def test_get_current_found(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule()],
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is not None
    assert result["name"] == "main-approval"
    assert result["id"] == 1


@responses.activate
def test_get_current_not_found(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[],
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is None


@responses.activate
def test_get_current_not_found_different_name(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(name="other-approval")],
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is None


@responses.activate
def test_matches_exact(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule()],
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is True


@responses.activate
def test_matches_differs_approvals_required(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(approvals_required=1)],
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_differs_rule_type(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(rule_type="any_approver")],
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_differs_branch_name(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(branch_name="develop")],
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_defaults(client):
    rule = _make_rule(client, {"approvals_required": 1})
    existing = _existing_rule(approvals_required=1, rule_type="regular", branch_name="main")
    assert rule._matches(existing) is True


@responses.activate
def test_matches_defaults_when_branch_none(client):
    rule = _make_rule(client, {"branch_name": None})
    existing = _existing_rule(branch_name=None)
    assert rule._matches(existing) is True


@responses.activate
def test_apply_skips_when_already_matching(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule()],
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result is not None
    assert result["name"] == "main-approval"


@responses.activate
def test_apply_creates_when_not_exists(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=_existing_rule(),
        status=201,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result is not None
    assert result["name"] == "main-approval"


@responses.activate
def test_apply_updates_when_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(approvals_required=1)],
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{RULE_URL}/1",
        json=_existing_rule(approvals_required=2),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["approvals_required"] == 2


@responses.activate
def test_apply_updates_when_rule_type_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(rule_type="any_approver")],
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{RULE_URL}/1",
        json=_existing_rule(rule_type="regular"),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["rule_type"] == "regular"


@responses.activate
def test_apply_updates_when_branch_name_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(branch_name="develop")],
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{RULE_URL}/1",
        json=_existing_rule(branch_name="main"),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["branch_name"] == "main"


@responses.activate
def test_apply_multiple_rules(client):
    rules_data = [
        {"name": "main-approval", "approvals_required": 2, "branch_name": "main"},
        {"name": "develop-approval", "approvals_required": 1, "branch_name": "develop"},
    ]

    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=_existing_rule(name="main-approval"),
        status=201,
    )

    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=_existing_rule(name="develop-approval"),
        status=201,
    )

    for rule_data in rules_data:
        rule = ApprovalRule(client, rule_data)
        result = rule.apply()
        assert result["name"] == rule_data["name"]


@responses.activate
def test_delete(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule()],
        status=200,
    )
    responses.delete(
        f"{client.base_url}/projects/123/{RULE_URL}/1",
        status=204,
    )
    rule = _make_rule(client)
    rule.delete()


@responses.activate
def test_delete_not_found(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[],
        status=200,
    )
    rule = _make_rule(client)
    rule.delete()


@responses.activate
def test_partial_rule_uses_defaults(client):
    partial_rule = {"name": "feature-approval", "branch_name": "feature/*"}
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=_existing_rule(name="feature-approval"),
        status=201,
    )
    rule = ApprovalRule(client, partial_rule)
    result = rule.apply()
    assert result["name"] == "feature-approval"


@responses.activate
def test_apply_updates_when_rule_exists_with_diff(client):
    responses.get(
        f"{client.base_url}/projects/123/{RULE_URL}",
        json=[_existing_rule(name="main-approval", approvals_required=1, rule_type="any_approver")],
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{RULE_URL}/1",
        json=_existing_rule(approvals_required=2, rule_type="regular"),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["approvals_required"] == 2
    assert result["rule_type"] == "regular"
