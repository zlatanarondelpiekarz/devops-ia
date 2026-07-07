import pytest
import responses

from rules.protected_branches import ProtectedBranchRule


BRANCH_NAME = "main"
BRANCH_URL = "protected_branches"
BRANCH_ITEM_URL = f"protected_branches/{BRANCH_NAME}"


def _make_rule(client, overrides: dict | None = None) -> ProtectedBranchRule:
    defaults = {
        "name": BRANCH_NAME,
        "push_access_level": 40,
        "merge_access_level": 40,
        "allow_force_push": False,
        "code_owner_approval_required": True,
    }
    if overrides:
        defaults.update(overrides)
    return ProtectedBranchRule(client, defaults)


def _existing_branch(**overrides) -> dict:
    defaults = {
        "name": BRANCH_NAME,
        "push_access_level": 40,
        "merge_access_level": 40,
        "allow_force_push": False,
        "code_owner_approval_required": True,
    }
    defaults.update(overrides)
    return defaults


@responses.activate
def test_get_current_found(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[_existing_branch()],
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is not None
    assert result["name"] == BRANCH_NAME


@responses.activate
def test_get_current_not_found(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[],
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is None


@responses.activate
def test_get_current_other_branch(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[_existing_branch(name="develop")],
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is None


@responses.activate
def test_matches_exact(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[_existing_branch()],
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is True


@responses.activate
def test_matches_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[_existing_branch(push_access_level=30)],
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_defaults(client):
    rule = _make_rule(client, {"push_access_level": 40})
    existing = _existing_branch(push_access_level=40, merge_access_level=40)
    assert rule._matches(existing) is True


@responses.activate
def test_apply_creates_when_not_exists(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=_existing_branch(),
        status=201,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result is not None
    assert result["name"] == BRANCH_NAME


@responses.activate
def test_apply_skips_when_already_matching(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[_existing_branch()],
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result is not None
    assert result["name"] == BRANCH_NAME


@responses.activate
def test_apply_updates_when_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[_existing_branch(push_access_level=30)],
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{BRANCH_ITEM_URL}",
        json=_existing_branch(push_access_level=40),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["push_access_level"] == 40


@responses.activate
def test_delete(client):
    responses.delete(
        f"{client.base_url}/projects/123/{BRANCH_ITEM_URL}",
        status=204,
    )
    rule = _make_rule(client)
    rule.delete()


@responses.activate
def test_apply_multiple_branches(client):
    rules_data = [
        {"name": "main", "push_access_level": 40, "merge_access_level": 40},
        {"name": "develop", "push_access_level": 30, "merge_access_level": 30},
    ]

    # First GET returns empty for both
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=_existing_branch(name="main"),
        status=201,
    )

    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=_existing_branch(name="develop"),
        status=201,
    )

    for rule_data in rules_data:
        rule = ProtectedBranchRule(client, rule_data)
        result = rule.apply()
        assert result["name"] == rule_data["name"]


@responses.activate
def test_partial_rule_uses_defaults(client):
    partial_rule = {"name": "feature/*"}
    responses.get(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=[],
        status=200,
    )
    responses.post(
        f"{client.base_url}/projects/123/{BRANCH_URL}",
        json=_existing_branch(name="feature/*"),
        status=201,
    )
    rule = ProtectedBranchRule(client, partial_rule)
    result = rule.apply()
    assert result["name"] == "feature/*"
