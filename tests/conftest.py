from collections.abc import Generator
from unittest.mock import patch

import pytest
import yaml

from app.auth import GitLabAuth
from app.config import Settings
from app.gitlab_client import GitLabClient


@pytest.fixture
def settings() -> Settings:
    s = Settings()
    s._data = {
        "gitlab": {
            "url": "https://gitlab.example.com",
            "token": "test-token",
            "project_id": "123",
        },
        "rules": {"path": "rules"},
    }
    return s


@pytest.fixture
def auth(settings: Settings) -> GitLabAuth:
    return GitLabAuth.from_settings(settings)


@pytest.fixture
def client(auth: GitLabAuth) -> GitLabClient:
    return GitLabClient(auth)


@pytest.fixture
def sample_rule_yaml() -> str:
    return yaml.dump(
        {
            "protected_branches": [
                {
                    "name": "main",
                    "push_access_level": 40,
                    "merge_access_level": 40,
                    "allow_force_push": False,
                    "code_owner_approval_required": True,
                },
                {
                    "name": "develop",
                    "push_access_level": 30,
                    "merge_access_level": 30,
                },
            ],
            "merge_requests": {
                "merge_method": "merge",
                "pipeline_required": True,
                "discussions_resolved": True,
                "remove_source_branch": True,
            },
            "approval_rules": [
                {
                    "name": "main-approval",
                    "approvals_required": 2,
                    "rule_type": "regular",
                    "branch_name": "main",
                }
            ],
        }
    )
