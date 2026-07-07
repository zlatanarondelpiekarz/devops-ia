import pytest
import responses

from rules.merge_requests import MergeRequestRule


PROJECT_URL = ""


def _make_rule(client, overrides: dict | None = None) -> MergeRequestRule:
    defaults = {
        "merge_method": "merge",
        "pipeline_required": True,
        "discussions_resolved": True,
        "remove_source_branch": True,
    }
    if overrides:
        defaults.update(overrides)
    return MergeRequestRule(client, defaults)


def _existing_project(**overrides) -> dict:
    defaults = {
        "id": 123,
        "merge_method": "merge",
        "only_allow_merge_if_pipeline_succeeds": True,
        "only_allow_merge_if_all_discussions_are_resolved": True,
        "remove_source_branch_after_merge": True,
    }
    defaults.update(overrides)
    return defaults


@responses.activate
def test_get_current_returns_project(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(),
        status=200,
    )
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is not None
    assert result["id"] == 123
    assert result["merge_method"] == "merge"


@responses.activate
def test_get_current_returns_none_on_exception(client):
    rule = _make_rule(client)
    result = rule._get_current()
    assert result is None


@responses.activate
def test_matches_exact(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(),
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is True


@responses.activate
def test_matches_differs_merge_method(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(merge_method="ff"),
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_differs_pipeline_required(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(only_allow_merge_if_pipeline_succeeds=False),
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_differs_discussions_resolved(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(only_allow_merge_if_all_discussions_are_resolved=False),
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_differs_remove_source_branch(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(remove_source_branch_after_merge=False),
        status=200,
    )
    rule = _make_rule(client)
    existing = rule._get_current()
    assert rule._matches(existing) is False


@responses.activate
def test_matches_defaults(client):
    rule = _make_rule(client, {"merge_method": "merge"})
    existing = _existing_project(
        merge_method="merge",
        only_allow_merge_if_pipeline_succeeds=True,
        only_allow_merge_if_all_discussions_are_resolved=True,
        remove_source_branch_after_merge=True,
    )
    assert rule._matches(existing) is True


@responses.activate
def test_apply_skips_when_already_matching(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result is not None
    assert result["merge_method"] == "merge"


@responses.activate
def test_apply_updates_when_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(merge_method="ff"),
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(merge_method="merge"),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["merge_method"] == "merge"


@responses.activate
def test_apply_partial_update(client):
    partial_rule = {"merge_method": "ff"}
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(merge_method="merge"),
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(merge_method="ff"),
        status=200,
    )
    rule = MergeRequestRule(client, partial_rule)
    result = rule.apply()
    assert result["merge_method"] == "ff"


@responses.activate
def test_apply_updates_when_pipeline_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(only_allow_merge_if_pipeline_succeeds=False),
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(only_allow_merge_if_pipeline_succeeds=True),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["only_allow_merge_if_pipeline_succeeds"] is True


@responses.activate
def test_apply_updates_when_discussions_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(only_allow_merge_if_all_discussions_are_resolved=False),
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(only_allow_merge_if_all_discussions_are_resolved=True),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["only_allow_merge_if_all_discussions_are_resolved"] is True


@responses.activate
def test_apply_updates_when_remove_source_branch_differs(client):
    responses.get(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(remove_source_branch_after_merge=False),
        status=200,
    )
    responses.put(
        f"{client.base_url}/projects/123/{PROJECT_URL}",
        json=_existing_project(remove_source_branch_after_merge=True),
        status=200,
    )
    rule = _make_rule(client)
    result = rule.apply()
    assert result["remove_source_branch_after_merge"] is True
