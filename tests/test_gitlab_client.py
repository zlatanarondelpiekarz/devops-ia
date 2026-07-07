import pytest
import responses

from app.gitlab_client import GitLabClient


@responses.activate
def test_health_check_success(client: GitLabClient):
    responses.get(
        f"{client.base_url}/version",
        json={"version": "16.0.0"},
        status=200,
    )
    assert client.health_check() is True


@responses.activate
def test_health_check_failure(client: GitLabClient):
    responses.get(f"{client.base_url}/version", status=500)
    assert client.health_check() is False


@responses.activate
def test_get_protected_branches(client: GitLabClient):
    expected = [{"name": "main", "push_access_level": 40}]
    responses.get(
        f"{client.base_url}/projects/123/protected_branches",
        json=expected,
        status=200,
    )
    result = client.get("protected_branches")
    assert result == expected


@responses.activate
def test_create_protected_branch(client: GitLabClient):
    payload = {"name": "main", "push_access_level": 40, "merge_access_level": 40}
    responses.post(
        f"{client.base_url}/projects/123/protected_branches",
        json=payload,
        status=201,
    )
    result = client.post("protected_branches", payload)
    assert result["name"] == "main"


@responses.activate
def test_delete_protected_branch(client: GitLabClient):
    responses.delete(
        f"{client.base_url}/projects/123/protected_branches/main",
        status=204,
    )
    client.delete("protected_branches/main")
    assert True


@responses.activate
def test_get_approval_rules(client: GitLabClient):
    expected = [{"name": "main-approval", "approvals_required": 2}]
    responses.get(
        f"{client.base_url}/projects/123/approval_rules",
        json=expected,
        status=200,
    )
    result = client.get("approval_rules")
    assert result == expected
