import os
from unittest.mock import patch

import pytest

from app.auth import GitLabAuth, _get_token


def test_get_token_from_env():
    with patch.dict(os.environ, {"GITLAB_TOKEN": "env-token"}, clear=True):
        assert _get_token() == "env-token"


def test_get_token_from_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GITLAB_TOKEN=dotenv-token\nOTHER=value\n")
    with patch.object(os, "getcwd", return_value=str(tmp_path)):
        assert _get_token() == "dotenv-token"


def test_get_token_missing():
    with patch.dict(os.environ, {}, clear=True), patch("os.getcwd", return_value="/tmp/nonexistent"):
        with pytest.raises(ValueError, match="GITLAB_TOKEN must be set"):
            _get_token()


def test_from_env(settings):
    with patch.dict(
        os.environ,
        {
            "GITLAB_URL": "https://gitlab.custom.com",
            "GITLAB_TOKEN": "custom-token",
            "GITLAB_PROJECT_ID": "42",
        },
        clear=True,
    ):
        auth = GitLabAuth.from_env()
        assert auth.url == "https://gitlab.custom.com"
        assert auth.token == "custom-token"
        assert auth.project_id == "42"


def test_from_env_missing_project_id():
    with patch.dict(
        os.environ, {"GITLAB_TOKEN": "t", "GITLAB_PROJECT_ID": ""}, clear=True
    ):
        with pytest.raises(ValueError, match="GITLAB_PROJECT_ID"):
            GitLabAuth.from_env()


def test_from_settings(settings):
    auth = GitLabAuth.from_settings(settings)
    assert auth.url == "https://gitlab.example.com"
    assert auth.token == "test-token"
    assert auth.project_id == "123"
