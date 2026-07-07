import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from app.config import Settings


def test_default_values():
    s = Settings(config_path="/tmp/nonexistent.yaml")
    assert s.gitlab_url == "https://gitlab.com"
    assert s.rules_path.endswith("/rules")


def test_from_yaml(tmp_path):
    cfg = tmp_path / "settings.yaml"
    cfg.write_text(
        yaml.dump(
            {
                "gitlab": {
                    "url": "https://gitlab.internal",
                    "token": "yaml-token",
                    "project_id": "99",
                }
            }
        )
    )
    s = Settings(config_path=str(cfg))
    assert s.gitlab_url == "https://gitlab.internal"
    assert s.gitlab_token == "yaml-token"
    assert s.gitlab_project_id == "99"


def test_token_env_override(tmp_path):
    cfg = tmp_path / "settings.yaml"
    cfg.write_text(
        yaml.dump(
            {
                "gitlab": {
                    "url": "https://gitlab.com",
                    "token": "yaml-token",
                    "project_id": "1",
                }
            }
        )
    )
    with patch.dict(os.environ, {"GITLAB_TOKEN": "env-token"}, clear=True):
        s = Settings(config_path=str(cfg))
        assert s.gitlab_token == "env-token"


def test_reload(tmp_path):
    cfg = tmp_path / "settings.yaml"
    cfg.write_text(yaml.dump({"gitlab": {"url": "https://v1.com", "project_id": "1"}}))
    s = Settings(config_path=str(cfg))
    assert s.gitlab_url == "https://v1.com"
    cfg.write_text(yaml.dump({"gitlab": {"url": "https://v2.com", "project_id": "1"}}))
    s.reload()
    assert s.gitlab_url == "https://v2.com"
